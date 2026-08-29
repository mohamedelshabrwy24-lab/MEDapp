import json
import urllib.request
import urllib.parse
from europepmc import EuropePMCRetriever

r = EuropePMCRetriever()
res = r.search_medical_literature('Asthma', setting='emergency', max_total=25)

print(f"Query: {res['query_condition']} (Setting: {res['query_setting']})")
print(f"Total Records: {res['total_records_retrieved']}")
print("Summary:", json.dumps(res['summary'], indent=2))

print("\n--- SAMPLE SYSTEMATIC REVIEW / META-ANALYSIS ---")
for sr in res['evidence_tiers']['systematic_reviews_and_meta_analyses'][:2]:
    print(f"Title: {sr['title']}")
    print(f"Authors: {sr['authors']}")
    print(f"Journal: {sr['journal']} | Year: {sr['pub_year']}")
    print(f"PMID: {sr['pmid']} | DOI: {sr['doi']}")
    print(f"URL: {sr['article_url']}")
    print(f"Abstract preview: {sr['abstract'][:150]}...")
    print(f"Designation: {sr['evidence_designation']}")
    print("-" * 50)

print("\n--- SAMPLE EGYPTIAN RELEVANT PAPER ---")
for eg in res['evidence_tiers']['egypt_specific_literature'][:2]:
    print(f"Title: {eg['title']}")
    print(f"Authors: {eg['authors']}")
    print(f"Journal: {eg['journal']} | Year: {eg['pub_year']}")
    print(f"PMID: {eg['pmid']} | DOI: {eg['doi']}")
    print(f"URL: {eg['article_url']}")
    print(f"Egypt Details: {eg['egypt_evidence_details']}")
    print(f"Abstract preview: {eg['abstract'][:150]}...")
    print("-" * 50)
