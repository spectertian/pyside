# 导入必要的库
import torch
from transformers import BertTokenizer, BertForSequenceClassification
from transformers import pipeline
import pandas as pd
import matplotlib.pyplot as plt

# 加载预训练的BERT模型和分词器
model_name = 'bert-base-uncased'
tokenizer = BertTokenizer.from_pretrained(model_name, clean_up_tokenization_spaces=True)
model = BertForSequenceClassification.from_pretrained(model_name)

# 创建情感分析pipeline
sentiment_pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

# 示例用户反馈
feedback = [
    "The product is amazing! I love it.",
    "Terrible customer service, very disappointed.",
    "Great value for money, highly recommend.",
    "The quality is poor, wouldn't buy again.",
    "Neutral experience, nothing special."
]

# 进行情感分析
results = sentiment_pipeline(feedback)

# 创建DataFrame来存储结果
df = pd.DataFrame({
    'Feedback': feedback,
    'Sentiment': [r['label'] for r in results],
    'Score': [r['score'] for r in results]
})

# 打印结果
print(df)

# 可视化情感分布
sentiment_counts = df['Sentiment'].value_counts()
plt.figure(figsize=(10, 6))
sentiment_counts.plot(kind='bar')
plt.title('Sentiment Distribution')
plt.xlabel('Sentiment')
plt.ylabel('Count')
plt.show()

# 分析积极反馈
positive_feedback = df[df['Sentiment'] == 'POSITIVE']
print("\nPositive Feedback Summary:")
print(positive_feedback['Feedback'].tolist())

# 分析消极反馈
negative_feedback = df[df['Sentiment'] == 'NEGATIVE']
print("\nNegative Feedback Summary:")
print(negative_feedback['Feedback'].tolist())

# 计算平均情感得分
average_score = df['Score'].mean()
print(f"\nAverage Sentiment Score: {average_score:.2f}")
