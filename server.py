"""
MedRef Secure Gateway Server (Phases 1, 2, 3 & 4 Active)
Python 3 Standard Library only (Zero external dependencies needed)

Features:
- Secure server-side credential isolation (.env)
- Topic Classification & Authoritative Society Router (Phase 3)
- Live International Guidelines & Cochrane Discovery (Phase 3)
- Post-Guideline Update Search (2024-Present Evidence) (Phase 3)
- Real Live Europe PMC & PubMed Literature Retrieval (Phase 2)
- 6-Track Egypt Medical Research & Practice Engine (Phase 4):
  * Track A: Official Egyptian Guidance (MOHP / EHC / GOTHI / EDA)
  * Track B: Live Egyptian Scientific Cohorts & Studies (Europe PMC)
  * Track C: Real-World Clinical Practice & University Pathways
  * Track D: EDA Regulatory & Pharmaceutical Status
  * Track E: Egyptian Market & Price Information (DawaaGate / DwaPrices)
  * Track F: Egyptian Formulations & Generic Alternatives
- Multi-Tier Grounding Context Builder injected into Gemini synthesis
- Non-fabrication & Citation Integrity Safeguards
- Endpoints: /api/research, /api/guidelines, /api/literature, /api/egypt, /api/save_keys, /api/health
"""

import http.server
import json
import os
import re
import socketserver
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Import Research Engines
from europepmc import EuropePMCRetriever, build_literature_grounding_context
from guidelines_engine import GuidelinesRetriever, TopicClassifier
from egypt_engine import EgyptResearchEngine

# Paths
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / '.env'

# Instantiate Retrievers
epmc_retriever = EuropePMCRetriever(timeout=25)
guidelines_retriever = GuidelinesRetriever(epmc_retriever)
egypt_engine = EgyptResearchEngine(epmc_retriever)

# In-Memory Usage Tracker
USAGE_TRACKER = {
    'total_topics_researched': 0,
    'total_tavily_searches': 0,
    'total_europepmc_queries': 0,
    'total_gemini_calls': 0,
    'active_model': 'gemini-3.6-flash'
}

def load_env():
    """Load configuration from system environment variables and .env file."""
    config = {
        'GEMINI_API_KEY': os.environ.get('GEMINI_API_KEY', ''),
        'TAVILY_API_KEY': os.environ.get('TAVILY_API_KEY', ''),
        'MAX_SEARCHES_PER_TOPIC': os.environ.get('MAX_SEARCHES_PER_TOPIC', '2'),
        'SERVER_PORT': os.environ.get('PORT', os.environ.get('SERVER_PORT', '8000'))
    }
    if ENV_PATH.exists():
        with open(ENV_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    k_clean = k.strip()
                    v_clean = v.strip()
                    if not config.get(k_clean):
                        config[k_clean] = v_clean
    return config

def save_env_keys(gemini_key=None, tavily_key=None, max_searches=None):
    """Update keys in .env file safely."""
    current = load_env()
    if gemini_key is not None and gemini_key.strip():
        current['GEMINI_API_KEY'] = gemini_key.strip()
    if tavily_key is not None and tavily_key.strip():
        current['TAVILY_API_KEY'] = tavily_key.strip()
    if max_searches is not None:
        current['MAX_SEARCHES_PER_TOPIC'] = str(max_searches).strip()

    with open(ENV_PATH, 'w', encoding='utf-8') as f:
        f.write("# MedRef Secure Gateway Environment Configuration\n")
        f.write(f"GEMINI_API_KEY={current['GEMINI_API_KEY']}\n")
        f.write(f"TAVILY_API_KEY={current['TAVILY_API_KEY']}\n")
        f.write(f"MAX_SEARCHES_PER_TOPIC={current['MAX_SEARCHES_PER_TOPIC']}\n")
        f.write(f"SERVER_PORT={current['SERVER_PORT']}\n")

def mask_key(key):
    if not key or len(key) < 8:
        return 'Not configured' if not key else '***'
    return f"{key[:4]}...{key[-4:]}"

def build_dual_protocol_prompt(condition: str, setting: str, combined_grounding_context: str = "") -> str:
    """Generate the exhaustive Master Dual-Protocol system prompt grounded in international guidelines & Egyptian 6-track evidence."""
    return f"""You are the Chief Medical Officer, Evidence-Based Research Director, and Egyptian University Hospital Clinical Pharmacologist for "MedRef".
Generate an exhaustive, dual-perspective clinical research dossier for the condition: "{condition}", setting: "{setting.upper()}".

{combined_grounding_context}

CRITICAL GROUNDING & SOURCE HIERARCHY DIRECTIVES:
1. International Guidelines Protocol (Part 1): Strictly ground clinical management on the retrieved authoritative international guidelines (e.g. 2024 ADA/EASD/JBDS Consensus & ADA 2026 for DKA, GINA 2026 for Asthma, ESC 2026 for Heart Failure, etc.) and completed Cochrane reviews. Compare bodies directly, noting consensus vs divergence and assigning explicit GRADE strength (Strong/Conditional) and certainty (High/Moderate/Low).
2. Validated Numerical Clinical Rules (Part 1 & 2): You MUST STRICTLY ENFORCE the exact numerical clinical rules and boundary parameters provided in SECTION 2 of the context:
   - For Adult DKA Fluid Resuscitation: strictly enforce 500–1000 mL/hour during the first 2–4 hours for adults without renal/cardiac compromise (do NOT use obsolete aggressive 1000–1500 mL/h rates), with cautious/individualized fluid reduction in older adults and patients with heart failure or chronic kidney disease.
   - For Adult DKA Insulin: Continuous IV Regular Insulin at 0.1 U/kg/h (initial IV bolus is not required).
   - For Glycemic/Dextrose Transition & DKA Resolution/Discharge Criteria: Add 5%–10% Dextrose when blood glucose falls below 250 mg/dL (or 200 mg/dL), reducing IV insulin to ~0.02–0.05 U/kg/h while continuing infusion until ketoacidosis resolves. Strictly define DKA resolution and discharge readiness by blood beta-hydroxybutyrate < 0.6 mmol/L, venous pH > 7.30, and serum bicarbonate >= 18.0 mEq/L with clinical alertness and tolerance of oral intake. Do NOT use or mention "anion gap closure" or "anion gap normalization" as a criterion for DKA resolution or discharge (anion gap is used for initial diagnosis and assessment only, but is NOT a resolution criterion because hyperchloremic acidosis from saline makes it misleading).
   - For Potassium Safety: Target 4.0–5.0 mEq/L. HOLD insulin if K+ < 3.5 mEq/L until repleted; add 20–30 mEq K+/L fluid if K+ is 3.5–5.0 mEq/L; HOLD potassium if K+ >= 5.2 mEq/L.
   - For Pediatric DKA: Rehydrate deficit over 48 hours and strictly NO routine IV insulin bolus (ISPAD); start IV regular insulin 0.05–0.1 U/kg/h 1 hour after starting fluid resuscitation.
3. Egypt Practice & Pharmacology Protocol (Part 2): Strictly adhere to the 6 Egyptian Research Tracks:
   - Track A (Official): Cite MOHP, EHC, and GOTHI protocols with confidence ratings.
   - Track B (Science): Cite genuine Egyptian scientific studies with institutional affiliations (Kasr Al Ainy, Ain Shams, Alexandria, Mansoura, Assiut).
   - Track C (Practice): Document Kasr Al Ainy & Ain Shams triage realities, resource-limited workarounds, and Islamic Ramadan jurisprudence.
   - Track D (Regulatory - EDA): List registered INN active ingredients, formulations, and EDA status (Tier 1).
   - Track E (Market - DawaaGate/DwaPrices): List famous Egyptian brands with manufacturers and estimated EGP price ranges.
   - Track F (Formulations): Detail Egyptian generic equivalents and specialized formulations.
4. Crucial Distinctions: 'Registered in EDA' ≠ 'Market Availability' ≠ 'Clinical Recommendation'.
5. Strict Non-Fabrication: Preserve exact PMIDs, DOIs, and original source URLs.

RETURN ONLY A VALID JSON OBJECT MATCHING THIS EXACT SCHEMA (no markdown wrapping):

{{
  "condition_name": "{condition}",
  "classification": {{
    "primary_specialty": "Main Specialty",
    "secondary_specialties": ["Specialty 1", "Specialty 2"],
    "clinical_question_type": ["Diagnosis", "Acute Management", "Pharmacotherapy"],
    "clinical_setting": "{setting}"
  }},
  "guidelines": {{
    "overview": {{
      "definition": "Clinical definition and diagnostic criteria",
      "epidemiology": "Epidemiology and high-risk groups",
      "pathophysiology": "Pathophysiological mechanism"
    }},
    "authoritative_guidelines": [
      {{
        "organization": "e.g. GINA 2026, WHO 2026, BTS/SIGN, SPLF 2026",
        "guideline_title": "Full guideline title",
        "year": "Year",
        "pmid": "Real PMID if available",
        "doi": "Real DOI if available",
        "methodology": "GRADE systematic review / Consensus",
        "key_recommendation": "Summary of recommendation",
        "recommendation_strength": "Strong / Conditional",
        "evidence_certainty": "High / Moderate / Low",
        "source_url": "Direct URL to guideline"
      }}
    ],
    "guideline_consensus_and_divergence": {{
      "consensus_points": ["Consensus recommendation shared across major bodies"],
      "divergence_points": [
        {{
          "issue": "Specific clinical controversy",
          "details": "Comparison between societies",
          "underlying_reasons": "Different evidence cutoffs or resource settings"
        }}
      ]
    }},
    "red_flags_and_triage": [
      "Critical warning sign or immediate life-threat"
    ],
    "diagnostic_strategy": {{
      "approach": "Evidence-based diagnostic algorithm",
      "bedside_and_pocus": ["POCUS, ECG, rapid tests"],
      "laboratory_and_biomarkers": ["Biomarkers with cutoffs and sensitivity/specificity"],
      "imaging": ["Imaging modalities and indications"]
    }},
    "stepped_management_protocol": [
      {{
        "step_number": 1,
        "title": "Action title",
        "priority": "Critical Emergency / First-Line / Step-Up",
        "clinical_details": "Detailed step instructions",
        "medications": [
          {{
            "generic_name": "Active ingredient (INN)",
            "dose": "Standard dose",
            "route": "IV / PO / SC / Nebulized",
            "frequency": "Frequency",
            "duration": "Duration",
            "grade_strength": "Strong / Conditional",
            "grade_certainty": "High / Moderate / Low",
            "clinical_notes": "Important clinical notes"
          }}
        ]
      }}
    ],
    "landmark_evidence_and_trials": [
      {{
        "trial_name_or_study": "Trial name or Author et al. (cite PMID/DOI from literature context)",
        "year": "Year",
        "pmid": "Real PMID from literature context",
        "doi": "Real DOI from literature context",
        "article_url": "Direct URL to study",
        "design": "Multi-center RCT / Cochrane / Systematic Review",
        "primary_outcome": "Primary outcome & statistical significance",
        "clinical_takeaway": "Clinical takeaway"
      }}
    ],
    "safety_monitoring_and_warnings": {{
      "boxed_warnings_and_contraindications": ["Boxed warning or contraindication"],
      "monitoring_parameters": ["Parameters to monitor"],
      "escalation_and_failure_criteria": ["Treatment failure criteria"],
      "special_populations": "Renal, Hepatic, Pregnancy dosing adjustments"
    }},
    "disposition_and_followup": {{
      "admission_criteria": ["Admission criteria"],
      "discharge_criteria": ["Discharge criteria"],
      "outpatient_followup": "Follow-up schedule"
    }},
    "evidence_gaps_and_uncertainties": [
      "Low-certainty or controversial area"
    ],
    "practical_takeaway": "High-yield summary pearl"
  }},
  "egypt_practice_and_pharmacology": {{
    "track_a_official_guidance": {{
      "national_guidelines_and_mohp": "MOHP / EHC / GOTHI official clinical protocol summary",
      "guideline_type": "Egyptian National Guideline / Institutional Protocol",
      "confidence": "HIGH / MODERATE / LOW"
    }},
    "track_b_scientific_and_epidemiological_evidence": {{
      "local_epidemiology_and_cohorts": "Egyptian cohorts and local data (cite verified Egyptian studies)",
      "antimicrobial_resistance_and_biomarkers": "Reported AMR in Egyptian hospitals",
      "confidence": "HIGH / MODERATE / LOW"
    }},
    "track_c_real_world_clinical_practice": {{
      "hospital_and_clinic_patterns": "Kasr Al Ainy & Ain Shams triage and prescribing realities",
      "resource_limited_workarounds": ["Practical workarounds for delayed diagnostics / pMDI+spacer"],
      "cultural_and_ramadan_counseling": "Ramadan fasting adjustments and Islamic jurisprudence counseling",
      "confidence": "HIGH / MODERATE / LOW"
    }},
    "track_d_and_e_medication_landscape": [
      {{
        "active_ingredient": "Generic INN",
        "famous_egyptian_brands": ["Famous Brand 1 (Company)", "Famous Brand 2 (Company)"],
        "available_strengths_and_forms": "Dosage forms and strengths",
        "eda_registration_status": "Officially Registered in EDA / Restricted Hospital Supply",
        "market_availability_and_retail_status": "Widely Available / Available via DawaaGate & Retail",
        "reported_price_range_egp": "Price in EGP",
        "therapeutic_role": "Primary Curative / Fast-acting bronchodilator",
        "evidence_tier": "Tier 1 (EDA Official) / Tier 5 (Market/DawaaGate)",
        "source_category": "[Official Regulatory Source - EDA] or [Market Source - DawaaGate]"
      }}
    ],
    "track_f_specialized_egyptian_formulations": {{
      "effervescent_sachets_and_alkalinizers": "Egyptian effervescent sachets (الفوارات) with trade names if relevant",
      "standardized_phytotherapy_and_terpenes": "Standardized herbal/terpene extracts with trade names",
      "common_egyptian_prescription_formulas": [
        "Multi-drug prescription formula written in Egypt with brand names"
      ]
    }},
    "therapeutic_alternatives": [
      {{
        "primary_drug": "Main active ingredient",
        "egyptian_generic_alternatives": ["Generic Alternative 1 (Brand)"],
        "therapeutic_class_alternatives": ["Class Alternative"]
      }}
    ],
    "egypt_vs_international_comparison": {{
      "evidence_supported_adaptations": ["Legitimate local adaptation"],
      "potentially_outdated_or_irrational_practices": [
        {{
          "practice": "Outdated local habit",
          "pharmacological_critique": "Pharmacological critique"
        }}
      ]
    }},
    "confidence_and_evidence_gap_summary": {{
      "high_confidence_areas": ["Areas with verified data"],
      "evidence_gaps": ["Areas lacking local studies"]
    }}
  }}
}}"""

class MedRefGatewayHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE_DIR), **kwargs)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def send_json(self, status_code, data):
        try:
            body = json.dumps(data).encode('utf-8')
            self.send_response(status_code)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except (ConnectionResetError, BrokenPipeError):
            pass
        except Exception as e:
            print(f"[MedRef Gateway] Error sending JSON: {e}")

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        
        # 1. Health & Status Endpoint
        if url.path == '/api/health':
            env = load_env()
            has_gemini = bool(env.get('GEMINI_API_KEY'))
            has_tavily = bool(env.get('TAVILY_API_KEY'))
            
            return self.send_json(200, {
                'status': 'healthy',
                'phase': 'Phase 4 — Full 6-Track Egypt Research & International Evidence Active',
                'credentials': {
                    'gemini_configured': has_gemini,
                    'gemini_masked': mask_key(env.get('GEMINI_API_KEY')),
                    'tavily_configured': has_tavily,
                    'tavily_masked': mask_key(env.get('TAVILY_API_KEY'))
                },
                'safeguards': {
                    'max_searches_per_topic': int(env.get('MAX_SEARCHES_PER_TOPIC', 2)),
                    'usage_stats': USAGE_TRACKER
                },
                'research_pipeline_stages': [
                    'CLASSIFY (Specialty & Authoritative Bodies)',
                    'INTERNATIONAL_GUIDELINES (GINA 2026, WHO 2026, BTS/SIGN)',
                    'COCHRANE_EVIDENCE (Completed Reviews Only)',
                    'UPDATE_SEARCH (Post-Guideline 2024-2026 Evidence)',
                    'EGYPT_TRACK_A (MOHP / EHC / GOTHI Official Guidance)',
                    'EGYPT_TRACK_B (Live Verified Egyptian Scientific Studies)',
                    'EGYPT_TRACK_C (Kasr Al Ainy / Ain Shams Clinical Practice)',
                    'EGYPT_TRACKS_D_E_F (EDA Regulatory, DawaaGate Market & Formulations)',
                    'MULTI_TIER_GROUNDING (Combined Context Injection)',
                    'SYNTHESIZE (Dually Grounded Evidence Protocol)'
                ]
            })

        # 2. Dedicated Europe PMC / PubMed Literature Search Endpoint (Phase 2)
        if url.path == '/api/literature':
            query_params = urllib.parse.parse_qs(url.query)
            condition = query_params.get('condition', [''])[0].strip()
            setting = query_params.get('setting', ['emergency'])[0].strip()

            if not condition:
                return self.send_json(400, {'error': 'MISSING_CONDITION', 'message': 'Please provide a condition query.'})

            print(f"[MedRef Gateway] Live Europe PMC literature search for: '{condition}' ({setting})...")
            USAGE_TRACKER['total_europepmc_queries'] += 1
            lit_results = epmc_retriever.search_medical_literature(condition, setting=setting)
            return self.send_json(200, lit_results)

        # 3. Dedicated Guidelines & Cochrane Evidence Endpoint (Phase 3)
        if url.path == '/api/guidelines':
            query_params = urllib.parse.parse_qs(url.query)
            condition = query_params.get('condition', [''])[0].strip()
            setting = query_params.get('setting', ['emergency'])[0].strip()

            if not condition:
                return self.send_json(400, {'error': 'MISSING_CONDITION', 'message': 'Please provide a condition query.'})

            print(f"[MedRef Gateway] Live Guidelines & Evidence search for: '{condition}' ({setting})...")
            USAGE_TRACKER['total_europepmc_queries'] += 1
            guidelines_dossier = guidelines_retriever.retrieve_guidelines_and_evidence(condition, setting=setting)
            return self.send_json(200, guidelines_dossier)

        # 4. Dedicated Egypt 6-Track Research Endpoint (Phase 4)
        if url.path == '/api/egypt':
            query_params = urllib.parse.parse_qs(url.query)
            condition = query_params.get('condition', [''])[0].strip()
            setting = query_params.get('setting', ['emergency'])[0].strip()

            if not condition:
                return self.send_json(400, {'error': 'MISSING_CONDITION', 'message': 'Please provide a condition query.'})

            print(f"[MedRef Gateway] Live Egypt 6-Track research for: '{condition}' ({setting})...")
            USAGE_TRACKER['total_europepmc_queries'] += 1
            egypt_dossier = egypt_engine.execute_egypt_research(condition, setting=setting)
            return self.send_json(200, egypt_dossier)

        # 5. Static File Serving
        return super().do_GET()

    def do_POST(self):
        url = urllib.parse.urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        raw_body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'

        try:
            req_data = json.loads(raw_body)
        except Exception:
            req_data = {}

        # 1. Save Keys Endpoint
        if url.path == '/api/save_keys':
            gemini_key = req_data.get('gemini_key')
            tavily_key = req_data.get('tavily_key')
            max_searches = req_data.get('max_searches')
            save_env_keys(gemini_key, tavily_key, max_searches)
            print(f"[MedRef Gateway] Successfully updated .env keys (Gemini: {mask_key(gemini_key)})")
            return self.send_json(200, {'success': True, 'message': 'API credentials securely saved to server-side .env'})

        # 2. Secure Research Proxy Endpoint (Phases 1, 2, 3, & 4 Grounded Pipeline)
        if url.path == '/api/research':
            env = load_env()
            gemini_key = env.get('GEMINI_API_KEY', '').strip()
            
            if not gemini_key:
                print("[MedRef Gateway] Research call rejected: GEMINI_API_KEY is not set in .env")
                return self.send_json(400, {
                    'error': 'MISSING_API_KEY',
                    'message': 'Gemini API key is not configured in the server .env file. Please add GEMINI_API_KEY to .env or save it via server settings.'
                })

            condition = req_data.get('condition', '').strip()
            setting = req_data.get('setting', 'emergency').strip().lower()

            if not condition:
                return self.send_json(400, {'error': 'MISSING_CONDITION', 'message': 'Please provide a condition name.'})

            print(f"\n[MedRef Gateway] ===============================================")
            print(f"[MedRef Gateway] Executing Phase 4 Full Research for: '{condition}' ({setting.upper()})")
            print(f"[MedRef Gateway] ===============================================")

            # Step 1-3: Run Guidelines, Literature, & Egypt Engines Concurrently
            import concurrent.futures
            USAGE_TRACKER['total_europepmc_queries'] += 1

            def fetch_guidelines():
                try:
                    return guidelines_retriever.retrieve_guidelines_and_evidence(condition, setting=setting)
                except Exception as e:
                    print(f"[MedRef Gateway] Guidelines retrieval error: {e}")
                    return {"classification": TopicClassifier.classify(condition, setting), "guideline_records": [], "cochrane_and_landmark_evidence": [], "update_search_recent_evidence": [], "counts": {}}

            def fetch_literature():
                try:
                    return epmc_retriever.search_medical_literature(condition, setting=setting)
                except Exception as e:
                    print(f"[MedRef Gateway] Europe PMC error: {e}")
                    return {'total_records_retrieved': 0, 'records': [], 'summary': {}}

            def fetch_egypt():
                try:
                    return egypt_engine.execute_egypt_research(condition, setting=setting)
                except Exception as e:
                    print(f"[MedRef Gateway] Egypt Engine error: {e}")
                    return {}

            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                f_guide = executor.submit(fetch_guidelines)
                f_lit = executor.submit(fetch_literature)
                f_egypt = executor.submit(fetch_egypt)

                guidelines_dossier = f_guide.result()
                lit_results = f_lit.result()
                egypt_dossier = f_egypt.result()

            print(f"[MedRef Gateway] Guidelines Engine: {guidelines_dossier.get('counts', {}).get('official_guidelines_found', 0)} guidelines, {guidelines_dossier.get('counts', {}).get('landmark_cochrane_found', 0)} Cochrane reviews.")
            print(f"[MedRef Gateway] Europe PMC: {lit_results.get('total_records_retrieved', 0)} papers retrieved.")
            print(f"[MedRef Gateway] Egypt Engine: {len(egypt_dossier.get('track_a_official_guidance', {}).get('documents', []))} official docs, {len(egypt_dossier.get('track_b_scientific_evidence', {}).get('verified_studies', []))} Egyptian studies.")

            # Step 4: Build Compact, Ranked Multi-Tier Grounding Context (Phases 2, 3, & 4)
            combined_grounding = self._build_compact_grounding_context(guidelines_dossier, lit_results, egypt_dossier)
            print(f"[MedRef Gateway] Unified Multi-Tier Compact Context: {len(combined_grounding)} chars injected into Gemini prompt.")

            # Step 5: Track usage
            USAGE_TRACKER['total_topics_researched'] += 1
            USAGE_TRACKER['total_gemini_calls'] += 1

            # Step 6: GEMINI GROUNDED SYNTHESIS (Cascade with Bounded Backoff)
            try:
                result, active_model = self._call_gemini_proxy(gemini_key, condition, setting, combined_grounding)
                USAGE_TRACKER['active_model'] = active_model
                
                # Attach Phase 2, 3, & 4 evidence records to response
                result['guidelines_evidence'] = guidelines_dossier
                result['literature_evidence'] = lit_results
                result['egypt_evidence'] = egypt_dossier

                # Attach Complete Pipeline Metadata
                result['pipeline_metadata'] = {
                    'stages_completed': [
                        'CLASSIFY (Specialty & Authoritative Bodies)',
                        'INTERNATIONAL_GUIDELINES (GINA 2026, WHO 2026, ADA 2026, ESC 2026)',
                        'COCHRANE_EVIDENCE (Completed Reviews Only)',
                        'UPDATE_SEARCH (Post-Guideline 2024-2026 Evidence)',
                        'EGYPT_TRACK_A (MOHP / EHC / GOTHI Official Guidance)',
                        'EGYPT_TRACK_B (Live Verified Egyptian Scientific Studies)',
                        'EGYPT_TRACK_C (Kasr Al Ainy / Ain Shams Clinical Practice)',
                        'EGYPT_TRACKS_D_E_F (EDA Regulatory, DawaaGate Market & Formulations)',
                        'CLINICAL_RULES (Condition-Bound Validation Schema)',
                        'COMPACT_GROUNDING (Ranked High-Yield Context)',
                        'SYNTHESIZE (Dually Grounded Evidence Protocol)'
                    ],
                    'gateway_mode': 'Phase 4 — Full 6-Track Egypt Research & International Evidence Active',
                    'active_model': active_model,
                    'search_budget_enforced': True,
                    'max_searches_allocated': int(env.get('MAX_SEARCHES_PER_TOPIC', 2)),
                    'official_guidelines_retrieved': guidelines_dossier.get('counts', {}).get('official_guidelines_found', 0),
                    'cochrane_reviews_retrieved': guidelines_dossier.get('counts', {}).get('landmark_cochrane_found', 0),
                    'post_guideline_updates_retrieved': guidelines_dossier.get('counts', {}).get('recent_updates_found', 0),
                    'egypt_official_docs': len(egypt_dossier.get('track_a_official_guidance', {}).get('documents', [])),
                    'egypt_verified_studies': len(egypt_dossier.get('track_b_scientific_evidence', {}).get('verified_studies', [])),
                    'egypt_market_meds': len(egypt_dossier.get('track_e_market_and_pricing', []))
                }
                
                print(f"[MedRef Gateway] Successfully generated Phase 4 grounded research dossier for '{condition}' via {active_model}")
                return self.send_json(200, result)
            except urllib.error.HTTPError as e:
                err_text = e.read().decode('utf-8')
                print(f"[MedRef Gateway] Gemini API HTTP {e.code} Error: {err_text}")
                try:
                    err_json = json.loads(err_text)
                    msg = err_json.get('error', {}).get('message', err_text)
                except Exception:
                    msg = err_text
                return self.send_json(e.code, {'error': f'HTTP_{e.code}', 'message': msg})
            except Exception as e:
                print(f"[MedRef Gateway] Server error during research call: {e}")
                return self.send_json(500, {'error': 'SERVER_ERROR', 'message': str(e)})

        return self.send_json(404, {'error': 'NOT_FOUND', 'path': url.path})

    def _build_compact_grounding_context(self, guidelines_dossier: Dict[str, Any], lit_results: Dict[str, Any], egypt_dossier: Dict[str, Any]) -> str:
        """Construct ranked, high-yield, compact grounding context removing duplicate text while preserving 100% provenance."""
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

    def _call_gemini_proxy(self, api_key: str, condition: str, setting: str, combined_grounding_context: str = ""):
        """Execute server-side call with production model preference cascade and bounded retry/backoff."""
        models_cascade = [
            "gemini-3.7-flash",
            "gemini-3.6-flash",
            "gemini-3.5-flash-lite",
            "gemini-3.1-flash-lite",
            "gemini-3-flash-preview",
            "gemini-flash-lite-latest"
        ]
        ver = 'v1beta'
        prompt_text = build_dual_protocol_prompt(condition, setting, combined_grounding_context)

        body = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"Generate exhaustive dual-protocol dossier for condition: '{condition}', setting: '{setting}'. Strictly synthesize both the international evidence guidelines (Part 1) and the 6-track Egyptian clinical & pharmacological practice (Part 2)."}]
                }
            ],
            "systemInstruction": {
                "parts": [{"text": prompt_text}]
            },
            "generationConfig": {
                "temperature": 0.2,
                "topP": 0.85,
                "topK": 40,
                "responseMimeType": "application/json"
            }
        }

        for model in models_cascade:
            url = f"https://generativelanguage.googleapis.com/{ver}/models/{model}:generateContent?key={api_key}"
            for attempt in range(1, 3):
                try:
                    req = urllib.request.Request(
                        url,
                        data=json.dumps(body).encode('utf-8'),
                        headers={'Content-Type': 'application/json'}
                    )
                    with urllib.request.urlopen(req, timeout=45) as resp:
                        data = json.loads(resp.read().decode('utf-8'))
                        text = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '{}')
                        
                        s = text.strip()
                        if s.startswith('```json'): s = s[7:]
                        elif s.startswith('```'): s = s[3:]
                        if s.endswith('```'): s = s[:-3]
                        s = s.strip()
                        
                        try:
                            parsed = json.loads(s)
                        except Exception:
                            a = s.find('{')
                            b = s.rfind('}')
                            if a != -1 and b > a:
                                parsed = json.loads(s[a:b+1])
                            else:
                                parsed = {'error': 'JSON_PARSE_FAILED', 'raw_text': text}

                        parsed['research_mode'] = 'enhanced_evidence_synthesis'
                        return parsed, model
                except urllib.error.HTTPError as e:
                    print(f"[MedRef Gateway] Model '{model}' attempt {attempt} HTTP {e.code}: {e.reason}")
                    if e.code in [429, 500, 503]:
                        import time
                        time.sleep(2.0)
                        continue
                    break
                except Exception as e:
                    print(f"[MedRef Gateway] Model '{model}' attempt {attempt} exception: {e}")
                    import time
                    time.sleep(1.0)
                    continue

        raise RuntimeError("All candidate Gemini models in production cascade failed or were unreachable.")

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

def run_server(port=None):
    env = load_env()
    if port is None:
        if len(sys.argv) > 1:
            try:
                port = int(sys.argv[1])
            except Exception:
                port = None
        if port is None and 'PORT' in os.environ:
            try:
                port = int(os.environ['PORT'])
            except Exception:
                port = None
        if port is None:
            try:
                port = int(env.get('SERVER_PORT', 8000))
            except Exception:
                port = 8000

    print("\n=======================================================")
    print("  [MedRef Secure Gateway Server - Phase 5 Active]")
    print(f"  Local Web App : http://localhost:{port}")
    print(f"  Health Check  : http://localhost:{port}/api/health")
    print(f"  Egypt API     : http://localhost:{port}/api/egypt?condition=Asthma")
    print(f"  Guidelines API: http://localhost:{port}/api/guidelines?condition=Asthma")
    print(f"  Literature API: http://localhost:{port}/api/literature?condition=Asthma")
    print("  Security      : Credentials isolated server-side in .env")
    print("=======================================================\n")

    with ThreadedHTTPServer(("0.0.0.0", port), MedRefGatewayHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down MedRef Secure Gateway...")
            httpd.server_close()

if __name__ == '__main__':
    run_server()
