# 导入必要的库
import pandas as pd
import torch
from transformers import BertTokenizer, BertForSequenceClassification
from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF

# 加载预训练的中文BERT模型和分词器
model_name = 'bert-base-chinese'
tokenizer = BertTokenizer.from_pretrained(model_name, clean_up_tokenization_spaces=True)

model = BertForSequenceClassification.from_pretrained(model_name)

# 创建情感分析pipeline
sentiment_pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

# 读取Excel文件
df = pd.read_excel('comments.xlsx')  # 请替换为你的Excel文件名

# 进行情感分析
results = sentiment_pipeline(df['comments'].tolist())

# 将结果添加到DataFrame
df['Sentiment'] = [r['label'] for r in results]
df['Score'] = [r['score'] for r in results]

# 定义一个函数来提取主题
# def extract_topics(texts, n_topics=3):
#     vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
#     tfidf = vectorizer.fit_transform(texts)
#     nmf = NMF(n_components=n_topics, random_state=42)
#     nmf.fit(tfidf)
#     feature_names = vectorizer.get_feature_names_out()  # 修改这里
#     topics = []
#     for topic_idx, topic in enumerate(nmf.components_):
#         top_words = [feature_names[i] for i in topic.argsort()[:-10 - 1:-1]]
#         topics.append(", ".join(top_words))
#     return topics


import jieba


def extract_topics(texts, n_topics=3):
    # 使用jieba进行中文分词
    texts = [' '.join(jieba.cut(text)) for text in texts]

    vectorizer = TfidfVectorizer(max_features=1000)
    tfidf = vectorizer.fit_transform(texts)
    nmf = NMF(n_components=n_topics, random_state=42)
    nmf.fit(tfidf)
    feature_names = vectorizer.get_feature_names_out()
    topics = []
    for topic_idx, topic in enumerate(nmf.components_):
        top_words = [feature_names[i] for i in topic.argsort()[:-10 - 1:-1]]
        topics.append(", ".join(top_words))
    return topics

# 分类并提取主题
positive_comments = df[df['Sentiment'] == 'LABEL_1']['comments']
neutral_comments = df[(df['Score'] > 0.4) & (df['Score'] < 0.6)]['comments']
negative_comments = df[df['Sentiment'] == 'LABEL_0']['comments']

print(positive_comments)
positive_topics = extract_topics(positive_comments)
neutral_topics = extract_topics(neutral_comments)
negative_topics = extract_topics(negative_comments)

# 打印结果
print("积极评论主题：")
for i, topic in enumerate(positive_topics):
    print(f"主题 {i+1}: {topic}")

print("\n中性评论主题：")
for i, topic in enumerate(neutral_topics):
    print(f"主题 {i+1}: {topic}")

print("\n消极评论主题：")
for i, topic in enumerate(negative_topics):
    print(f"主题 {i+1}: {topic}")

# 计算各类评论的数量和比例
total = len(df)
positive_count = len(positive_comments)
neutral_count = len(neutral_comments)
negative_count = len(negative_comments)

print(f"\n总评论数: {total}")
print(f"积极评论: {positive_count} ({positive_count/total*100:.2f}%)")
print(f"中性评论: {neutral_count} ({neutral_count/total*100:.2f}%)")
print(f"消极评论: {negative_count} ({negative_count/total*100:.2f}%)")

# 输出一些示例评论
print("\n积极评论示例:")
print(positive_comments.head().tolist())

print("\n中性评论示例:")
print(neutral_comments.head().tolist())

print("\n消极评论示例:")
print(negative_comments.head().tolist())