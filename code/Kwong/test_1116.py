import json

json_path = "code\Kwong\pic2_idiom_match.json"
with open(json_path, "r", encoding="utf-8") as file:
    json_data = json.load(file)

pic2_topic = "道德修养"
pic2_idiom = "学而时习之，不亦乐乎"  # （默认句） 根据 pic2_topic2 从找到对应要重写的原句（待实现）

for index, item in enumerate(json_data):
    part_reserve = item["part_reserve"]
    pic2_idiom = item["part_rewrite"]
    print("index:",index, item["class"])
    print("part_reserve :",part_reserve )
    print("pic2_idiom :",pic2_idiom)

print("pic2_idiom :", pic2_idiom)
