import urllib.request
import json
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("  PHASE 3 FINAL AUDIT & SCOPE VERIFICATION: ASTHMA (EMERGENCY)")
print("=" * 80)

# Step 1: Query /api/research for Asthma Emergency
t0 = time.time()
req_data = json.dumps({'condition': 'Asthma', 'setting': 'emergency'}).encode('utf-8')
req = urllib.request.Request('http://localhost:8000/api/research', data=req_data, headers={'Content-Type': 'application/json'})

print("\nExecuting research call for Asthma (Emergency)...")
resp = urllib.request.urlopen(req, timeout=120)
elapsed = round(time.time() - t0, 2)
result = json.loads(resp.read().decode('utf-8'))

print(f"Research Completed: HTTP {resp.status} in {elapsed}s")

# Step 2: Inspect Guidelines Evidence & Scope
g_ev = result.get('guidelines_evidence', {})
print("\n" + "=" * 50)
print("  GUIDELINE SCOPE & APPLICABILITY AUDIT")
print("=" * 50)
for g in g_ev.get('guideline_records', []):
    print(f"• Organization : {g.get('organization')}")
    print(f"  Title        : {g.get('guideline_title')}")
    print(f"  Year & Status: {g.get('publication_year')} [{g.get('status')}]")
    print(f"  Scope        : {g.get('scope')}")
    print(f"  Population   : {g.get('target_population')}")
    print(f"  Applicability: {g.get('setting_applicability')} (Primary for Emergency: {g.get('is_primary_for_setting')})")
    print(f"  PMID / DOI   : {g.get('pmid')} | {g.get('doi')}")
    print(f"  URL          : {g.get('article_url')}")
    print("-" * 50)

# Step 3: Inspect Gemini's Synthesized Authoritative Guidelines
g_rep = result.get('guidelines', {})
auth_g = g_rep.get('authoritative_guidelines', [])
print("\n" + "=" * 50)
print(f"  GEMINI SYNTHESIZED GUIDELINES ({len(auth_g)} items)")
print("=" * 50)
for item in auth_g:
    print(f"• {item.get('organization')} ({item.get('year')})")
    print(f"  Title   : {item.get('guideline_title')}")
    print(f"  Strength: {item.get('recommendation_strength')} | Certainty: {item.get('evidence_certainty')}")
    print(f"  Key Rec : {item.get('key_recommendation')}")
    print(f"  URL     : {item.get('source_url')}")
    print("-" * 50)

print("\n" + "=" * 80)
print("  VERIFICATION COMPLETE")
print("=" * 80)
