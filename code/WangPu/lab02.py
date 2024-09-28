import json

# 设置输入路径和输出路径
input_json_path = "code\WangPu\句子主题归类结果02.json"  # 原始 JSON 文件路径
output_json_path = "code\WangPu\全部对话.json"  # 输出 JSON 文件路径

# 读取原始 JSON 数据
with open(input_json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 提取所有 dialog
dialogs = [entry["dialog"] for entry in data]

# 保存到新的 JSON 文件
with open(output_json_path, 'w', encoding='utf-8') as f:
    json.dump(dialogs, f, ensure_ascii=False, indent=4)

print(f"所有 dialog 已保存到 {output_json_path}")
