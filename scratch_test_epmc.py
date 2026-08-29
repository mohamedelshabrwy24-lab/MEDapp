import urllib.request
import urllib.parse
import json

queries = [
    'Asthma Egypt',
    'Asthma AND (Egypt OR Egyptian)',
    'Asthma AND (PUB_TYPE:"Systematic Review" OR PUB_TYPE:"Meta-Analysis")',
    'Asthma AND PUB_TYPE:"Randomized Controlled Trial"',
    'Asthma AND (guideline OR consensus OR management)'
]

for q in queries:
    params = urllib.parse.urlencode({
        'query': q,
        'format': 'json',
        'pageSize': 3,
        'resultType': 'core',
        'synonym': 'TRUE'
    })
    url = f'https://www.ebi.ac.uk/europepmc/webservices/rest/search?{params}'
    req = urllib.request.Request(url, headers={'User-Agent': 'MedRef-Universal-Clinical-Search/1.0'})
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read().decode('utf-8'))
        count = data.get('hitCount', 0)
        res = data.get('resultList', {}).get('result', [])
        print(f"Query: {q:50} -> Total Hits: {count:6} | Returned: {len(res)}")
        if res:
            first = res[0]
            print(f"  Title: {first.get('title')[:85]}")
            print(f"  PMID: {first.get('pmid')} | DOI: {first.get('doi')} | Year: {first.get('pubYear')} | Journal: {first.get('journalTitle')}")
            print(f"  PubType: {first.get('pubTypeList', {}).get('pubType', [])}")
            print(f"  Abstract len: {len(first.get('abstractText', '') or '')}")
    except Exception as e:
        print(f"Error on '{q}': {e}")
