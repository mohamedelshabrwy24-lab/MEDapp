import time
import urllib.request
import urllib.parse
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("  VERIFYING CORRECTED DKA CLINICAL RULES IN REAL SERVER RESPONSE")
print("=" * 80)

url = "http://localhost:8000/api/research"
payload = {
    "condition": "DKA",
    "setting": "emergency"
}

t_start = time.time()
req = urllib.request.Request(
    url,
    data=json.dumps(payload).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)

try:
    with urllib.request.urlopen(req, timeout=120) as resp:
        t_total = time.time() - t_start
        status_code = resp.status
        data = json.loads(resp.read().decode('utf-8'))
        
        print(f"• HTTP Status           : {status_code} OK")
        print(f"• Total Latency         : {t_total:.2f} seconds")
        print(f"• Active Model          : {data.get('pipeline_metadata', {}).get('active_model')}")
        
        # Check Management Steps
        steps = data.get("guidelines", {}).get("stepped_management_protocol", [])
        print(f"\n--- STEPPED MANAGEMENT PROTOCOL ({len(steps)} steps) ---")
        
        full_text_dossier = json.dumps(data, ensure_ascii=False)
        
        # Check for obsolete wording
        obsolete_matches = re.findall(r"1000\s*[-–]\s*1500\s*ml", full_text_dossier, re.IGNORECASE)
        print(f"• Obsolete '1000–1500 mL' occurrences in final payload: {len(obsolete_matches)} {obsolete_matches}")
        
        for st in steps:
            print(f"\n[Step {st.get('step_number')}] {st.get('title')} ({st.get('priority')})")
            print(f"  Details: {st.get('clinical_details')}")
            for med in st.get("medications", []):
                print(f"    - Drug: {med.get('generic_name')} | Dose: {med.get('dose')} | Route: {med.get('route')} | Notes: {med.get('clinical_notes')}")

        # Check Safety Monitoring & Warnings
        sm = data.get("guidelines", {}).get("safety_monitoring_and_warnings", {})
        print("\n--- SAFETY MONITORING & WARNINGS ---")
        print(f"• Boxed Warnings: {sm.get('boxed_warnings_and_contraindications')}")
        print(f"• Monitoring Parameters: {sm.get('monitoring_parameters')}")
        print(f"• Special Populations: {sm.get('special_populations')}")

        # Check Egyptian Medications
        meds = data.get("egypt_practice_and_pharmacology", {}).get("track_d_and_e_medication_landscape", [])
        print(f"\n--- EGYPTIAN MEDICATION LANDSCAPE ({len(meds)} items) ---")
        for m in meds:
            print(f"• {m.get('active_ingredient')} -> {m.get('famous_egyptian_brands')} | Price: {m.get('reported_price_range_egp')}")

except urllib.error.HTTPError as e:
    print(f"• HTTP Error {e.code}: {e.read().decode('utf-8')}")
except Exception as e:
    print(f"• Exception: {e}")

print("\n" + "=" * 80)
