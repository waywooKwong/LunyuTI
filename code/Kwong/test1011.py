import re

# 原始字符串
data = """{
        "answer": "这是:"answer"",
        "answer_translation": "这是:"translation""
}"""

### 加入 answer_translation 的字符处理
# 删除 {""}
data = re.sub(r'[{}"“” ]+', "", data)  # 删除 '{' 和 '"' 符号
print("cleaned_data:", data)

# 提取 answer: 后面到 answer_translation: 之间的内容
start_index = data.find('answer:') + len('answer:')
end_index = data.find('answer_translation:')
answer_part = data[start_index:end_index].strip()  # 去掉前后空格

# 提取 answer_translation: 后的内容
start_index_translation = data.find('answer_translation:') + len('answer_translation:')
translation_part = data[start_index_translation:].strip()  # 去掉前后空格

print("Answer Part:", answer_part)
print("Translation Part:", translation_part)

