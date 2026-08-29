import urllib.request
import urllib.parse
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

q = 'TITLE:"asthma" AND (Egypt OR Egyptian OR Cairo OR "Ain Shams" OR Alexandria OR Mansoura OR Assiut OR "Kasr Al Ainy" OR Zagazig OR Tanta OR Menoufia) AND SRC:MED'
params = {'query': q, 'format': 'json', 'pageSize': 15, 'resultType': 'core', 'synonym': 'TRUE'}
url = f'https://www.ebi.ac.uk/europepmc/webservices/rest/search?{urllib.parse.urlencode(params)}'
req = urllib.request.Request(url, headers={'User-Agent': 'MedRef-Audit/1.0'})

data = json.loads(urllib.request.urlopen(req, timeout=20).read().decode('utf-8'))
results = data.get('resultList', {}).get('result', [])

print(f"Total results on Asthma in Title with Egyptian affiliations: {len(results)}\n")
for r in results:
    title = r.get('title')
    pmid = r.get('pmid')
    doi = r.get('doi')
    aff = r.get('affiliation') or ''
    year = r.get('pubYear')
    ab = r.get('abstractText') or ''
    print("=" * 70)
    print(f"Title   : {title}")
    print(f"PMID    : {pmid} | Year: {year} | DOI: {doi}")
    print(f"Affil   : {aff[:140]}")
    print(f"Abstract: {ab[:200]}...")
