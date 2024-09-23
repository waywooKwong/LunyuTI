"""
22/09/2024 weihua
这是一个 json 提取的 .py
简单演示如何从 json 读取目标的条目
"""

import json

json_path = "log\QianCheng\问答.json"
with open(json_path,'r',encoding='utf-8') as f:
    data = json.load(f)
    
questions = [item['question'] for item in data]

for question in questions:
    print(question)