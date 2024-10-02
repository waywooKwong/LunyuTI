import json
# 基于 topic 的对话划分
json_path = "data\\topic.json"
with open(json_path,'r',encoding='utf-8') as file:
    topic_based_data = json.load(file)
    
for item in topic_based_data:
    print("topic:",item["class"])
    contents = item["contents"]
    for content in contents:
        print("dialog:",content["dialog"])
        print("role:",content["name"])