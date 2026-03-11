# src/data_generation/llm_generator.py
import os
import yaml
from dotenv import load_dotenv
from openai import OpenAI

# 1. 加载环境变量
load_dotenv()  # 自动读取根目录的 .env 文件

# 2. 加载 Prompt 模板
with open("src/data_generation/prompts.yaml", "r", encoding="utf-8") as f:
    PROMPTS = yaml.safe_load(f)

# 3. 初始化客户端
client = OpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_API_BASE_URL")
)

def generate_dialogue(topic, emotion):
    # 格式化 Prompt
    prompt_text = PROMPTS["dialogue_generation"].format(
        topic=topic, 
        emotion=emotion, 
        turns=os.getenv("MAX_DIALOGUE_TURNS", 8)
    )
    
    # 调用 API
    response = client.chat.completions.create(
        model=os.getenv("LLM_MODEL_NAME"),
        messages=[
            {"role": "system", "content": PROMPTS["system_role"] + PROMPTS["safety_constraints"]},
            {"role": "user", "content": prompt_text}
        ],
        response_format={"type": "json_object"}  # 强制输出 JSON
    )
    
    return response.choices[0].message.content

# 测试
if __name__ == "__main__":
    print("生成测试...")
    result = generate_dialogue("考试焦虑", "anxiety")
    print(result)