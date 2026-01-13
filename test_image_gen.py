
import os
import requests
import json
import base64
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

model_name = "gemini-2.5-flash-image" # User requested this model
# Note: Usually this is a vision model (image input). 
# If it supports generation, the endpoint might be different or the payload specific.
# Let's try standard generateContent with a request for an image.

url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
headers = {'Content-Type': 'application/json'}

prompt_text = "Generate a cinematic image of a futuristic unmanned surface vessel (USV) patrolling the ocean at sunset."

data = {
    "contents": [{"parts": [{"text": prompt_text}]}],
    # "generationConfig": {"response_mime_type": "image/jpeg"} # Hypothetical
}

print(f"Testing generation on {model_name}...")
response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    print("Success! Checking response...")
    print(response.text[:500]) # Print first 500 chars to see if it's text or binary/base64 structure
else:
    print(f"Failed: {response.status_code}")
    print(response.text)

# Also try another variant if the above fails to be "image gen"
print("\n--- Listing model info ---")
info_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}?key={api_key}"
resp_info = requests.get(info_url)
print(resp_info.text)
