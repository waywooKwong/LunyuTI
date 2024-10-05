import os
os.environ["SERPER_API_KEY"] = "972ce275dafcf94a944d6aa41459ed7d5581d538"

import json
import pprint
from langchain_community.utilities import GoogleSerperAPIWrapper

# 初始化 GoogleSerper 搜索工具
search = GoogleSerperAPIWrapper(type="news")

# 执行搜索，获取结果
results = search.results("国内外热门新闻,只在国内新闻网上找")

# 打印结果
pprint.pp(results)

# 将结果保存为 JSON 文件
output_file = "Lunyu/search_results.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=4)

print(f"搜索结果已保存到文件: {output_file}")