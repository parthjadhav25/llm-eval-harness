import requests
import os
from dotenv import load_dotenv

load_dotenv()

r = requests.get(
    'https://api.groq.com/openai/v1/models',
    headers={'Authorization': f'Bearer {os.getenv("GROQ_API_KEY")}'}
)

for model in r.json()['data']:
    print(model['id'])