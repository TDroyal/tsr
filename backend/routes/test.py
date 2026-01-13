from openai import OpenAI
DEEPSEEK_API_KEY = "my token"
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

resp = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "user", "content": "你好"}
    ]
)

print(resp)