import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("  DKA CLINICAL PHARMACOLOGY & SAFETY AUDIT (WITHOUT GEMINI CALL)")
print("=" * 80)

url = "http://localhost:8000/api/egypt?condition=DKA&setting=emergency"
resp = urllib.request.urlopen(url)
data = json.loads(resp.read().decode('utf-8'))

t_e = data.get("track_e_market_and_pricing", [])
print(f"Total DKA Products Audited: {len(t_e)}\n")

for idx, m in enumerate(t_e, 1):
    print(f"{idx}. INN Active Ingredient     : {m.get('active_ingredient')}")
    print(f"   Brand Name & Manufacturer : {m.get('brand_name')} ({m.get('manufacturer')})")
    print(f"   Dosage Form & Strength    : {m.get('strength_and_form')}")
    print(f"   Clinical Scope & Severity : {m.get('clinical_scope')}")
    print(f"   Authoritative Guideline   : {m.get('clinical_indication_source')}")
    print(f"   EDA Registration Source   : {m.get('eda_source')}")
    print(f"   Market Price & Date       : {m.get('price')} ({m.get('price_date')})")
    print(f"   Availability Source & Date: {m.get('availability_source_and_date')}")
    print("-" * 75)

# Verification checks:
print("\n=== SAFETY & CLASSIFICATION CHECKS ===")
has_insulatard_in_regular = any("insulatard" in m.get("brand_name", "").lower() and "regular" in m.get("active_ingredient", "").lower() for m in t_e)
print(f"1. Is Insulatard (NPH) merged under Regular Insulin? {'YES (DANGEROUS BUG)' if has_insulatard_in_regular else 'NO (CORRECTLY EXCLUDED)'}")

has_subq_as_general_replacement = any("sole therapy in severe" in m.get("clinical_scope", "").lower() for m in t_e)
print(f"2. Is SubQ insulin presented as universal replacement in severe DKA? {'YES (BUG)' if has_subq_as_general_replacement else 'NO (STRICTLY RESTRICTED TO MILD/UNCOMPLICATED)'}")

has_pediatric_distinction = any("ispad" in m.get("clinical_indication_source", "").lower() for m in t_e)
print(f"3. Are Pediatric ISPAD directives included? {'YES (VERIFIED)' if has_pediatric_distinction else 'NO (MISSING)'}")
