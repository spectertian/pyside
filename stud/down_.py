from transformers import AutoTokenizer, AutoModelForSequenceClassification

# 设置模型名称和本地保存路径
model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
local_model_path = "./local_model"

# 下载并保存模型
print("Downloading model...")
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# 保存模型到本地
tokenizer.save_pretrained(local_model_path)
model.save_pretrained(local_model_path)
print("Model downloaded and saved locally.")