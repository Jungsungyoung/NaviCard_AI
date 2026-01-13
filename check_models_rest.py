
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

print(f"Checking models via REST: {url.replace(api_key, 'HIDDEN_KEY')}")
response = requests.get(url)

if response.status_code == 200:
    models = response.json().get('models', [])
    print(f"Found {len(models)} models.")
    for m in models:
        if 'generateContent' in m.get('supportedGenerationMethods', []):
            print(f" - {m['name']}")
else:
    print(f"Error: {response.status_code} - {response.text}")
