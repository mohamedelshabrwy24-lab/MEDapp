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

models_list = [
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite-preview",
    "gemini-3.1-flash-lite",
    "gemini-3-flash-preview",
    "gemini-flash-latest",
    "gemini-flash-lite-latest",
    "gemma-4-26b-a4b-it",
    "gemma-4-31b-it"
]

print("Probing all models for available quota:")
for m in models_list:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
    body = {"contents": [{"parts": [{"text": "Say OK"}]}]}
    req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            txt = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '').strip()
            print(f"  ✅ {m:30s} : SUCCESS -> {txt[:40]}")
    except urllib.error.HTTPError as e:
        err = e.read().decode('utf-8')
        try:
            err_j = json.loads(err)
            msg = err_j.get('error', {}).get('message', '')[:60]
        except Exception:
            msg = err[:60]
        print(f"  ❌ {m:30s} : HTTP {e.code} -> {msg}")
    except Exception as e:
        print(f"  ❌ {m:30s} : TIMEOUT/ERR -> {str(e)[:60]}")
