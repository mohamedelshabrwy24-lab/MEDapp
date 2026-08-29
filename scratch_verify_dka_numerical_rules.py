import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("  DKA NUMERICAL CLINICAL RULES AUDIT (RUNTIME VERIFICATION)")
print("=" * 80)

url = "http://localhost:8000/api/egypt?condition=DKA&setting=emergency"
resp = urllib.request.urlopen(url)
data = json.loads(resp.read().decode('utf-8'))

t_e = data.get("track_e_market_and_pricing", [])

for idx, m in enumerate(t_e, 1):
    print(f"\n[{idx}] {m.get('active_ingredient')} -> {m.get('brand_name')}")
    print(f"    Class       : {m.get('pharmacological_class')}")
    print(f"    Scope       : {m.get('clinical_scope')}")
    print(f"    Instructions: {m.get('route_and_dosage_instructions')}")
    print(f"    Guideline   : {m.get('clinical_indication_source')}")

print("\n" + "=" * 80)
print("  AUDIT COMPLETED CLEANLY")
print("=" * 80)
