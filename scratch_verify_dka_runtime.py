import urllib.request
import urllib.parse
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("  DKA RUNTIME VERIFICATION (WITHOUT GEMINI CALL)")
print("  Direct Engine & Gateway Inspection for Condition: DKA (Emergency)")
print("=" * 80)

# Step 1: Direct Egypt Engine API Call
url = "http://localhost:8000/api/egypt?condition=DKA&setting=emergency"
resp = urllib.request.urlopen(url)
data = json.loads(resp.read().decode('utf-8'))

print("\n[1] CLASSIFICATION & SPECIALTY:")
clf = data.get("classification", {})
print(f"• Primary Specialty   : {clf.get('primary_specialty')}")
print(f"• Secondary Specialties: {clf.get('secondary_specialties')}")
print(f"• Clinical Question    : {clf.get('clinical_question_type')}")

print("\n[2] TRACK A: DKA OFFICIAL EGYPTIAN GUIDANCE TARGETS:")
t_a = data.get("track_a_official_guidance", {})
print(f"• Strongest Source     : {t_a.get('strongest_source')}")
print(f"• Primary Specialty    : {t_a.get('primary_specialty')}")
for idx, doc in enumerate(t_a.get("documents", []), 1):
    print(f"  {idx}. Organization: {doc.get('issuing_organization')}")
    print(f"     Title       : {doc.get('exact_title')}")
    print(f"     Scope       : {doc.get('scope')}")
    print(f"     URL         : {doc.get('source_url')}")
for idx, sdoc in enumerate(t_a.get("society_documents", []), 1):
    print(f"  Society {idx} : {sdoc.get('issuing_organization')} ({sdoc.get('source_url')})")

print("\n[3] TRACK B: DKA EGYPTIAN SCIENTIFIC LITERATURE QUERY & VERIFIED STUDIES:")
t_b = data.get("track_b_scientific_evidence", {})
print(f"• Exact Query Sent to Europe PMC: {t_b.get('query_used')}")
print(f"• Total Records Retrieved       : {t_b.get('total_retrieved')}")
print(f"• Verified On-Topic Studies     : {t_b.get('verified_studies_count')}")
for idx, st in enumerate(t_b.get("verified_studies", []), 1):
    print(f"  {idx}. PMID: {st.get('verified_pmid')} | DOI: {st.get('verified_doi')}")
    print(f"     Title: {st.get('verified_title')}")
    print(f"     Affiliation Proof: {st.get('egypt_relevance')[:90]}...")
    print(f"     Clinical Relevance: {st.get('clinical_relevance')}")

print("\n[4] TRACK C: DKA CLINICAL PRACTICE & RAMADAN FASTING JURISPRUDENCE:")
t_c = data.get("track_c_clinical_practice", {})
for hp in t_c.get("hospital_protocols", []):
    print(f"• Institution: {hp.get('institution')}")
    print(f"  Claim      : {hp.get('practice_claim')}")
    print(f"  Status     : {hp.get('verification_label')}")
print("• Resource-Limited Workarounds:")
for w in t_c.get("resource_limited_workarounds", []):
    print(f"  - {w}")
print(f"• Ramadan Ruling: {t_c.get('cultural_and_ramadan_counseling')}")

print("\n[5] TRACKS D & E: DKA MEDICATION LANDSCAPE (ZERO ASTHMA DRUGS VERIFICATION):")
t_e = data.get("track_e_market_and_pricing", [])
print(f"• Total DKA Products Retrieved: {len(t_e)}")

asthma_drugs_found = []
for m in t_e:
    inn = m.get("active_ingredient", "")
    brand = m.get("brand_name", "")
    if any(ad in inn.lower() or ad in brand.lower() for ad in ["salbutamol", "ventolin", "farcolin", "butalin", "atrovent", "ipratropium"]):
        asthma_drugs_found.append(f"{brand} ({inn})")

print(f"• Asthma Drugs Found in DKA Results: {len(asthma_drugs_found)} -> {asthma_drugs_found}")

print("\n• DKA Medications List:")
for idx, m in enumerate(t_e, 1):
    print(f"  {idx}. INN Active   : {m.get('active_ingredient')}")
    print(f"     Brand Name   : {m.get('brand_name')} ({m.get('manufacturer')})")
    print(f"     Strength/Form: {m.get('strength_and_form')}")
    print(f"     EDA Source   : {m.get('eda_source')[:65]}...")
    print(f"     Market Price : {m.get('price')} ({m.get('price_date')})")
    print(f"     Clinical Ind : {m.get('clinical_indication_source')[:80]}...")
    print("     " + "-" * 50)

# Step 2: Build Grounding Context
from egypt_engine import EgyptResearchEngine
engine = EgyptResearchEngine()
grounding_text = engine.build_egypt_grounding_context(data)

print(f"\n[6] GROUNDING CONTEXT INJECTED INTO GEMINI PROMPT (Length: {len(grounding_text)} chars):")
has_asthma_in_grounding = "ventolin" in grounding_text.lower() or "farcolin" in grounding_text.lower() or "salbutamol" in grounding_text.lower()
print(f"• Contains Asthma References in Grounding Context? {'YES (BUG)' if has_asthma_in_grounding else 'NO (CLEAN)'}")

print("\n" + "=" * 80)
print("  DKA RUNTIME VERIFICATION COMPLETE")
print("=" * 80)
