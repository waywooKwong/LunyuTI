# -*- coding: utf-8 -*-
from transformers import pipeline
import os

# 这里是从 Huggingface 调用模型，所以需要翻墙，设置代理
# 记得挂上梯子，具体的端口号看自己机场的配置，我的是 7890
# 也可以把模型下到本地，这样就不用每次加载了
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

# 加载文本摘要模型
summarizer = pipeline("summarization",  device="cuda")




# 输入句子
text = """
樊迟问什么是仁，孔子说：“处事要恭敬，做事要敬重他人，与人交往要忠诚。即使是异国他乡的人，也不能抛弃这些品德。

"""

# 生成主题摘要
summary = summarizer(text, max_length=20, min_length=5, do_sample=False)

print(summary[0]['summary_text'])