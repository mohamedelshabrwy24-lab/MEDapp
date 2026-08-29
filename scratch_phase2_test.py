import urllib.request
import json
import time

print("=" * 60)
print("  MEDREF PHASE 2 TEST: LIVE EUROPE PMC / PUBMED SEARCH")
print("=" * 60)

# 1. Test Health Endpoint
health_resp = urllib.request.urlopen('http://localhost:8000/api/health')
health = json.loads(health_resp.read().decode())
print(f"Health Status: {health.get('status')} | Phase: {health.get('phase')}")
print(f"Europe PMC Queries so far: {health.get('safeguards', {}).get('usage_stats', {}).get('total_europepmc_queries')}")

# 2. Test Live Literature Endpoint for 'Asthma'
t0 = time.time()
lit_url = 'http://localhost:8000/api/literature?condition=Asthma&setting=emergency'
print(f"\nQuerying LIVE Europe PMC REST API via {lit_url}...")
resp = urllib.request.urlopen(lit_url, timeout=25)
elapsed = round(time.time() - t0, 2)
data = json.loads(resp.read().decode())

print(f"Response Received: HTTP {resp.status} in {elapsed}s")
print(f"Source: {data.get('source')}")
print(f"Condition: {data.get('query_condition')} | Setting: {data.get('query_setting')}")

summary = data.get('summary', {})
print("\n" + "=" * 40)
print("  BIBLIOGRAPHIC & EVIDENCE METRICS")
print("=" * 40)
print(f"• Total papers retrieved: {data.get('total_records_retrieved')}")
print(f"• Recent papers (2020-Present): {summary.get('recent_papers_count')}")
print(f"• Systematic reviews & Meta-analyses: {summary.get('systematic_reviews_count')}")
print(f"• Randomized Controlled Trials (RCTs): {summary.get('rcts_count')}")
print(f"• Clinical Guidelines & Consensus: {summary.get('guidelines_count')}")
print(f"• Potentially Egyptian Studies: {summary.get('egypt_relevant_count')}")
print(f"• Records with real PMIDs: {summary.get('with_pmid_count')}")
print(f"• Records with real DOIs: {summary.get('with_doi_count')}")
print(f"• Records with real Abstracts: {summary.get('with_abstract_count')}")

print("\n" + "=" * 40)
print("  SAMPLE 1: HIGH-LEVEL SYSTEMATIC REVIEW / META-ANALYSIS")
print("=" * 40)
sr_list = data.get('evidence_tiers', {}).get('systematic_reviews_and_meta_analyses', [])
if sr_list:
    item = sr_list[0]
    print(f"Title       : {item['title']}")
    print(f"Authors     : {item['authors']}")
    print(f"Journal     : {item['journal']} ({item['pub_year']})")
    print(f"PMID        : {item['pmid']}")
    print(f"DOI         : {item['doi']}")
    print(f"Article URL : {item['article_url']}")
    print(f"Evidence    : {item['evidence_designation']}")
    print(f"Abstract    : {item['abstract'][:250]}...")

print("\n" + "=" * 40)
print("  SAMPLE 2: RANDOMIZED CONTROLLED TRIAL (RCT)")
print("=" * 40)
rct_list = data.get('evidence_tiers', {}).get('randomized_trials', [])
if rct_list:
    item = rct_list[0]
    print(f"Title       : {item['title']}")
    print(f"Authors     : {item['authors']}")
    print(f"Journal     : {item['journal']} ({item['pub_year']})")
    print(f"PMID        : {item['pmid']}")
    print(f"DOI         : {item['doi']}")
    print(f"Article URL : {item['article_url']}")
    print(f"Evidence    : {item['evidence_designation']}")
    print(f"Abstract    : {item['abstract'][:250]}...")

print("\n" + "=" * 40)
print("  SAMPLE 3: EGYPTIAN CLINICAL STUDY / COHORT")
print("=" * 40)
eg_list = data.get('evidence_tiers', {}).get('egypt_specific_literature', [])
if eg_list:
    item = eg_list[0]
    print(f"Title       : {item['title']}")
    print(f"Authors     : {item['authors']}")
    print(f"Journal     : {item['journal']} ({item['pub_year']})")
    print(f"PMID        : {item['pmid']}")
    print(f"DOI         : {item['doi']}")
    print(f"Article URL : {item['article_url']}")
    print(f"Egypt Tag   : {item['egypt_evidence_details']}")
    print(f"Evidence    : {item['evidence_designation']}")
    print(f"Abstract    : {item['abstract'][:250]}...")

print("\n" + "=" * 60)
print("  TEST COMPLETED SUCCESSFULLY")
print("=" * 60)
