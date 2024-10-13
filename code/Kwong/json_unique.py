# import json

# # 从 test.json 文件加载 JSON 数据
# with open('data\QA_with_topic.json', 'r', encoding='utf-8') as f:
#     data = json.load(f)

# # 创建一个用于存储去重后的条目的列表
# unique_entries = []
# seen_entries = set()

# # 遍历每个条目
# for entry in data:
#     # 将每个字典条目转换为元组，元组是可哈希的，可以放入集合中
#     entry_tuple = tuple(sorted(entry.items()))
    
#     if entry_tuple not in seen_entries:
#         seen_entries.add(entry_tuple)
#         unique_entries.append(entry)

# # 将去重后的结果保存到 result.json 文件
# with open('data\QA_with_topic_unique.json', 'w', encoding='utf-8') as f:
#     json.dump(unique_entries, f, ensure_ascii=False, indent=4)

# print("去重完成，结果已保存到 result.json")

import json

# 从 test.json 文件中加载 JSON 数据
with open('data\\topic.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 去重每个条目中 "contents" 列表的子条目
for entry in data:
    seen_names = set()  # 用于跟踪已出现的 name
    unique_contents = []
    
    for content in entry["contents"]:
        name = content["name"]
        if name not in seen_names:
            unique_contents.append(content)  # 只保留第一次出现的条目
            seen_names.add(name)
    
    entry["contents"] = unique_contents  # 更新去重后的内容

# 将处理后的数据保存到 result.json 文件中
with open('data\\topic_name_unique.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("JSON 数据已处理并保存到 result.json")

