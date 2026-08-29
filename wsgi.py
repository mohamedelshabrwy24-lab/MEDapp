"""
MedRef Cloud WSGI Application — Self-contained for Render/Gunicorn.
No dependency on MedRefGatewayHandler class methods.
"""
import os
import sys
import json
import time
import urllib.parse
import urllib.request
import urllib.error
import traceback
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# ─── Helpers ────────────────────────────────────────────────────────

MIME_TYPES = {
    '.html': 'text/html; charset=utf-8',
    '.css': 'text/css; charset=utf-8',
    '.js': 'application/javascript; charset=utf-8',
    '.json': 'application/json; charset=utf-8',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.svg': 'image/svg+xml',
    '.ico': 'image/x-icon',
}

def get_gemini_key():
    """Read GEMINI_API_KEY from environment (Render injects it)."""
    return os.environ.get('GEMINI_API_KEY', '').strip()

def mask_key(key):
    if not key or len(key) < 8:
        return 'Not configured' if not key else '***'
    return f"{key[:4]}...{key[-4:]}"

def call_gemini(api_key, condition, setting):
    """Call Gemini API directly — simple, reliable, no research engines."""
    models = [
        "gemini-3.6-flash",
        "gemini-3.5-flash-lite",
        "gemini-3.1-flash-lite",
        "gemini-flash-lite-latest",
    ]

    system_prompt = f"""You are the Chief Medical Officer for "MedRef — Universal Medical Reference".
Generate an exhaustive clinical dossier for: "{condition}", setting: "{setting.upper()}".

Cover TWO sections:
1. INTERNATIONAL EVIDENCE-BASED GUIDELINES — authoritative society guidelines (ADA, ESC, GINA, WHO, BTS/SIGN, etc.), diagnostic criteria, stepped management with medications (generic INN names, doses, routes, GRADE strength), landmark trials, monitoring, disposition.
2. EGYPTIAN CLINICAL PRACTICE & PHARMACOLOGY — MOHP/EHC/GOTHI guidance, Egyptian university hospital practices (Kasr Al Ainy, Ain Shams), EDA-registered drugs, famous Egyptian brands with manufacturer and EGP price ranges, generic alternatives, local prescribing patterns, Ramadan counseling if relevant.

IMPORTANT RULES:
- Use ONLY generic drug names (INN active ingredients), never brand names in Part 1.
- In Part 2, include famous Egyptian brand names with their manufacturers.
- All medications must include: dose, route, frequency, duration.
- Include real PMIDs/DOIs where possible.
- For DKA: use 500-1000 mL/h fluid (NOT 1000-1500), insulin 0.1 U/kg/h IV, do NOT use anion gap for resolution criteria.
- Adapt response to setting: emergency = acute management focus, outpatient = chronic management and follow-up.

RETURN ONLY VALID JSON matching this schema (no markdown wrapping):

{{
  "condition_name": "{condition}",
  "classification": {{
    "primary_specialty": "Main Specialty",
    "secondary_specialties": ["Specialty 1"],
    "clinical_question_type": ["Diagnosis", "Acute Management"],
    "clinical_setting": "{setting}"
  }},
  "guidelines": {{
    "overview": {{
      "definition": "Clinical definition",
      "epidemiology": "Epidemiology",
      "pathophysiology": "Pathophysiology"
    }},
    "authoritative_guidelines": [
      {{
        "organization": "e.g. GINA 2026",
        "guideline_title": "Full title",
        "year": "Year",
        "pmid": "PMID if available",
        "doi": "DOI if available",
        "key_recommendation": "Summary",
        "recommendation_strength": "Strong / Conditional",
        "evidence_certainty": "High / Moderate / Low",
        "source_url": "URL"
      }}
    ],
    "guideline_consensus_and_divergence": {{
      "consensus_points": ["Consensus"],
      "divergence_points": [{{
        "issue": "Issue",
        "details": "Details"
      }}]
    }},
    "red_flags_and_triage": ["Red flag"],
    "diagnostic_strategy": {{
      "approach": "Diagnostic algorithm",
      "bedside_and_pocus": ["Tests"],
      "laboratory_and_biomarkers": ["Labs"],
      "imaging": ["Imaging"]
    }},
    "stepped_management_protocol": [
      {{
        "step_number": 1,
        "title": "Step title",
        "priority": "Critical Emergency / First-Line",
        "clinical_details": "Details",
        "medications": [
          {{
            "generic_name": "INN name",
            "dose": "Dose",
            "route": "Route",
            "frequency": "Frequency",
            "duration": "Duration",
            "grade_strength": "Strong / Conditional",
            "clinical_notes": "Notes"
          }}
        ]
      }}
    ],
    "landmark_evidence_and_trials": [
      {{
        "trial_name_or_study": "Name",
        "year": "Year",
        "pmid": "PMID",
        "design": "RCT / Systematic Review",
        "primary_outcome": "Outcome",
        "clinical_takeaway": "Takeaway"
      }}
    ],
    "safety_monitoring_and_warnings": {{
      "boxed_warnings_and_contraindications": ["Warning"],
      "monitoring_parameters": ["Parameters"],
      "escalation_and_failure_criteria": ["Criteria"],
      "special_populations": "Adjustments"
    }},
    "disposition_and_followup": {{
      "admission_criteria": ["Criteria"],
      "discharge_criteria": ["Criteria"],
      "outpatient_followup": "Schedule"
    }},
    "evidence_gaps_and_uncertainties": ["Gap"],
    "practical_takeaway": "Summary pearl"
  }},
  "egypt_practice_and_pharmacology": {{
    "track_a_official_guidance": {{
      "national_guidelines_and_mohp": "MOHP protocol summary",
      "guideline_type": "Egyptian National Guideline",
      "confidence": "HIGH / MODERATE / LOW"
    }},
    "track_b_scientific_and_epidemiological_evidence": {{
      "local_epidemiology_and_cohorts": "Egyptian data",
      "confidence": "MODERATE"
    }},
    "track_c_real_world_clinical_practice": {{
      "hospital_and_clinic_patterns": "Practice patterns",
      "resource_limited_workarounds": ["Workarounds"],
      "cultural_and_ramadan_counseling": "Counseling",
      "confidence": "MODERATE"
    }},
    "track_d_and_e_medication_landscape": [
      {{
        "active_ingredient": "INN",
        "famous_egyptian_brands": ["Brand (Company)"],
        "available_strengths_and_forms": "Forms",
        "eda_registration_status": "Registered",
        "reported_price_range_egp": "Price EGP",
        "therapeutic_role": "Role",
        "evidence_tier": "Tier 1"
      }}
    ],
    "track_f_specialized_egyptian_formulations": {{
      "common_egyptian_prescription_formulas": ["Formula"]
    }},
    "therapeutic_alternatives": [
      {{
        "primary_drug": "Drug",
        "egyptian_generic_alternatives": ["Alternative"]
      }}
    ],
    "egypt_vs_international_comparison": {{
      "evidence_supported_adaptations": ["Adaptation"],
      "potentially_outdated_or_irrational_practices": [{{
        "practice": "Practice",
        "pharmacological_critique": "Critique"
      }}]
    }}
  }}
}}"""

    body = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": f"Generate exhaustive dual-protocol clinical dossier for: '{condition}', setting: '{setting}'."}]
            }
        ],
        "systemInstruction": {
            "parts": [{"text": system_prompt}]
        },
        "generationConfig": {
            "temperature": 0.2,
            "topP": 0.85,
            "topK": 40,
            "responseMimeType": "application/json"
        }
    }

    last_error = None
    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        for attempt in range(2):
            try:
                req = urllib.request.Request(
                    url,
                    data=json.dumps(body).encode('utf-8'),
                    headers={'Content-Type': 'application/json'}
                )
                with urllib.request.urlopen(req, timeout=60) as resp:
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
                            parsed = {'error': 'JSON_PARSE_FAILED', 'raw': text[:500]}

                    parsed['research_mode'] = 'cloud_direct'
                    parsed['active_model'] = model
                    return parsed

            except urllib.error.HTTPError as e:
                last_error = f"Model {model} HTTP {e.code}"
                print(f"[WSGI] {last_error}: {e.reason}", flush=True)
                if e.code in [429, 500, 503]:
                    time.sleep(2)
                    continue
                break
            except Exception as e:
                last_error = f"Model {model}: {e}"
                print(f"[WSGI] {last_error}", flush=True)
                time.sleep(1)
                continue

    raise RuntimeError(f"All Gemini models failed. Last error: {last_error}")

# ─── WSGI Application ──────────────────────────────────────────────

def application(environ, start_response):
    path = environ.get('PATH_INFO', '/')
    method = environ.get('REQUEST_METHOD', 'GET').upper()

    # CORS preflight
    if method == 'OPTIONS':
        start_response('200 OK', [
            ('Access-Control-Allow-Origin', '*'),
            ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'),
            ('Access-Control-Allow-Headers', 'Content-Type'),
        ])
        return [b'']

    # ── Health Check ──
    if path == '/api/health':
        key = get_gemini_key()
        data = {
            'status': 'healthy',
            'runtime': 'cloud_wsgi',
            'credentials': {
                'gemini_configured': bool(key),
                'gemini_masked': mask_key(key),
            },
        }
        body = json.dumps(data).encode('utf-8')
        start_response('200 OK', [
            ('Content-Type', 'application/json'),
            ('Access-Control-Allow-Origin', '*'),
        ])
        return [body]

    # ── Save Keys (cloud: keys are in Render env vars, not .env file) ──
    if path == '/api/save_keys' and method == 'POST':
        key = get_gemini_key()
        if key:
            body = json.dumps({'status': 'ok', 'message': 'API key is already configured via server environment variables.'}).encode('utf-8')
            start_response('200 OK', [('Content-Type', 'application/json'), ('Access-Control-Allow-Origin', '*')])
        else:
            body = json.dumps({'status': 'error', 'message': 'Please set GEMINI_API_KEY in Render Dashboard > Environment.'}).encode('utf-8')
            start_response('400 Bad Request', [('Content-Type', 'application/json'), ('Access-Control-Allow-Origin', '*')])
        return [body]

    # ── Research API ──
    if path == '/api/research' and method == 'POST':
        api_key = get_gemini_key()

        if not api_key:
            err = json.dumps({'error': 'MISSING_API_KEY', 'message': 'GEMINI_API_KEY is not configured on the server.'}).encode('utf-8')
            start_response('400 Bad Request', [('Content-Type', 'application/json'), ('Access-Control-Allow-Origin', '*')])
            return [err]

        try:
            length = int(environ.get('CONTENT_LENGTH', 0))
            raw = environ['wsgi.input'].read(length).decode('utf-8')
            req_data = json.loads(raw)
        except Exception:
            req_data = {}

        condition = req_data.get('condition', '').strip()
        setting = req_data.get('setting', 'emergency').strip().lower()

        if not condition:
            err = json.dumps({'error': 'MISSING_CONDITION', 'message': 'Please provide a condition.'}).encode('utf-8')
            start_response('400 Bad Request', [('Content-Type', 'application/json'), ('Access-Control-Allow-Origin', '*')])
            return [err]

        try:
            print(f"[WSGI] Research request: '{condition}' ({setting})", flush=True)
            t0 = time.time()
            result = call_gemini(api_key, condition, setting)
            t1 = time.time()
            print(f"[WSGI] Research completed in {t1-t0:.1f}s", flush=True)

            body = json.dumps(result).encode('utf-8')
            start_response('200 OK', [
                ('Content-Type', 'application/json; charset=utf-8'),
                ('Access-Control-Allow-Origin', '*'),
            ])
            return [body]
        except Exception as e:
            traceback.print_exc()
            err = json.dumps({'error': 'SERVER_ERROR', 'message': str(e)}).encode('utf-8')
            start_response('500 Internal Server Error', [('Content-Type', 'application/json'), ('Access-Control-Allow-Origin', '*')])
            return [err]

    # ── Static Files ──
    if path == '/':
        path = '/index.html'

    file_path = BASE_DIR / path.lstrip('/')
    if file_path.exists() and file_path.is_file():
        ext = file_path.suffix.lower()
        ct = MIME_TYPES.get(ext, 'application/octet-stream')
        content = file_path.read_bytes()
        start_response('200 OK', [
            ('Content-Type', ct),
            ('Access-Control-Allow-Origin', '*'),
            ('Content-Length', str(len(content))),
        ])
        return [content]

    # ── 404 ──
    start_response('404 Not Found', [('Content-Type', 'text/plain'), ('Access-Control-Allow-Origin', '*')])
    return [b'Not Found']

# Alias for gunicorn
app = application

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    from wsgiref.simple_server import make_server
    print(f"[WSGI] Serving on 0.0.0.0:{port}...")
    make_server('0.0.0.0', port, app).serve_forever()
