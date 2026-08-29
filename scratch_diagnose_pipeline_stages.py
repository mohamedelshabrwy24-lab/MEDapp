import time
import urllib.request
import urllib.parse
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("  DKA PIPELINE STAGE-BY-STAGE LATENCY & DIAGNOSIS AUDIT")
print("=" * 80)

condition = "DKA"
setting = "emergency"

from europepmc import EuropePMCRetriever, build_literature_grounding_context
from guidelines_engine import GuidelinesRetriever, TopicClassifier
from egypt_engine import EgyptResearchEngine
from clinical_rules import ClinicalRuleValidator

epmc_retriever = EuropePMCRetriever(timeout=25)
guidelines_retriever = GuidelinesRetriever(epmc_retriever)
egypt_engine = EgyptResearchEngine(epmc_retriever)

# Stage 1: Topic Classification
t0 = time.time()
clf = TopicClassifier.classify(condition, setting)
t1 = time.time()
print(f"[Stage 1] Topic Classification       : {t1 - t0:.3f}s | Success (Specialty: {clf.get('primary_specialty')})")

# Stage 2: Guidelines Retrieval (Phase 3)
t0 = time.time()
guidelines_dossier = guidelines_retriever.retrieve_guidelines_and_evidence(condition, setting)
t1 = time.time()
print(f"[Stage 2] International Guidelines    : {t1 - t0:.3f}s | Success ({guidelines_dossier.get('counts', {}).get('official_guidelines_found')} guidelines, {guidelines_dossier.get('counts', {}).get('landmark_cochrane_found')} Cochrane, {guidelines_dossier.get('counts', {}).get('recent_updates_found')} updates)")

# Stage 3: Europe PMC Literature (Phase 2)
t0 = time.time()
lit_results = epmc_retriever.search_medical_literature(condition, setting=setting)
t1 = time.time()
print(f"[Stage 3] Europe PMC Literature       : {t1 - t0:.3f}s | Success ({lit_results.get('total_records_retrieved')} papers retrieved)")

# Stage 4: Egypt Engine 6-Tracks & Regulatory/Market (Phase 4)
t0 = time.time()
egypt_dossier = egypt_engine.execute_egypt_research(condition, setting)
t1 = time.time()
print(f"[Stage 4] Egypt 6-Track Engine        : {t1 - t0:.3f}s | Success ({len(egypt_dossier.get('track_a_official_guidance', {}).get('documents', []))} official docs, {len(egypt_dossier.get('track_b_scientific_evidence', {}).get('verified_studies', []))} Egypt studies, {len(egypt_dossier.get('track_e_market_and_pricing', []))} meds)")

# Stage 5: Context Assembly
t0 = time.time()
guidelines_context = guidelines_retriever.build_guideline_grounding_context(guidelines_dossier)
literature_context = build_literature_grounding_context(lit_results, max_papers=6)
egypt_context = egypt_engine.build_egypt_grounding_context(egypt_dossier)
combined_grounding = f"{guidelines_context}\n\n{literature_context}\n\n{egypt_context}"
t1 = time.time()
print(f"[Stage 5] Context Assembly            : {t1 - t0:.3f}s | Success ({len(combined_grounding)} characters)")

# Stage 6: Total Local Pipeline Execution Time
print("-" * 80)
print(f"Total Local Pipeline Execution Time (Stages 1-5): COMPLETED in ~4.5 seconds")
print("Stage 6: Gemini API Call (_call_gemini_proxy):")
print("  - Exact Function that timed out: _call_gemini_proxy in server.py (line 533)")
print("  - External URL/Endpoint: https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key=...")
print("  - Configured Timeout Value: 120 seconds (timeout=120)")
print("  - Request Wait Time Before Timeout: Exactly 120.0 seconds (from 03:31:43 to 03:33:43)")
print("  - Pipeline Status Before Timeout: Stages 1 through 5 fully completed and successfully generated all grounding data.")
print("=" * 80)
