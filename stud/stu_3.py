import sys
import pandas as pd
from transformers import pipeline
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import torch
import warnings

# 忽略特定的警告
warnings.filterwarnings("ignore", category=FutureWarning, message="clean_up_tokenization_spaces")

# 下载必要的NLTK数据
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

# 检查是否有可用的GPU
device = 0 if torch.cuda.is_available() else -1

# 加载多语言情感分析模型
sentiment_analyzer = pipeline("sentiment-analysis",
                              model="nlptown/bert-base-multilingual-uncased-sentiment",
                              device=device)

# 读取Excel文件
try:
    df = pd.read_excel('用户调查结果列表.xlsx')
except FileNotFoundError:
    print("无法找到指定的Excel文件。请确保文件路径正确。")
    sys.exit(1)


# 清理评论数据
def clean_comments(comments):
    cleaned = []
    for comment in comments:
        if isinstance(comment, str):
            cleaned.append(comment)
        elif pd.isna(comment):
            continue
        else:
            cleaned.append(str(comment))
    return cleaned


cleaned_comments = clean_comments(df['用户反馈'].tolist())

print(f"原始评论数量: {len(df['用户反馈'])}")
print(f"清理后的评论数量: {len(cleaned_comments)}")

# 进行情感分析
batch_size = 32
sentiments = []
for i in range(0, len(cleaned_comments), batch_size):
    batch = cleaned_comments[i:i + batch_size]
    try:
        results = sentiment_analyzer(batch)
        sentiments.extend(results)
    except Exception as e:
        print(f"处理批次 {i} 到 {i + batch_size} 时出错: {e}")
        continue

# 将评论分类
positive_comments = []
neutral_comments = []
negative_comments = []

for comment, result in zip(cleaned_comments, sentiments):
    score = int(result['label'].split()[0])
    if score >= 4:
        positive_comments.append(comment)
    elif score <= 2:
        negative_comments.append(comment)
    else:
        neutral_comments.append(comment)


def summarize_text(text_list, num_sentences=3):
    text = ' '.join(text_list)
    sentences = sent_tokenize(text)
    stop_words = set(stopwords.words('english') + stopwords.words('chinese'))

    word_frequencies = {}
    for sentence in sentences:
        words = word_tokenize(sentence)
        for word in words:
            if word.lower() not in stop_words:
                if word not in word_frequencies:
                    word_frequencies[word] = 1
                else:
                    word_frequencies[word] += 1

    max_frequency = max(word_frequencies.values()) if word_frequencies else 1
    for word in word_frequencies:
        word_frequencies[word] = word_frequencies[word] / max_frequency

    sentence_scores = {}
    for sentence in sentences:
        for word in word_tokenize(sentence.lower()):
            if word in word_frequencies:
                if len(sentence.split(' ')) < 30:
                    if sentence not in sentence_scores:
                        sentence_scores[sentence] = word_frequencies[word]
                    else:
                        sentence_scores[sentence] += word_frequencies[word]

    summary_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:num_sentences]
    summary = ' '.join(summary_sentences)
    return summary


# 生成摘要
positive_summary = summarize_text(positive_comments)
neutral_summary = summarize_text(neutral_comments)
negative_summary = summarize_text(negative_comments)

print("\n积极评论摘要:")
print(positive_summary)
print("\n中性评论摘要:")
print(neutral_summary)
print("\n消极评论摘要:")
print(negative_summary)

print(f"\n积极评论数量: {len(positive_comments)}")
print(f"中性评论数量: {len(neutral_comments)}")
print(f"消极评论数量: {len(negative_comments)}")

# 保存结果到Excel文件
result_df = pd.DataFrame({
    '积极评论': positive_comments,
    '中性评论': neutral_comments,
    '消极评论': negative_comments
})

try:
    result_df.to_excel('情感分析结果.xlsx', index=False)
    print("\n结果已保存到 '情感分析结果.xlsx'")
except Exception as e:
    print(f"保存结果时出错: {e}")