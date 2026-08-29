import urllib.request
import json
import time

with open("scratch_verify_grounded_research.py", "w", encoding="utf-8") as f:
    f.write('''import urllib.request
import json
import time
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

t0 = time.time()
data = json.dumps({'condition': 'Asthma', 'setting': 'emergency'}).encode('utf-8')
req = urllib.request.Request('http://localhost:8000/api/research', data=data, headers={'Content-Type': 'application/json'})

resp = urllib.request.urlopen(req, timeout=120)
elapsed = round(time.time() - t0, 2)
result = json.loads(resp.read().decode('utf-8'))

print("=" * 70)
print(f"RESEARCH DOSSIER GENERATED (HTTP {resp.status} in {elapsed}s)")
print("=" * 70)
print("Condition     :", result.get('condition_name'))
print("Classification:", result.get('classification', {}).get('primary_specialty'))

pipeline = result.get('pipeline_metadata', {})
print("\\n--- PIPELINE EXECUTION ---")
print("Stages:", pipeline.get('stages_completed'))
print("Europe PMC Total Retrieved:", pipeline.get('europepmc_records_retrieved'))
print("Grounding Papers Injected :", pipeline.get('grounding_papers_injected'))

print("\\n--- LANDMARK TRIALS GROUNDED ON LIVE EUROPE PMC ---")
for t in result.get('guidelines', {}).get('landmark_evidence_and_trials', []):
    print(f"• Study: {t.get('trial_name_or_study')}")
    print(f"  PMID : {t.get('pmid')} | DOI: {t.get('doi')}")
    print(f"  URL  : {t.get('article_url')}")
    print(f"  Type : {t.get('design')}")
    print(f"  Takeaway: {t.get('clinical_takeaway')}")
    print()

print("--- TRACK B: EGYPTIAN SCIENTIFIC LITERATURE GROUNDED ---")
eg_b = result.get('egypt_practice_and_pharmacology', {}).get('track_b_scientific_and_epidemiological_evidence', {})
print("Local Epidemiology:", eg_b.get('local_epidemiology_and_cohorts'))
print("AMR Patterns      :", eg_b.get('antimicrobial_resistance_and_biomarkers'))
''')
