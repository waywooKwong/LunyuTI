import requests
import json

# API URL
url = "https://tenapi.cn/v2/baiduhot"

# 发起 GET 请求
response = requests.get(url)

# 检查请求是否成功
if response.status_code == 200:
    # 获取返回的 JSON 数据
    data = response.json()
    
    # 打印返回的数据（可选）
    print(data)

    # 将数据保存为 JSON 文件
    with open('Lunyu/baidu_hot.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print("数据已保存为 baidu_hot.json")
else:
    print(f"请求失败，状态码: {response.status_code}")
