import urllib.request
import json
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("  PHASE 4 FULL END-TO-END VERIFICATION: ASTHMA (EMERGENCY)")
print("=" * 80)

# Step 1: Check Health
h_resp = urllib.request.urlopen('http://localhost:8000/api/health')
health = json.loads(h_resp.read().decode('utf-8'))
print(f"Health Status: {health.get('status')}")
print(f"Phase        : {health.get('phase')}")
print(f"Stages       : {health.get('research_pipeline_stages')}")

# Step 2: Direct Egypt Endpoint Check
eg_resp = urllib.request.urlopen('http://localhost:8000/api/egypt?condition=Asthma&setting=emergency')
eg_data = json.loads(eg_resp.read().decode('utf-8'))
print("\n--- 1. DIRECT EGYPT 6-TRACK ENDPOINT CHECK ---")
print(f"Track A Official Docs Count  : {len(eg_data['track_a_official_guidance']['documents'])}")
print(f"Track B Verified Studies Count: {len(eg_data['track_b_scientific_evidence']['verified_studies'])}")
print(f"Track C Hospital Pathways Count: {len(eg_data['track_c_clinical_practice']['hospital_protocols'])}")
print(f"Track D Regulatory Items Count: {len(eg_data['track_d_regulatory_status'])}")
print(f"Track E Market Products Count : {len(eg_data['track_e_market_and_pricing'])}")

# Step 3: Full Research Call
t0 = time.time()
req_data = json.dumps({'condition': 'Asthma', 'setting': 'emergency'}).encode('utf-8')
req = urllib.request.Request('http://localhost:8000/api/research', data=req_data, headers={'Content-Type': 'application/json'})

print("\nExecuting live Phase 4 /api/research for Asthma (Emergency)...")
resp = urllib.request.urlopen(req, timeout=120)
elapsed = round(time.time() - t0, 2)
result = json.loads(resp.read().decode('utf-8'))

print(f"\nResponse Received: HTTP {resp.status} in {elapsed}s")
print(f"Condition: {result.get('condition_name')}")

pipeline = result.get('pipeline_metadata', {})
print("\n" + "=" * 50)
print("  [A] PIPELINE EXECUTION & STAGES")
print("=" * 50)
print("Stages Completed            :", pipeline.get('stages_completed'))
print("Official Egypt Docs Injected:", pipeline.get('egypt_official_docs'))
print("Verified Egyptian Studies   :", pipeline.get('egypt_verified_studies'))
print("Egyptian Market Medicines   :", pipeline.get('egypt_market_meds'))

eg_rep = result.get('egypt_practice_and_pharmacology', {})

print("\n" + "=" * 50)
print("  [B] TRACK A: OFFICIAL NATIONAL GUIDANCE")
print("=" * 50)
t_a = eg_rep.get('track_a_official_guidance', {})
print("• MOHP & National Guidelines:", t_a.get('national_guidelines_and_mohp'))
print("• Guideline Type            :", t_a.get('guideline_type'))
print("• Confidence Rating         :", t_a.get('confidence'))

print("\n" + "=" * 50)
print("  [C] TRACK B: SCIENTIFIC EVIDENCE & AMR")
print("=" * 50)
t_b = eg_rep.get('track_b_scientific_and_epidemiological_evidence', {})
print("• Local Epidemiology/Cohorts:", t_b.get('local_epidemiology_and_cohorts'))
print("• AMR & Resistance Patterns :", t_b.get('antimicrobial_resistance_and_biomarkers'))
print("• Confidence Rating         :", t_b.get('confidence'))

print("\n" + "=" * 50)
print("  [D] TRACK C: REAL-WORLD CLINICAL PRACTICE & WORKAROUNDS")
print("=" * 50)
t_c = eg_rep.get('track_c_real_world_clinical_practice', {})
print("• Hospital & Clinic Patterns:", t_c.get('hospital_and_clinic_patterns'))
print("• Resource-Limited Workarounds:")
for w in t_c.get('resource_limited_workarounds', []):
    print(f"  - {w}")
print("• Ramadan & Cultural Counseling:", t_c.get('cultural_and_ramadan_counseling'))

print("\n" + "=" * 50)
print("  [E] TRACKS D & E: MEDICATION LANDSCAPE (EDA & MARKET)")
print("=" * 50)
meds = eg_rep.get('track_d_and_e_medication_landscape', [])
for m in meds[:5]:
    print(f"• INN Active Ingredient: {m.get('active_ingredient')}")
    print(f"  Famous Brands         : {', '.join(m.get('famous_egyptian_brands', []))}")
    print(f"  Strengths & Forms     : {m.get('available_strengths_and_forms')}")
    print(f"  EDA Registration      : {m.get('eda_registration_status')}")
    print(f"  Reported Price Range  : {m.get('reported_price_range_egp')}")
    print(f"  Market Availability   : {m.get('market_availability_and_retail_status')}")
    print(f"  Source Category       : {m.get('source_category')}")
    print("-" * 40)

print("\n" + "=" * 50)
print("  [F] TRACK F: LOCAL FORMULATIONS & COMPARISON")
print("=" * 50)
t_f = eg_rep.get('track_f_specialized_egyptian_formulations', {})
print("• Effervescent & Alkalinizers:", t_f.get('effervescent_sachets_and_alkalinizers'))
print("• Standardized Phytotherapy  :", t_f.get('standardized_phytotherapy_and_terpenes'))
print("• Common Prescription Regimens:")
for r in t_f.get('common_egyptian_prescription_formulas', []):
    print(f"  - {r}")

comp = eg_rep.get('egypt_vs_international_comparison', {})
print("\n• Evidence-Supported Adaptations:")
for ea in comp.get('evidence_supported_adaptations', []):
    print(f"  ✅ {ea}")
print("\n• Potentially Outdated / Irrational Practices:")
for op in comp.get('potentially_outdated_or_irrational_practices', []):
    if isinstance(op, dict):
        print(f"  ⚠️ Practice : {op.get('practice')}")
        print(f"     Critique : {op.get('pharmacological_critique')}")
    else:
        print(f"  ⚠️ {op}")

print("\n" + "=" * 80)
print("  PHASE 4 TEST COMPLETE")
print("=" * 80)
