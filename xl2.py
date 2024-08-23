from transformers import BertTokenizer, BertForSequenceClassification
import os

model_name = 'bert-base-uncased'
output_dir = './bert_model'

# 确保输出目录存在
os.makedirs(output_dir, exist_ok=True)

# 下载 tokenizer
tokenizer = BertTokenizer.from_pretrained(model_name)
tokenizer.save_pretrained(output_dir)

# 下载模型
model = BertForSequenceClassification.from_pretrained(model_name)
model.save_pretrained(output_dir)

print(f"模型和 tokenizer 已保存到 {output_dir}")