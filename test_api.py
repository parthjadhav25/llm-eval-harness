import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

response = requests.post(
    "https://api.groq.com/openai/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "user", "content": "What is the capital of France?"}
        ]
    }
)

data = response.json()
answer = data["choices"][0]["message"]["content"]
print(answer)