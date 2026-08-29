import urllib.request
import urllib.parse
import json

q = '"Asthma" AND (PUB_TYPE:"Systematic Review" OR PUB_TYPE:"Meta-Analysis")'
params = {'query': q, 'format': 'json', 'pageSize': 5, 'resultType': 'core', 'synonym': 'TRUE'}
url = f'https://www.ebi.ac.uk/europepmc/webservices/rest/search?{urllib.parse.urlencode(params)}'
print('URL:', url)

try:
    req = urllib.request.Request(url, headers={'User-Agent': 'MedRef-Universal-Clinical-Search/1.0'})
    resp = urllib.request.urlopen(req, timeout=15)
    data = json.loads(resp.read().decode('utf-8'))
    print('HIT COUNT:', data.get('hitCount'))
    print('Returned results:', len(data.get('resultList', {}).get('result', [])))
except Exception as e:
    print('EXCEPTION:', e)
