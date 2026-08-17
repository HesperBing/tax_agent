import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")
base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
model = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")

if not api_key:
    raise ValueError("没有读取到 DEEPSEEK_API_KEY，请检查根目录中的 .env 文件")

client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

try:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "你是一个用于测试 API 连接的助手。"
            },
            {
                "role": "user",
                "content": "请只回答：DeepSeek API 连接成功"
            }
        ],
        max_tokens=50,
        stream=False
    )

    print("API 调用成功")
    print("模型：", model)
    print("回答：", response.choices[0].message.content)

except Exception as error:
    print("API 调用失败")
    print("错误类型：", type(error).__name__)
    print("错误信息：", error)