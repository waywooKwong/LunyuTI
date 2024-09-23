"""
22/9/2024
论语角色prompt生成器
"""
import os
os.environ["ZHIPUAI_API_KEY"] = "0e863acacdc09cad69cd7865fc3e0a28.mhYC6Yl7joh1dCZ5"
    # 20240731 20:55 weihua
    # new key: "6ac43a47c3fed6a70433a55108033202.OMB8LBLcgcz60x3q"
    # old key: "43c5d0cda6ab08302d6db046469d7c6b.eCF9cwVy1tadDU1q"
    # qiancheng: "72fea15b5fce38e0a81b2bb01e4903dd.wkhUuC4oAO5otOmY"
from langchain_community.chat_models import ChatZhipuAI

zhipuai_chat_model = ChatZhipuAI(model="glm-4")
# -*- coding: utf-8 -*-
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from typing import AsyncIterable, List
import json

model_name = "qwen2.5"  # 这里的 Lunyu 模型是 Ollama 基于 Qwen2.5 生成的

# chat_model = ChatOllama(model=model_name)
chat_model =zhipuai_chat_model

# print(chat_model.invoke("你好"))
class PromptGenerator:
    def __init__(self):
        self.chat_model = chat_model
        self.prompt_template_str = ("""
    您是一位专业的提示词模板生成器。\n
    您的任务是根据给定角色生成栩栩如生的 prompt 模板，帮助智能体刻画该角色的性格、行为和思想。\n
    该角色的名字为：{name}。\n
    在论语中的典型对话包括：{dialogue_in_lunyu}。\n
    该角色的历史故事为：{historical_story}。\n
    后世学者对该角色的评论为：{scholarly_comments}。\n

    您需要分析这些对话、故事和评论，生成详细的、高质量 prompt，使得智能体能够根据该角色的背景信息完成对角色的深入刻画。\n

    ### Prompt 格式要求\n
    - Prompt 用于生成历史人物的形象，角色包括孔子、曾子、子贡等。\n
    - 生成的 prompt 应涵盖至少 5 处角色细节。\n
    - 根据论语中的对话、历史故事、学术评论，生成符合角色身份的 prompt 内容。\n
    - 输出的 prompt 必须以该角色的名字 {name} 开头，并包含对话风格、价值观、哲学思想等要素。\n
    - 生成的 prompt 必须为字符串类型，并按需换行。\n
    - 最终生成的 prompt 必须为中文，且所有引用的对话必须使用文言文风格，不得出现白话文。\n

    ### Prompt 生成步骤\n
    1. **角色对话风格**：\n
       提炼该角色在论语中的对话片段，分析其典型的表达方式和用词习惯。确保符合其历史时期的语言风格。\n
       例如，孔子的对话简洁、深刻，常以简练的语句表达复杂的思想。\n

    2. **价值观**：\n
       通过角色在对话中的表现及历史故事，提炼出角色的核心价值观。\n
       例如，曾子的核心价值观可以是“自省”、“仁义”，且需结合实际历史背景。\n

    3. **教学风格（如果适用）**：\n
       如果该角色是教师，分析其在教学中的表现，提炼出典型的教学方法。结合对话中的教学实例来反映他的教学理念。\n
       例如，孔子重视启发式教学，经常通过问答形式引导学生思考。\n

    4. **哲学思想**：\n
       提炼论语中该角色的核心信念，通过典型对话和历史事件总结出其哲学思想。\n
       例如，孔子提倡“仁”，并通过一系列对话和行为展示对“仁”的解读。\n

    5. **外貌与形象（如果有历史记载）**：\n
       描述该角色的外貌特征和形象，若无明确记载，可以根据历史背景进行合理的推测。\n
       例如，孔子可能身着传统儒家服饰，面容庄重，给人以威严和智慧的印象。\n

    6. **典型对话引用**：\n
       至少提供三段该角色在论语中的经典对话，并确保引用符合文言文风格，展示该角色在不同情境下的行为和思想。\n
       例如，孔子与弟子的对话：“子曰：‘学而不思则罔，思而不学则殆。’”\n

    7. **互动方式**：\n
       详细分析该角色如何处理问题、回应道德困境，以及他与学生或同僚之间的互动方式。\n
       例如，孔子如何通过引导式提问，启发学生在道德问题上的思考。\n

    8. **角色目标**：\n
       - 短期目标：根据历史故事，推测出角色的短期目标。\n
       - 长期目标：结合角色的历史背景和哲学思想，推断其长期理想或追求。\n
       例如，孔子的长期目标是推行“仁政”，使社会回归正义和礼仪。\n

    ### 输出示例\n
    - {name}\n
    - 对话风格: 文言文风格，简洁而富有哲理。\n
    - 价值观: 注重仁义、自省和社会正义。\n
    - 教学风格: 启发式教学，善于通过提问引导学生思考。\n
    - 哲学思想: 仁、义、礼、智、信。\n
    - 典型对话: 子曰：“学而时习之，不亦说乎？”\n

    请确保输出的内容符合历史背景，生成准确的 prompt。\n
    注意！！！你只需要按照以上步骤分析，最后给出一份完整的角色模板介绍，不需要展示过程
    """
)


    def generate_prompt(self, name: str, dialogue_in_lunyu: List[str], historical_story: str, scholarly_comments: str):
        # 将对话数组转换为多行字符串，确保格式正确
        dialogue_in_lunyu_str = "\n".join(dialogue_in_lunyu)
        
        # 使用输入替换 JSON 中的模板标记
        prompt_str_input = self.prompt_template_str.format(name=name, dialogue_in_lunyu=dialogue_in_lunyu_str,historical_story=historical_story,scholarly_comments=scholarly_comments)


        # 添加强制要求输出为中文，并保持文言文风格


        # 发送给模型进行处理
        result=self.chat_model.invoke(prompt_str_input)
        print(result.content)

# agent = PromptGenerator()

# @app.get("/stream")
# async def stream_response():
#     return StreamingResponse(agent.generate_prompt(
#         name="孔子",
#         dialogue_in_lunyu=[
#             "三人行，必有我师焉。",
#             "学而时习之，不亦说乎？",
#             "吾日三省吾身。"
#         ],
#         historical_story="孔子周游列国传道，教导弟子。",
#         scholarly_comments="孔子被誉为古代中国最伟大的思想家和教育家。"
#     ), media_type='text/plain')

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
import json

json_path = "D:\WorkSpace\VScodeProject\LunYuDemo\log\WangPu\论语全角色对话.json"  # 使用原始字符串
# json_path = "log\\WangPu\\论语全角色对话.json"  # 或使用双反斜杠

with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

name_to_extract = "子张"
dialog=[]
for entry in data:
    if entry["name"] == name_to_extract:
        contents = entry["contents"]
        story=entry["story"]
        comments=entry["comments"]
        for item in contents:
            dialog.append(item["dialog"])

        
model=PromptGenerator()
model.generate_prompt(name_to_extract,dialog,story,comments)