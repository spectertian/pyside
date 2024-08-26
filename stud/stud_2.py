import sys

import pandas as pd
from transformers import pipeline
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import numpy as np

# import warnings
# warnings.filterwarnings("ignore", category=FutureWarning, message="clean_up_tokenization_spaces")
# 下载必要的NLTK数据
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt_tab')

# 加载情感分析模型
# sentiment_analyzer = pipeline("sentiment-analysis",model="distilbert-base-uncased-finetuned-sst-2-english")
sentiment_analyzer = pipeline("sentiment-analysis", model="bert-base-uncased")

# 读取Excel文件
df = pd.read_excel('用户调查结果列表.xlsx')  # 替换为你的Excel文件名

# print(df)
# sys.exit()
# 假设评论在名为'comments'的列中
comments = df['用户反馈'].tolist()
# print(comments)
# sys.exit()
# 清理和检查评论数据
cleaned_comments = []
for comment in comments:
    if isinstance(comment, str):
        cleaned_comments.append(comment)
    elif pd.isna(comment):
        continue  # 跳过NaN值
    else:
        cleaned_comments.append(str(comment))  # 尝试将非字符串转换为字符串

print(f"原始评论数量: {len(comments)}")
print(f"清理后的评论数量: {len(cleaned_comments)}")

try:
    # 进行情感分析
    sentiments = sentiment_analyzer(cleaned_comments)
except Exception as e:
    print(f"情感分析过程中出现错误: {e}")
    print("请检查输入数据，确保所有评论都是有效的文本字符串。")
    sys.exit(1)

# 将评论分类
positive_comments = []
neutral_comments = []
negative_comments = []

for comment, sentiment in zip(comments, sentiments):
    if sentiment['label'] == 'POSITIVE' and sentiment['score'] > 0.6:
        positive_comments.append(comment)
    elif sentiment['label'] == 'NEGATIVE' and sentiment['score'] > 0.6:
        negative_comments.append(comment)
    else:
        neutral_comments.append(comment)


def summarize_text(text_list, num_sentences=3):
    if not text_list:
        return "No comments to summarize."

    # 确保所有元素都是字符串
    text_list = [str(item) if not isinstance(item, str) else item for item in text_list]

    # 将所有评论合并成一个字符串
    text = ' '.join(text_list)

    # 分割成句子
    sentences = sent_tokenize(text)

    # 去除停用词
    stop_words = set(stopwords.words('english'))

    # 计算词频
    word_frequencies = {}
    for sentence in sentences:
        words = word_tokenize(sentence)
        for word in words:
            if word.lower() not in stop_words:
                if word not in word_frequencies:
                    word_frequencies[word] = 1
                else:
                    word_frequencies[word] += 1

    # 如果word_frequencies为空，返回一个提示信息
    if not word_frequencies:
        return "All words in the comments are stop words or the comments are empty."

    # 计算最大频率
    max_frequency = max(word_frequencies.values())

    # 计算每个词的权重
    for word in word_frequencies:
        word_frequencies[word] = word_frequencies[word] / max_frequency

    # 计算句子得分
    sentence_scores = {}
    for sentence in sentences:
        for word in word_tokenize(sentence.lower()):
            if word in word_frequencies:
                if len(sentence.split(' ')) < 30:  # 忽略过长的句子
                    if sentence not in sentence_scores:
                        sentence_scores[sentence] = word_frequencies[word]
                    else:
                        sentence_scores[sentence] += word_frequencies[word]

    # 如果没有有效的句子得分，返回一个提示信息
    if not sentence_scores:
        return "No valid sentences found for summarization."

    # 获取前N个句子作为摘要
    summary_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:num_sentences]
    summary = ' '.join(summary_sentences)

    return summary


def clean_comments(comments):
    return [str(comment) for comment in comments if comment is not None and comment == comment]  # 最后的条件用于排除 NaN


# 生成摘要
positive_comments = clean_comments(positive_comments)
neutral_comments = clean_comments(neutral_comments)
negative_comments = clean_comments(negative_comments)

positive_summary = summarize_text(positive_comments)
neutral_summary = summarize_text(neutral_comments)
negative_summary = summarize_text(negative_comments)

print("Positive Comments Summary:")
print(positive_summary)
print("\nNeutral Comments Summary:")
print(neutral_summary)
print("\nNegative Comments Summary:")
print(negative_summary)


def print_comment_info(comments, name):
    print(f"\n{name} 评论信息:")
    print(f"评论数量: {len(comments)}")
    print(f"非字符串类型的评论:")
    for i, comment in enumerate(comments):
        if not isinstance(comment, str):
            print(f"  索引 {i}: 类型 {type(comment)}, 值 {comment}")
        else:
            print(comment)


print_comment_info(positive_comments, "正面")
print_comment_info(neutral_comments, "中性")
print_comment_info(negative_comments, "负面")

# 输出每种情感的评论数量
print(f"\nNumber of Positive Comments: {len(positive_comments)}")
print(f"Number of Neutral Comments: {len(neutral_comments)}")
print(f"Number of Negative Comments: {len(negative_comments)}")
# pip install pandas transformers nltk openpyxl
