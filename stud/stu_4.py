import pandas as pd
from transformers import pipeline
from tqdm import tqdm

# 加载BERT情感分析模型
sentiment_analyzer = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")

# 读取Excel文件
df = pd.read_excel("your_excel_file.xlsx")

# 假设留言列名为'comment'
comments = df['comment'].tolist()

results = []

# 对每条留言进行情感分析
for comment in tqdm(comments):
    result = sentiment_analyzer(comment)[0]
    sentiment = result['label']
    score = result['score']

    # 根据分数确定情感类别
    if sentiment in ['1 star', '2 stars']:
        category = 'Negative'
    elif sentiment in ['3 stars']:
        category = 'Neutral'
    else:
        category = 'Positive'

    results.append({
        'comment': comment,
        'sentiment': category,
        'score': score
    })

# 创建结果DataFrame
results_df = pd.DataFrame(results)

# 输出结果摘要
print(results_df['sentiment'].value_counts())
print("\nPositive comments sample:")
print(results_df[results_df['sentiment'] == 'Positive']['comment'].sample(3).tolist())
print("\nNeutral comments sample:")
print(results_df[results_df['sentiment'] == 'Neutral']['comment'].sample(3).tolist())
print("\nNegative comments sample:")
print(results_df[results_df['sentiment'] == 'Negative']['comment'].sample(3).tolist())

# 保存结果到新的Excel文件
results_df.to_excel("sentiment_analysis_results.xlsx", index=False)