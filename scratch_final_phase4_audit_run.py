import urllib.request
import json
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("  FINAL PHASE 4 AUDIT RUN: ASTHMA (EMERGENCY)")
print("=" * 80)

# Step 1: Query /api/egypt
eg_url = 'http://localhost:8000/api/egypt?condition=Asthma&setting=emergency'
eg_resp = urllib.request.urlopen(eg_url)
eg_data = json.loads(eg_resp.read().decode('utf-8'))

print("\n[A] FINAL VERIFIED EGYPTIAN STUDIES (TRACK B):")
t_b = eg_data.get('track_b_scientific_evidence', {})
print(f"Total Verified Studies: {t_b.get('verified_studies_count')}")

for idx, st in enumerate(t_b.get('verified_studies', []), 1):
    print(f"\n{idx}. Verified Title     : {st.get('verified_title')}")
    print(f"   Authors            : {st.get('authors')} | Journal: {st.get('journal')} ({st.get('pub_year')})")
    print(f"   Verified PMID      : {st.get('verified_pmid')}")
    print(f"   Verified DOI       : {st.get('verified_doi')}")
    print(f"   Publication Type   : {st.get('verified_publication_type')}")
    print(f"   Egypt Relevance    : {st.get('egypt_relevance')}")
    print(f"   Clinical Relevance : {st.get('clinical_relevance')}")
    print(f"   Evidence Type      : {st.get('evidence_type')} (Confidence: {st.get('confidence')})")
    print(f"   Original URL       : {st.get('original_url')}")
    print(f"   Verification Source: {st.get('verification_source')}")
    print(f"   Verification Time  : {st.get('verification_timestamp')}")

print("\n" + "=" * 80)
print("[B] FINAL VERIFIED EGYPTIAN OFFICIAL SOURCES (TRACK A):")
t_a = eg_data.get('track_a_official_guidance', {})
for doc in t_a.get('documents', []):
    print(f"• [{doc.get('evidence_tier')}] {doc.get('organization')}")
    print(f"  Title: {doc.get('title')} ({doc.get('publication_date')}) [{doc.get('status')}]")
    print(f"  Scope: {doc.get('scope')}")
    print(f"  Document Type: {doc.get('document_type')} | URL: {doc.get('source_url')}")
    print("-" * 50)
for sdoc in t_a.get('society_documents', []):
    print(f"• [{sdoc.get('evidence_tier')}] {sdoc.get('organization')}")
    print(f"  Title: {sdoc.get('title')} ({sdoc.get('publication_date')}) [{sdoc.get('status')}]")
    print(f"  Document Type: {sdoc.get('document_type')} | URL: {sdoc.get('source_url')}")
    print("-" * 50)

print("\n" + "=" * 80)
print("[C] FINAL VERIFIED MEDICATION RECORDS (TRACKS D & E):")
t_e = eg_data.get('track_e_market_and_pricing', [])
for med in t_e:
    print(f"• INN Active Ingredient     : {med.get('active_ingredient')}")
    print(f"  Egyptian Brand            : {med.get('brand_name')}")
    print(f"  Strength & Dosage Form    : {med.get('dosage_form')}")
    print(f"  Manufacturer              : {med.get('manufacturer')}")
    print(f"  EDA Registration Source   : {med.get('eda_registration_source')}")
    print(f"  EDA Formulary Evidence URL: {med.get('eda_formulary_evidence')}")
    print(f"  Market Source             : {med.get('market_source')}")
    print(f"  Price Source & Date       : {med.get('price_source_and_date')}")
    print(f"  Availability Source & Date: {med.get('availability_source_and_date')}")
    print(f"  Safety / Pharmacovigilance: {med.get('safety_alerts')}")
    print("-" * 50)

print("\n" + "=" * 80)
print("[D] RECORDS EXCLUDED BECAUSE OF IDENTIFIER / PROVENANCE CONFLICTS:")
for ex in t_b.get('excluded_off_topic_studies', []):
    print(f"• Excluded PMID: {ex.get('pmid')} -> {ex.get('title')}")
    print(f"  Reason       : {ex.get('reason')}")
    print("-" * 50)

# Step 2: Full Research Call
t0 = time.time()
req_data = json.dumps({'condition': 'Asthma', 'setting': 'emergency'}).encode('utf-8')
req = urllib.request.Request('http://localhost:8000/api/research', data=req_data, headers={'Content-Type': 'application/json'})

print("\nExecuting live fresh /api/research for Asthma (Emergency)...")
resp = urllib.request.urlopen(req, timeout=120)
elapsed = round(time.time() - t0, 2)
result = json.loads(resp.read().decode('utf-8'))

print(f"\nResearch Complete: HTTP {resp.status} in {elapsed}s")
eg_rep = result.get('egypt_practice_and_pharmacology', {})
eg_b = eg_rep.get('track_b_scientific_and_epidemiological_evidence', {})
print("\n[Synthesized Track B in Final Report]:")
print("Local Epidemiology / Cohorts:", eg_b.get('local_epidemiology_and_cohorts'))
print("AMR / Biomarkers            :", eg_b.get('antimicrobial_resistance_and_biomarkers'))

print("\n" + "=" * 80)
print("  FINAL AUDIT RUN SUCCESSFUL")
print("=" * 80)
