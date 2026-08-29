import os
import re
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8')

root = Path("C:/Users/Bakot/.gemini/antigravity/scratch/medref")

patterns = [
    r"1000",
    r"1500",
    r"10\s*[-–]\s*20\s*ml",
    r"250\s*[-–]\s*500",
    r"500\s*[-–]\s*1000",
    r"fluid resuscitation",
    r"resuscitation"
]

print("Searching files in MedRef directory for DKA fluid rule occurrences:\n")

for p in root.rglob("*.py"):
    if "venv" in str(p) or "__pycache__" in str(p):
        continue
    try:
        content = p.read_text(encoding='utf-8', errors='ignore')
        lines = content.splitlines()
        for idx, line in enumerate(lines, 1):
            for pat in patterns:
                if re.search(pat, line, re.IGNORECASE):
                    print(f"{p.name}:{idx} -> {line.strip()[:110]}")
                    break
    except Exception as e:
        print(f"Error reading {p}: {e}")
