import os
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from tqdm import tqdm

# 设置模型名称和本地保存路径
model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
local_model_path = "./local_model"

# 检查本地是否已有模型，如果没有则下载
if not os.path.exists(local_model_path):
    print("Downloading model...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)

    # 保存模型到本地
    tokenizer.save_pretrained(local_model_path)
    model.save_pretrained(local_model_path)
    print("Model downloaded and saved locally.")
else:
    print("Loading model from local storage...")

# 从本地加载模型
sentiment_analyzer = pipeline("sentiment-analysis", model=local_model_path, tokenizer=local_model_path)

# 读取Excel文件
df = pd.read_excel("用户调查结果列表.xlsx")

# 假设留言列名为'comment'
comments = df['用户反馈'].tolist()

results = []

# 对每条留言进行情感分析
for comment in tqdm(comments):
    # 确保comment是字符串类型，并处理NaN值
    if pd.isna(comment):
        comment = ""
    else:
        comment = str(comment)

    if comment.strip():  # 如果评论不是空字符串
        try:
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
        except Exception as e:
            print(f"Error processing comment: {comment}")
            print(f"Error message: {str(e)}")
            category = 'Error'
            score = 0
    else:
        category = 'Empty'
        score = 0

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
print(results_df[results_df['sentiment'] == 'Positive']['comment'].sample(
    min(3, len(results_df[results_df['sentiment'] == 'Positive']))).tolist())
print("\nNeutral comments sample:")
print(results_df[results_df['sentiment'] == 'Neutral']['comment'].sample(
    min(3, len(results_df[results_df['sentiment'] == 'Neutral']))).tolist())
print("\nNegative comments sample:")
print(results_df[results_df['sentiment'] == 'Negative']['comment'].sample(
    min(3, len(results_df[results_df['sentiment'] == 'Negative']))).tolist())

# 保存结果到新的Excel文件
results_df.to_excel("sentiment_analysis_results.xlsx", index=False)