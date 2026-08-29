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

models_to_test = [
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-flash-latest",
    "gemini-3.1-pro-preview",
    "gemini-2.5-flash"
]

print("Testing generateContent across candidate models:")
for m in models_to_test:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
    body = {"contents": [{"parts": [{"text": "Respond with JSON: {\"status\": \"ok\", \"model\": \"" + m + "\"}"}]}], "generationConfig": {"responseMimeType": "application/json"}}
    req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            txt = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            print(f"  ✅ {m:25s} : SUCCESS -> {txt.strip()[:60]}")
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode('utf-8')
        print(f"  ❌ {m:25s} : HTTP {e.code} -> {err_msg[:80]}")
    except Exception as e:
        print(f"  ❌ {m:25s} : ERROR -> {e}")
