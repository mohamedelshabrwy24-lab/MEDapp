import time
import urllib.request
import urllib.parse
import json
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("  REAL END-TO-END MEASUREMENT: DKA (EMERGENCY)")
print("=" * 80)

# Load API key
env_path = Path("C:/Users/Bakot/.gemini/antigravity/scratch/medref/.env")
api_key = ""
with open(env_path, 'r', encoding='utf-8') as f:
    for line in f:
        if line.startswith("GEMINI_API_KEY="):
            api_key = line.split("=", 1)[1].strip()

condition = "DKA"
setting = "emergency"

from europepmc import EuropePMCRetriever, build_literature_grounding_context
from guidelines_engine import GuidelinesRetriever, TopicClassifier
from egypt_engine import EgyptResearchEngine
from clinical_rules import ClinicalRuleValidator

# Step 1: Retrieval
t_start_total = time.time()
t0 = time.time()
epmc_retriever = EuropePMCRetriever(timeout=20)
guidelines_retriever = GuidelinesRetriever(epmc_retriever)
egypt_engine = EgyptResearchEngine(epmc_retriever)

clf = TopicClassifier.classify(condition, setting)
guidelines_dossier = guidelines_retriever.retrieve_guidelines_and_evidence(condition, setting)
lit_results = epmc_retriever.search_medical_literature(condition, setting=setting)
egypt_dossier = egypt_engine.execute_egypt_research(condition, setting)
t_retrieval = time.time() - t0
print(f"1. Retrieval Time            : {t_retrieval:.2f}s")

# Step 2: Compact High-Yield Context Assembly
t0 = time.time()

def build_compact_grounding_context(guidelines_dossier, lit_results, egypt_dossier) -> str:
    lines = []
    
    # 1. Authoritative International Guidelines & Landmarks
    lines.append("=== SECTION 1: INTERNATIONAL GUIDELINES & HIGHEST EVIDENCE ===")
    for g in guidelines_dossier.get("guideline_records", [])[:5]:
        lines.append(f"• [{g.get('status', 'Current')}] {g.get('organization')} ({g.get('year')}): {g.get('title')}")
        lines.append(f"  Scope: {g.get('scope')} | URL: {g.get('source_url')}")
        if g.get("pmid"): lines.append(f"  PMID: {g.get('pmid')} | DOI: {g.get('doi')}")
    
    for c in guidelines_dossier.get("cochrane_and_landmark_evidence", [])[:3]:
        lines.append(f"• [Cochrane Systematic Review] {c.get('title')} ({c.get('year')})")
        lines.append(f"  PMID: {c.get('pmid')} | DOI: {c.get('doi')} | URL: {c.get('article_url')}")
    
    for u in guidelines_dossier.get("update_search_recent_evidence", [])[:3]:
        lines.append(f"• [Post-Guideline Update] {u.get('title')} ({u.get('year')})")
        lines.append(f"  PMID: {u.get('pmid')} | DOI: {u.get('doi')} | URL: {u.get('article_url')}")

    # 2. Validated Condition-Bound Clinical Numerical Rules
    val_rules = egypt_dossier.get("validated_clinical_rules", [])
    if val_rules:
        lines.append("\n=== SECTION 2: VALIDATED CLINICAL NUMERICAL RULES & BOUNDARIES ===")
        for r in val_rules:
            lines.append(f"• [{r.get('population')} | {r.get('severity_context')}] {r.get('rule_summary')}")
            lines.append(f"  Source: {r.get('guideline_source')} ({r.get('version_year')})")
            lines.append(f"  Parameters: {r.get('numerical_parameters')}")
            lines.append(f"  Qualifications: {'; '.join(r.get('conditional_qualifications', []))}")
            lines.append(f"  Contraindications: {'; '.join(r.get('contraindications', []))}")

    # 3. Egypt 6-Track Evidence
    lines.append("\n=== SECTION 3: EGYPT-SPECIFIC MEDICAL & PHARMACOLOGICAL EVIDENCE ===")
    t_a = egypt_dossier.get("track_a_official_guidance", {})
    for doc in t_a.get("documents", []):
        lines.append(f"• [Track A Official] {doc.get('issuing_organization')}: {doc.get('exact_title')} ({doc.get('source_url')})")
    
    t_b = egypt_dossier.get("track_b_scientific_evidence", {})
    for st in t_b.get("verified_studies", [])[:4]:
        lines.append(f"• [Track B Egyptian Study] PMID {st.get('verified_pmid')}: {st.get('verified_title')} ({st.get('journal')}, {st.get('pub_year')})")
        lines.append(f"  Affiliation: {st.get('egypt_relevance')} | DOI: {st.get('verified_doi')}")
    
    t_c = egypt_dossier.get("track_c_clinical_practice", {})
    lines.append(f"• [Track C Practice & Ramadan]: {t_c.get('cultural_and_ramadan_counseling')}")
    for w in t_c.get("resource_limited_workarounds", []):
        lines.append(f"  Workaround: {w}")

    t_e = egypt_dossier.get("track_e_market_and_pricing", [])
    lines.append("• [Tracks D & E Egyptian Medications]:")
    for m in t_e[:6]:
        lines.append(f"  - INN: {m.get('active_ingredient')} | Brand: {m.get('brand_name')} ({m.get('manufacturer')}) | Form: {m.get('strength_and_form')}")
        lines.append(f"    EDA: {m.get('eda_source')} | Price: {m.get('price')} ({m.get('price_date')}) | Clinical Scope: {m.get('clinical_scope')}")

    return "\n".join(lines)

compact_grounding = build_compact_grounding_context(guidelines_dossier, lit_results, egypt_dossier)
t_context = time.time() - t0
print(f"2. Context Assembly Time    : {t_context:.3f}s (Compact Size: {len(compact_grounding)} chars)")

# Step 3: Synthesis with robust backoff
t0 = time.time()

def call_gemini_production(api_key: str, condition: str, setting: str, grounding_text: str):
    models = ["gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash"]
    
    prompt = f"""You are the Chief Medical Officer and Egyptian University Hospital Clinical Pharmacologist for "MedRef".
Synthesize an authoritative, dually-grounded clinical research dossier for: "{condition}", setting: "{setting.upper()}".

{grounding_text}

MANDATORY RULES:
1. Part 1 (International Guidelines): Strictly ground management on current guidelines (ADA 2026 / ISPAD 2024/2026 / UK JBDS-IP 2024). Include exact numerical fluid rates, insulin rates, potassium thresholds, and cerebral edema safety rules from Section 2.
2. Part 2 (Egypt Practice & Pharmacology): Include MOHP/EHC guidance, verified Egyptian studies (cite exact PMIDs/DOIs), Kasr Al Ainy workarounds, and Egyptian trade brands (Actrapid, Humulin R, Otsuka Saline, CID KCl) with EDA status and EGP prices.
3. Strict Provenance: Preserve real PMIDs, DOIs, and URLs.

Return ONLY a valid JSON matching this schema:
{{
  "condition_name": "{condition}",
  "classification": {{"primary_specialty": "Endocrinology, Diabetes & Metabolism", "clinical_setting": "{setting}"}},
  "guidelines": {{
    "overview": {{"definition": "...", "epidemiology": "...", "pathophysiology": "..."}},
    "authoritative_guidelines": [
      {{"organization": "...", "guideline_title": "...", "year": "2026", "pmid": "...", "doi": "...", "methodology": "GRADE", "key_recommendation": "...", "recommendation_strength": "Strong", "evidence_certainty": "High", "source_url": "..."}}
    ],
    "guideline_consensus_and_divergence": {{"consensus_points": ["..."], "divergence_points": [{{"issue": "...", "details": "...", "underlying_reasons": "..."}}]}},
    "red_flags_and_triage": ["..."],
    "diagnostic_strategy": {{"approach": "...", "bedside_and_pocus": ["..."], "laboratory_and_biomarkers": ["..."], "imaging": ["..."]}},
    "stepped_management_protocol": [
      {{"step_number": 1, "title": "...", "priority": "Critical Emergency", "clinical_details": "...", "medications": [{{"generic_name": "...", "dose": "...", "route": "...", "frequency": "...", "duration": "...", "grade_strength": "Strong", "grade_certainty": "High", "clinical_notes": "..."}}]}}
    ],
    "landmark_evidence_and_trials": [
      {{"trial_name_or_study": "...", "year": "...", "pmid": "...", "doi": "...", "article_url": "...", "design": "...", "primary_outcome": "...", "clinical_takeaway": "..."}}
    ],
    "safety_monitoring_and_warnings": {{"boxed_warnings_and_contraindications": ["..."], "monitoring_parameters": ["..."], "escalation_and_failure_criteria": ["..."], "special_populations": "..."}},
    "disposition_and_followup": {{"admission_criteria": ["..."], "discharge_criteria": ["..."], "outpatient_followup": "..."}},
    "evidence_gaps_and_uncertainties": ["..."],
    "practical_takeaway": "..."
  }},
  "egypt_practice_and_pharmacology": {{
    "track_a_official_guidance": {{"national_guidelines_and_mohp": "...", "guideline_type": "Egyptian National Protocol", "confidence": "HIGH"}},
    "track_b_scientific_and_epidemiological_evidence": {{"local_epidemiology_and_cohorts": "...", "antimicrobial_resistance_and_biomarkers": "...", "confidence": "HIGH"}},
    "track_c_real_world_clinical_practice": {{"hospital_and_clinic_patterns": "...", "resource_limited_workarounds": ["..."], "cultural_and_ramadan_counseling": "...", "confidence": "HIGH"}},
    "track_d_and_e_medication_landscape": [
      {{"active_ingredient": "...", "famous_egyptian_brands": ["..."], "available_strengths_and_forms": "...", "eda_registration_status": "...", "market_availability_and_retail_status": "...", "reported_price_range_egp": "...", "therapeutic_role": "...", "evidence_tier": "Tier 1 (EDA) / Tier 5 (Market)", "source_category": "Official / Market"}}
    ],
    "track_f_specialized_egyptian_formulations": {{"effervescent_sachets_and_alkalinizers": "...", "standardized_phytotherapy_and_terpenes": "...", "common_egyptian_prescription_formulas": ["..."]}},
    "therapeutic_alternatives": [
      {{"active_ingredient": "...", "brand_egypt": "...", "company": "...", "route": "...", "relative_cost": "...", "clinical_niche": "..."}}
    ]
  }}
}}"""

    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        body = {
            "contents": [{"role": "user", "parts": [{"text": f"Generate full dual-protocol JSON for '{condition}' ({setting})."}]}],
            "systemInstruction": {"parts": [{"text": prompt}]},
            "generationConfig": {
                "temperature": 0.2,
                "topP": 0.85,
                "topK": 40,
                "responseMimeType": "application/json"
            }
        }
        
        for attempt in range(1, 3):
            try:
                print(f"  • Invoking model '{model}' (Attempt {attempt})...")
                req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), headers={'Content-Type': 'application/json'})
                with urllib.request.urlopen(req, timeout=35) as resp:
                    raw_data = json.loads(resp.read().decode('utf-8'))
                    text = raw_data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '{}')
                    s = text.strip()
                    if s.startswith('```json'): s = s[7:]
                    elif s.startswith('```'): s = s[3:]
                    if s.endswith('```'): s = s[:-3]
                    parsed = json.loads(s.strip())
                    return parsed, model
            except urllib.error.HTTPError as e:
                print(f"    -> {model} HTTP {e.code}: {e.reason}")
                if e.code in [429, 500, 503]:
                    time.sleep(5.0) # 5 second cooldown for rate-limiting
                    continue
                break
            except Exception as e:
                print(f"    -> {model} exception: {e}")
                time.sleep(2.0)
                continue
    raise RuntimeError("All models failed in cascade.")

res_json, active_model = call_gemini_production(api_key, condition, setting, compact_grounding)
t_gemini = time.time() - t0
t_total = time.time() - t_start_total

print(f"3. Gemini Request Time       : {t_gemini:.2f}s (Served by: {active_model})")
print(f"4. Total Request Time        : {t_total:.2f}s")
print(f"5. Final Response Status     : HTTP 200 OK (Completed JSON: {len(json.dumps(res_json))} chars)")

# Verification of output
print("\n" + "=" * 80)
print("  VERIFICATION OF GENERATED CLINICAL DOSSIER")
print("=" * 80)
print(f"• Condition: {res_json.get('condition_name')}")
print(f"• Guidelines Listed: {len(res_json.get('guidelines', {}).get('authoritative_guidelines', []))}")
for g in res_json.get('guidelines', {}).get('authoritative_guidelines', [])[:3]:
    print(f"  - {g.get('organization')}: {g.get('guideline_title')} ({g.get('year')})")
print(f"• Management Steps: {len(res_json.get('guidelines', {}).get('stepped_management_protocol', []))} steps")
for step in res_json.get('guidelines', {}).get('stepped_management_protocol', [])[:3]:
    print(f"  Step {step.get('step_number')}: {step.get('title')} ({step.get('priority')})")
    print(f"    Details: {step.get('clinical_details')[:85]}...")
print(f"• Egyptian Medication Landscape ({len(res_json.get('egypt_practice_and_pharmacology', {}).get('track_d_and_e_medication_landscape', []))} products):")
for m in res_json.get('egypt_practice_and_pharmacology', {}).get('track_d_and_e_medication_landscape', [])[:4]:
    print(f"  - {m.get('active_ingredient')}: {m.get('famous_egyptian_brands')} | Price: {m.get('reported_price_range_egp')}")
print(f"• Ramadan Counseling: {res_json.get('egypt_practice_and_pharmacology', {}).get('track_c_real_world_clinical_practice', {}).get('cultural_and_ramadan_counseling')[:80]}...")
print("=" * 80)
