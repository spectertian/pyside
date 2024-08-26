import pandas as pd
from transformers import pipeline
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import numpy as np

# 下载必要的NLTK数据
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt_tab')
# 加载情感分析模型
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

# 读取Excel文件
df = pd.read_excel('comments.xlsx')  # 替换为你的Excel文件名

# 假设评论在名为'comments'的列中
comments = df['comments'].tolist()

# 进行情感分析
sentiments = sentiment_analyzer(comments)

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
    # 将所有评论合并成一个字符串
    text = ' \n'.join(text_list)

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

    # 获取前N个句子作为摘要
    summary_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:num_sentences]
    summary = ' '.join(summary_sentences)

    return summary


# 生成摘要
positive_summary = summarize_text(positive_comments)
neutral_summary = summarize_text(neutral_comments)
negative_summary = summarize_text(negative_comments)

print("Positive Comments Summary:")
print(positive_summary)
print("\nNeutral Comments Summary:")
print(neutral_summary)
print("\nNegative Comments Summary:")
print(negative_summary)

# 输出每种情感的评论数量
print(f"\nNumber of Positive Comments: {len(positive_comments)}")
print(f"Number of Neutral Comments: {len(neutral_comments)}")
print(f"Number of Negative Comments: {len(negative_comments)}")