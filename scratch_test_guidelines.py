import json
import sys
from guidelines_engine import GuidelinesRetriever, TopicClassifier

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 70)
print("  PHASE 3 TEST: GUIDELINES & STRONGEST EVIDENCE RETRIEVAL")
print("=" * 70)

# Step 1: Test Topic Classifier
c = TopicClassifier.classify("Asthma", "emergency")
print("\n[1] TOPIC CLASSIFICATION:")
print(f"• Condition           : {c['condition']}")
print(f"• Primary Specialty   : {c['primary_specialty']}")
print(f"• Secondary Branches  : {', '.join(c['secondary_specialties'])}")
print(f"• Clinical Questions  : {', '.join(c['clinical_question_types'])}")
print(f"• Selected Societies  : {', '.join([b['abbr'] + ' (' + b['name'] + ')' for b in c['authoritative_bodies']])}")

# Step 2: Test Guidelines Retriever
print("\n[2] RETRIEVING LIVE GUIDELINES & COCHRANE EVIDENCE...")
retriever = GuidelinesRetriever()
dossier = retriever.retrieve_guidelines_and_evidence("Asthma", "emergency")

counts = dossier["counts"]
print(f"\n[3] RETRIEVAL METRICS:")
print(f"• Official Guidelines Found       : {counts['official_guidelines_found']}")
print(f"• Landmark Cochrane Reviews Found : {counts['landmark_cochrane_found']}")
print(f"• Recent Post-Guideline Updates   : {counts['recent_updates_found']}")

print("\n" + "=" * 50)
print("  SAMPLE OFFICIAL GUIDELINES RETRIEVED")
print("=" * 50)
for g in dossier["guideline_records"][:3]:
    print(f"• Organization : {g['organization']}")
    print(f"  Title        : {g['guideline_title']}")
    print(f"  Year         : {g['publication_year']} | PMID: {g['pmid']} | DOI: {g['doi']}")
    print(f"  URL          : {g['article_url']}")
    print(f"  Abstract     : {g['abstract'][:200]}...")
    print("-" * 40)

print("\n" + "=" * 50)
print("  SAMPLE COCHRANE & LANDMARK REVIEWS")
print("=" * 50)
for c in dossier["cochrane_and_landmark_evidence"][:2]:
    print(f"• Title    : {c['title']}")
    print(f"  Authors  : {c['authors']} | Journal: {c['journal']} ({c['year']})")
    print(f"  PMID     : {c['pmid']} | DOI: {c['doi']} | URL: {c['article_url']}")
    print(f"  Design   : {c['design']}")
    print(f"  Abstract : {c['abstract'][:200]}...")
    print("-" * 40)

print("\n" + "=" * 50)
print("  SAMPLE POST-GUIDELINE UPDATE EVIDENCE (2024-2026)")
print("=" * 50)
for u in dossier["update_search_recent_evidence"][:2]:
    print(f"• Title    : {u['study_title']}")
    print(f"  Authors  : {u['authors']} | Journal: {u['journal']} ({u['year']})")
    print(f"  PMID     : {u['pmid']} | DOI: {u['doi']} | URL: {u['article_url']}")
    print(f"  Abstract : {u['abstract'][:200]}...")
    print("-" * 40)

# Step 3: Test Grounding Context Construction
context_text = retriever.build_guideline_grounding_context(dossier)
print(f"\n[4] GROUNDING CONTEXT GENERATED ({len(context_text)} characters)")
print("Preview of context header:")
print(context_text[:400])

print("\n" + "=" * 70)
print("  PHASE 3 RETRIEVAL TEST SUCCESSFUL")
print("=" * 70)
