"""
weihua 13/10/2024

目前我本机的redis数据库已经构建完成,
现在需要进行数据库的数据迁移构造到大家的电脑上,
思路为:
1. 将redis db5 中的 hash 类型数据导出为 JSON 文件
2. 加载这个 JSON 到本机的数据库

本代码是生成 JSON 文件，为 redis_db5_hash.json
注意:json 已经生成完毕,该代码不需再次运行
"""

import redis
import json

# 连接到 Redis 的 db5
r = redis.Redis(host="localhost", port=6379, db=5)

# 获取所有键
keys = r.keys()

# 存储所有键值数据的字典
data = {}

for key in keys:
    # 检查键是否为 hash 类型
    if r.type(key) == b"hash":
        # 获取该 hash 的所有字段和值
        hash_data = r.hgetall(key)
        # 将字节数据转换为字符串并存入字典
        data[key.decode("utf-8")] = {
            field.decode("utf-8"): value.decode("utf-8")
            for field, value in hash_data.items()
        }

# 将字典导出为 JSON 格式
with open(
    "code\\redis_data_load\\redis_db5_hash.json", "w", encoding="utf-8"
) as json_file:
    json.dump(data, json_file, ensure_ascii=False, indent=4)

print("Hash 类型数据已成功导出到 redis_db5_hash.json 文件中。")
