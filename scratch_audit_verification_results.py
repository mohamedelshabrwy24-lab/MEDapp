import urllib.request
import json
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("  POST-AUDIT SOURCE VERIFICATION TEST: ASTHMA (EMERGENCY)")
print("=" * 80)

# Step 1: Direct Guidelines Endpoint Audit
g_url = 'http://localhost:8000/api/guidelines?condition=Asthma&setting=emergency'
g_resp = urllib.request.urlopen(g_url)
g_data = json.loads(g_resp.read().decode('utf-8'))

print("\n--- 1. DIRECT GUIDELINES ENDPOINT AUDIT ---")
print(f"Condition           : {g_data.get('condition')}")
print(f"Guidelines Found    : {g_data['counts']['official_guidelines_found']}")
print(f"Cochrane Found      : {g_data['counts']['landmark_cochrane_found']}")
print(f"Update Studies Found: {g_data['counts']['recent_updates_found']}")

print("\n[A] OFFICIAL GUIDELINES RETRIEVED:")
for g in g_data['guideline_records']:
    print(f"• Org   : {g.get('organization')}")
    print(f"  Title : {g.get('guideline_title')}")
    print(f"  Year  : {g.get('publication_year')} [{g.get('current_status')}]")
    print(f"  PMID  : {g.get('pmid')} | DOI: {g.get('doi')}")
    print(f"  URL   : {g.get('article_url')}")
    print(f"  Design: {g.get('evidence_designation')}")
    print("-" * 50)

print("\n[B] COMPLETED COCHRANE & LANDMARK REVIEWS (PROTOCOLS EXCLUDED):")
for c in g_data['cochrane_and_landmark_evidence']:
    print(f"• Title : {c.get('title')}")
    print(f"  Year  : {c.get('year')} | PMID: {c.get('pmid')} | DOI: {c.get('doi')}")
    print(f"  URL   : {c.get('article_url')}")
    print(f"  Design: {c.get('design')} (Is Protocol: {c.get('is_protocol')})")
    print("-" * 50)

print("\n[C] POST-GUIDELINE UPDATE STUDIES (2024-2026):")
for u in g_data['update_search_recent_evidence']:
    print(f"• Title : {u.get('study_title')}")
    print(f"  Year  : {u.get('year')} | PMID: {u.get('pmid')} | DOI: {u.get('doi')}")
    print(f"  URL   : {u.get('article_url')}")
    print(f"  Design: {u.get('design')}")
    print("-" * 50)

# Step 2: Full End-to-End Synthesis Test
t0 = time.time()
req_data = json.dumps({'condition': 'Asthma', 'setting': 'emergency'}).encode('utf-8')
req = urllib.request.Request('http://localhost:8000/api/research', data=req_data, headers={'Content-Type': 'application/json'})

print("\n--- 2. FULL RESEARCH SYNTHESIS TEST WITH AUDITED GROUNDING ---")
resp = urllib.request.urlopen(req, timeout=120)
elapsed = round(time.time() - t0, 2)
result = json.loads(resp.read().decode('utf-8'))

print(f"Synthesis Complete: HTTP {resp.status} in {elapsed}s")
trials = result.get('guidelines', {}).get('landmark_evidence_and_trials', [])
print(f"\nLandmark Evidence Cited by Gemini ({len(trials)} studies):")
for t in trials:
    print(f"• Study : {t.get('trial_name_or_study')}")
    print(f"  PMID  : {t.get('pmid')} | DOI: {t.get('doi')}")
    print(f"  URL   : {t.get('article_url')}")
    print(f"  Design: {t.get('design')}")
    print(f"  Impact: {t.get('clinical_takeaway')}")
    print("-" * 50)

print("\n" + "=" * 80)
print("  AUDIT VERIFICATION TEST COMPLETE")
print("=" * 80)
