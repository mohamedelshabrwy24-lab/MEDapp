import urllib.request
import urllib.parse
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

def search(q, size=5):
    params = {'query': q, 'format': 'json', 'pageSize': size, 'resultType': 'core', 'synonym': 'TRUE'}
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={'User-Agent': 'MedRef-Audit/1.0'})
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read().decode('utf-8'))
        return data.get('resultList', {}).get('result', [])
    except Exception as e:
        print(f"Error {q}: {e}")
        return []

print("=== 1. GINA GUIDELINES SEARCH ===")
gina_results = search('("Global Initiative for Asthma" OR "GINA") AND (strategy OR guideline OR report OR management OR exacerbation) AND (SRC:MED OR SRC:PMC)', 6)
for r in gina_results:
    print(f"Title: {r.get('title')}")
    print(f"PMID: {r.get('pmid')} | Year: {r.get('pubYear')} | DOI: {r.get('doi')}")
    print(f"PubTypes: {r.get('pubTypeList', {}).get('pubType', [])}")
    print("-" * 50)

print("\n=== 2. COMPLETED COCHRANE REVIEWS FOR ASTHMA EMERGENCY / ACUTE ===")
cochrane_completed = search('("Cochrane Database Syst Rev" OR "Cochrane review") AND Asthma AND (acute OR emergency OR exacerbation OR "magnesium" OR "corticosteroids" OR "ipratropium" OR "SABA") NOT (protocol OR "protocol for a cochrane review")', 6)
for r in cochrane_completed:
    ab = r.get('abstractText') or ''
    is_proto = 'protocol for a cochrane' in ab.lower() or 'this is a protocol' in ab.lower() or 'protocol' in (r.get('title') or '').lower()
    print(f"Title: {r.get('title')}")
    print(f"PMID: {r.get('pmid')} | Year: {r.get('pubYear')} | DOI: {r.get('doi')}")
    print(f"Is Protocol?: {is_proto}")
    print("-" * 50)

print("\n=== 3. WHO / BTS-SIGN / NICE ASTHMA GUIDELINES ===")
guidelines_results = search('Asthma AND (PUB_TYPE:"Practice Guideline" OR PUB_TYPE:"Guideline") AND (NICE OR WHO OR BTS OR SIGN OR ERS OR ATS)', 6)
for r in guidelines_results:
    print(f"Title: {r.get('title')}")
    print(f"PMID: {r.get('pmid')} | Year: {r.get('pubYear')} | DOI: {r.get('doi')}")
    print(f"PubTypes: {r.get('pubTypeList', {}).get('pubType', [])}")
    print("-" * 50)
