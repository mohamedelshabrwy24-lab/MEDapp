import urllib.request
import json
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("  POST-AUDIT EGYPT RELEVANCE & PROVENANCE VERIFICATION: ASTHMA (EMERGENCY)")
print("=" * 80)

# Step 1: Query /api/egypt
eg_url = 'http://localhost:8000/api/egypt?condition=Asthma&setting=emergency'
eg_resp = urllib.request.urlopen(eg_url)
eg_data = json.loads(eg_resp.read().decode('utf-8'))

print("\n--- 1. TRACK B: AUDITED EGYPTIAN SCIENTIFIC STUDIES TABLE ---")
t_b = eg_data.get('track_b_scientific_evidence', {})
print(f"Verified On-Topic Studies Count: {t_b.get('verified_studies_count')}")
print(f"Excluded Off-Topic Studies Count: {t_b.get('excluded_off_topic_count')}")

for st in t_b.get('verified_studies', []):
    print(f"• Source / Title    : {st.get('title')} ({st.get('pub_year')})")
    print(f"  Egypt Relevance   : {st.get('egypt_relevance_reason')}")
    print(f"  Clinical Relevance: {st.get('clinical_relevance_reason')}")
    print(f"  Source Type       : {st.get('source_type')}")
    print(f"  Evidence Type     : {st.get('evidence_type')} (Confidence: {st.get('confidence')})")
    print(f"  Verified?         : {st.get('is_verified')}")
    print(f"  PMID / DOI        : {st.get('pmid')} | {st.get('doi')}")
    print(f"  Original URL      : {st.get('article_url')}")
    print("-" * 60)

print("\n--- 2. TRACKS D & E: MEDICATION PROVENANCE SEPARATION TABLE ---")
t_e = eg_data.get('track_e_market_and_pricing', [])
for med in t_e:
    print(f"• INN          : {med.get('active_ingredient')}")
    print(f"  Brand        : {med.get('brand_name')}")
    print(f"  Dosage Form  : {med.get('dosage_form')}")
    print(f"  Manufacturer : {med.get('manufacturer')}")
    print(f"  EDA Status   : {med.get('eda_registration_status')} [Tier 1]")
    print(f"  EDA URL      : {med.get('eda_official_url')}")
    print(f"  Market Source: {med.get('market_source')} [Tier 5]")
    print(f"  Price (EGP)  : {med.get('reported_price_egp')} (Date: {med.get('price_date')})")
    print(f"  Availability : {med.get('availability_source')}")
    print("-" * 60)

# Step 2: Full Research Call
t0 = time.time()
req_data = json.dumps({'condition': 'Asthma', 'setting': 'emergency'}).encode('utf-8')
req = urllib.request.Request('http://localhost:8000/api/research', data=req_data, headers={'Content-Type': 'application/json'})

print("\n--- 3. FULL RESEARCH SYNTHESIS WITH AUDITED EGYPTIAN GROUNDING ---")
resp = urllib.request.urlopen(req, timeout=120)
elapsed = round(time.time() - t0, 2)
result = json.loads(resp.read().decode('utf-8'))

print(f"Research Completed: HTTP {resp.status} in {elapsed}s")

eg_rep = result.get('egypt_practice_and_pharmacology', {})
eg_b = eg_rep.get('track_b_scientific_and_epidemiological_evidence', {})
print("\n[Synthesized Track B in Final Report]:")
print("Local Epidemiology / Cohorts:", eg_b.get('local_epidemiology_and_cohorts'))
print("AMR / Biomarkers            :", eg_b.get('antimicrobial_resistance_and_biomarkers'))

print("\n" + "=" * 80)
print("  AUDIT VERIFICATION COMPLETE")
print("=" * 80)
