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

print(f"API Key present: {bool(api_key)}, length: {len(api_key)}")

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
try:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print("Available models in API:")
        for m in data.get("models", []):
            name = m.get("name", "")
            methods = m.get("supportedGenerationMethods", [])
            if "generateContent" in methods:
                print(f"  • {name}")
except Exception as e:
    print(f"Error querying models: {e}")
