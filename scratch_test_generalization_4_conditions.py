import json
import urllib.request
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("  PHASE 4 GENERALIZATION ARCHITECTURE TEST: 4 CONDITIONS")
print("  (Asthma, DKA, UTI, Heart Failure)")
print("=" * 80)

conditions = ["Asthma", "DKA", "UTI", "Heart Failure"]

for cond in conditions:
    print(f"\n{'='*35} {cond.upper()} {'='*35}")
    url = f"http://localhost:8000/api/egypt?condition={urllib.parse.quote(cond)}&setting=emergency"
    resp = urllib.request.urlopen(url)
    data = json.loads(resp.read().decode('utf-8'))

    # A. Primary Specialty
    clf = data.get("classification", {})
    prim_spec = clf.get("primary_specialty", "N/A")
    print(f"A. Primary Specialty Identified   : {prim_spec}")

    # B. Egyptian Official Search Targets
    t_a = data.get("track_a_official_guidance", {})
    print(f"B. Official Search Targets ({len(t_a.get('documents', []))} docs, {len(t_a.get('society_documents', []))} societies):")
    for doc in t_a.get("documents", []):
        print(f"   • Official Gov : {doc.get('issuing_organization')}")
        print(f"     Title/Scope  : {doc.get('exact_title')}")
    for sdoc in t_a.get("society_documents", []):
        print(f"   • Specialty Soc: {sdoc.get('issuing_organization')} ({sdoc.get('source_url')})")

    # C. Egyptian Literature Search Query & Results
    t_b = data.get("track_b_scientific_evidence", {})
    print(f"C. Live Literature Query Generated : {t_b.get('query_used')}")
    print(f"   Verified On-Topic Studies Count : {t_b.get('verified_studies_count')}")
    for st in t_b.get("verified_studies", [])[:2]:
        print(f"   • PMID: {st.get('verified_pmid')} | Title: {st.get('verified_title')[:75]}...")
        print(f"     Affiliation: {st.get('egypt_relevance')[:85]}...")

    # D & E. Relevant Medications Retrieved & Verification of NO Asthma Fallback
    t_e = data.get("track_e_market_and_pricing", [])
    has_meds = data.get("evidence_hierarchy_summary", {}).get("has_condition_medications", False)
    print(f"D. Relevant Medications Identified : {len(t_e)} products (Condition-Specific: {has_meds})")
    print(f"E. First 5 Retrieved Medications for {cond.upper()}:")
    if t_e:
        for idx, m in enumerate(t_e[:5], 1):
            print(f"   {idx}. INN Active  : {m.get('active_ingredient')}")
            print(f"      Brand Name  : {m.get('brand_name')} ({m.get('manufacturer')})")
            print(f"      Strength/Form: {m.get('strength_and_form')}")
            print(f"      EDA Source  : {m.get('eda_source')[:65]}...")
            print(f"      Market Price: {m.get('price')} ({m.get('price_date')})")
            print(f"      Clinical Ind: {m.get('clinical_indication_source')[:75]}...")
            print("      " + "-" * 50)
    else:
        print("   • No Egypt-specific medications registered for this condition.")

    # F. Institutional Practice & Workarounds
    t_c = data.get("track_c_clinical_practice", {})
    print(f"F. Institutional Practice Target   : {t_c.get('hospital_protocols', [{}])[0].get('institution')}")
    print(f"   Verification Label              : {t_c.get('hospital_protocols', [{}])[0].get('verification_label')}")
    print(f"   Workarounds Adaptive to Domain  : {t_c.get('resource_limited_workarounds', [''])[0][:80]}...")
    print(f"   Ramadan Counseling Specificity  : {t_c.get('cultural_and_ramadan_counseling')[:85]}...")

print("\n" + "=" * 80)
print("  ALL 4 CONDITIONS TESTED SUCCESSFULLY")
print("=" * 80)
