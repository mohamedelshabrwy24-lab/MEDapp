import json
import sys
from egypt_engine import EgyptResearchEngine

sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("  PHASE 4 TEST: 6-TRACK EGYPT RESEARCH ENGINE")
print("=" * 80)

engine = EgyptResearchEngine()
dossier = engine.execute_egypt_research("Asthma", "emergency")

# Track A: Official Guidance
t_a = dossier["track_a_official_guidance"]
print("\n[TRACK A] EGYPTIAN OFFICIAL / NATIONAL GUIDANCE:")
print(f"Strongest Source: {t_a['strongest_source']}")
print(f"Total Official Docs: {len(t_a['documents'])}")
for doc in t_a["documents"]:
    print(f"• {doc['organization']}: {doc['title']} ({doc['publication_date']})")
    print(f"  Scope: {doc['scope']}")
    print(f"  URL: {doc['source_url']}")
    print("-" * 50)

# Track B: Egyptian Scientific Studies
t_b = dossier["track_b_scientific_evidence"]
print(f"\n[TRACK B] EGYPTIAN SCIENTIFIC STUDIES ({len(t_b['verified_studies'])} Verified Studies):")
for st in t_b["verified_studies"][:3]:
    print(f"• {st['title']} ({st['pub_year']})")
    print(f"  Authors: {st['authors']} | Journal: {st['journal']}")
    print(f"  PMID: {st['pmid']} | DOI: {st['doi']}")
    print(f"  URL: {st['article_url']}")
    print(f"  Affiliation Proof: {st['affiliation_evidence']}")
    print("-" * 50)

# Track C: Real-World Clinical Practice
t_c = dossier["track_c_clinical_practice"]
print("\n[TRACK C] REAL-WORLD CLINICAL PRACTICE:")
for hp in t_c["hospital_protocols"]:
    print(f"• {hp['institution']}: {hp['pathway_name']}")
    print(f"  Details: {hp['description']}")
    print("-" * 50)
print("Workarounds:")
for w in t_c["resource_limited_workarounds"]:
    print(f"  - {w}")

# Track D & E: Regulatory & Market
print("\n[TRACKS D & E] REGULATORY STATUS & MARKET PRICING (Sample):")
for item in dossier["track_e_market_and_pricing"][:4]:
    print(f"• Active INN   : {item['active_ingredient']}")
    print(f"  Brand Name   : {item['brand_name']} ({item['manufacturer']})")
    print(f"  Dosage Form  : {item['dosage_form']}")
    print(f"  Reported Price: {item['reported_price_egp']} ({item['price_date']})")
    print(f"  Market Source: {item['market_source']}")
    print("-" * 50)

# Build Grounding Context
context_text = engine.build_egypt_grounding_context(dossier)
print(f"\n[GROUNDING CONTEXT] Context Length: {len(context_text)} characters")

print("\n" + "=" * 80)
print("  PHASE 4 EGYPT ENGINE TEST COMPLETE")
print("=" * 80)
