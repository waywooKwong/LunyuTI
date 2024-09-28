from transformers import AutoTokenizer, AutoModel
import torch
from sklearn.cluster import KMeans
import numpy as np
import json

# 设置输入路径和输出路径
json_path = "code\WangPu\句子主题归类结果02.json"  # 使用原始字符串
output_path = "code\WangPu\句子主题归类结果.json"

# 加载中文BERT分词器和模型
tokenizer = AutoTokenizer.from_pretrained("bert-base-chinese")
model = AutoModel.from_pretrained("bert-base-chinese")

# 读取 JSON 数据
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 提取主题、对话和名称
themes = []
dialogues = []
names = []
translations=[]

for entry in data:
    themes.append(entry["theme"])
    dialogues.append(entry["dialog"])
    names.append(entry["name"])
    translations.append(entry["translation"])

# 获取主题的嵌入
embeddings = []
for theme in themes:
    inputs = tokenizer(theme, return_tensors='pt', max_length=512, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
        embeddings.append(outputs.last_hidden_state[:, 0, :].numpy())

# 转换为 numpy 数组
embeddings = np.vstack(embeddings)

# 使用 K-Means 进行聚类
num_clusters = 20  # 根据需要设置聚类数量
kmeans = KMeans(n_clusters=num_clusters)
kmeans.fit(embeddings)

# 按照主题将对话归类
clustered_data = {i: [] for i in range(num_clusters)}  # 创建主题字典

# 将对话根据主题分组
for theme, dialog, name,translation, label in zip(themes, dialogues, names,translations, kmeans.labels_):
    clustered_data[label].append({
        "theme": theme,
        "dialog": dialog,
        "translation":translation,
        "name": name
    })

# 将结果保存到文件中
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(clustered_data, f, ensure_ascii=False, indent=4)

print(f"句子主题归类结果已保存到 {output_path}")
