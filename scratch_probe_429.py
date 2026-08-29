import urllib.request
import json
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8')

env_path = Path("C:/Users/Bakot/.gemini/antigravity/scratch/medref/.env")
api_key = ""
with open(env_path, 'r', encoding='utf-8') as f:
    for line in f:
        if line.startswith("GEMINI_API_KEY="):
            api_key = line.split("=", 1)[1].strip()

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={api_key}"
body = {"contents": [{"parts": [{"text": "Hello"}]}]}
req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        print("Success:", resp.read().decode('utf-8')[:100])
except urllib.error.HTTPError as e:
    print(f"HTTP {e.code} details:")
    print(e.read().decode('utf-8'))
