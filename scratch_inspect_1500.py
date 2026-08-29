import json

# Let's inspect where 1000-1500 appeared
# It was likely in the contraindications in Section 2 or in the negative warnings
with open("C:/Users/Bakot/.gemini/antigravity/scratch/medref/clinical_rules.py", "r", encoding="utf-8") as f:
    code = f.read()
    print("In clinical_rules.py:")
    for idx, line in enumerate(code.splitlines(), 1):
        if "1000" in line and "1500" in line:
            print(f"  Line {idx}: {line.strip()}")
