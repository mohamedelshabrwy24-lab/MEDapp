import urllib.request
import json
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("=" * 70)
print("  PHASE 3 FULL PIPELINE TEST: ASTHMA (EMERGENCY)")
print("=" * 70)

# 1. Test Health Endpoint
h_resp = urllib.request.urlopen('http://localhost:8000/api/health')
health = json.loads(h_resp.read().decode('utf-8'))
print(f"Health Status: {health.get('status')}")
print(f"Phase        : {health.get('phase')}")
print(f"Stages       : {health.get('research_pipeline_stages')}")

# 2. Test /api/research with Phase 3 Grounding
t0 = time.time()
req_data = json.dumps({'condition': 'Asthma', 'setting': 'emergency'}).encode('utf-8')
req = urllib.request.Request('http://localhost:8000/api/research', data=req_data, headers={'Content-Type': 'application/json'})

print("\nExecuting live Phase 3 /api/research for Asthma (Emergency)...")
resp = urllib.request.urlopen(req, timeout=120)
elapsed = round(time.time() - t0, 2)
result = json.loads(resp.read().decode('utf-8'))

print(f"\nResponse Received: HTTP {resp.status} in {elapsed}s")
print(f"Condition: {result.get('condition_name')}")

c = result.get('classification', {})
print("\n" + "=" * 50)
print("  [1] SPECIALTY CLASSIFICATION & SOCIETY ROUTING")
print("=" * 50)
print(f"• Primary Specialty   : {c.get('primary_specialty')}")
print(f"• Secondary Branches  : {', '.join(c.get('secondary_specialties', []))}")
print(f"• Clinical Questions  : {', '.join(c.get('clinical_question_type', []))}")

pipeline = result.get('pipeline_metadata', {})
print("\n" + "=" * 50)
print("  [2] PIPELINE METADATA & RETRIEVAL STATS")
print("=" * 50)
print("Stages Completed              :", pipeline.get('stages_completed'))
print("Official Guidelines Retrieved :", pipeline.get('official_guidelines_retrieved'))
print("Cochrane Reviews Retrieved    :", pipeline.get('cochrane_reviews_retrieved'))
print("Post-Guideline Updates (2024+):", pipeline.get('post_guideline_updates_retrieved'))
print("Europe PMC Records Retrieved  :", pipeline.get('europepmc_records_retrieved'))

g = result.get('guidelines', {})
auth_g = g.get('authoritative_guidelines', [])
print("\n" + "=" * 50)
print(f"  [3] AUTHORITATIVE GUIDELINES IN FINAL REPORT ({len(auth_g)} Guidelines)")
print("=" * 50)
for item in auth_g:
    print(f"• Organization : {item.get('organization')} ({item.get('year')})")
    print(f"  Title        : {item.get('guideline_title')}")
    print(f"  Strength     : {item.get('recommendation_strength')} | Certainty: {item.get('evidence_certainty')}")
    print(f"  Key Rec      : {item.get('key_recommendation')}")
    print(f"  URL/Source   : {item.get('source_url')}")
    print("-" * 40)

cd = g.get('guideline_consensus_and_divergence', {})
print("\n" + "=" * 50)
print("  [4] GUIDELINE CONSENSUS VS DIVERGENCE ANALYSIS")
print("=" * 50)
print("Consensus Points:")
for p in cd.get('consensus_points', []):
    print(f"  ✅ {p}")
print("\nDivergence Points:")
for d in cd.get('divergence_points', []):
    if isinstance(d, dict):
        print(f"  ⚡ Issue : {d.get('issue')}")
        print(f"     Details: {d.get('details')}")
        print(f"     Reasons: {d.get('underlying_reasons')}")
    else:
        print(f"  ⚡ {d}")

trials = g.get('landmark_evidence_and_trials', [])
print("\n" + "=" * 50)
print(f"  [5] LANDMARK EVIDENCE & COCHRANE CITATIONS ({len(trials)} Studies)")
print("=" * 50)
for t in trials:
    print(f"• Study : {t.get('trial_name_or_study')} ({t.get('year')})")
    print(f"  PMID  : {t.get('pmid') or 'N/A'} | DOI: {t.get('doi') or 'N/A'}")
    print(f"  URL   : {t.get('article_url') or 'N/A'}")
    print(f"  Design: {t.get('design')}")
    print(f"  Impact: {t.get('clinical_takeaway')}")
    print("-" * 40)

print("\n" + "=" * 70)
print("  PHASE 3 END-TO-END TEST COMPLETE")
print("=" * 70)
