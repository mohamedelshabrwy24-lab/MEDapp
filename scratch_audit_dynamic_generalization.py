import json
import sys
from egypt_engine import EgyptResearchEngine

sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("  PHASE 4 CODE-LEVEL AUDIT: DYNAMIC GENERALIZATION TEST")
print("=" * 80)

engine = EgyptResearchEngine()

conditions = ["Asthma", "DKA", "UTI"]

for cond in conditions:
    print(f"\n{'='*30} TESTING: {cond} {'='*30}")
    dossier = engine.execute_egypt_research(cond, "emergency")

    # Track A: Official Guidance
    t_a = dossier.get("track_a_official_guidance", {})
    print(f"[Track A - Official Docs] Count: {len(t_a.get('documents', []))}")
    for d in t_a.get("documents", []):
        print(f"  • {d.get('issuing_organization')}: {d.get('exact_title')}")

    # Track B: Scientific Evidence
    t_b = dossier.get("track_b_scientific_evidence", {})
    print(f"[Track B - Scientific Evidence] Verified Studies Count: {t_b.get('verified_studies_count')}")
    for st in t_b.get("verified_studies", [])[:2]:
        print(f"  • PMID: {st.get('verified_pmid')} | Title: {st.get('verified_title')}")
        print(f"    Egypt Affil: {st.get('egypt_relevance')[:80]}")

    # Track C: Practice
    t_c = dossier.get("track_c_clinical_practice", {})
    print(f"[Track C - Clinical Practice] Hospital Protocols Count: {len(t_c.get('hospital_protocols', []))}")
    for hp in t_c.get("hospital_protocols", []):
        print(f"  • {hp.get('institution')}: {hp.get('practice_claim')[:70]}...")

    # Tracks D & E: Meds
    t_e = dossier.get("track_e_market_and_pricing", [])
    print(f"[Track E - Medications Returned] Count: {len(t_e)}")
    for m in t_e[:2]:
        print(f"  • INN: {m.get('active_ingredient')} | Brand: {m.get('brand_name')}")
