import urllib.request
import urllib.parse
import json
import datetime
import sys

sys.stdout.reconfigure(encoding='utf-8')

test_pmids = ['42102625', '41138958', '40996012', '38522064', '42056204', '42151924', '41888731', '40352336']
condition = 'asthma'

verified_list = []
excluded_list = []

for pmid in test_pmids:
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:{pmid}%20SRC:MED&format=json&resultType=core"
    req = urllib.request.Request(url, headers={'User-Agent': 'MedRef-Audit/1.0'})
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read().decode('utf-8'))
        results = data.get('resultList', {}).get('result', [])
        if not results:
            excluded_list.append({'pmid': pmid, 'reason': 'PMID not found in Europe PMC/MEDLINE'})
            continue
        r = results[0]
        title = (r.get('title') or '').strip().rstrip('.')
        doi = r.get('doi') or ''
        aff = r.get('affiliation') or ''
        year = str(r.get('pubYear') or '')
        pub_types = r.get('pubTypeList', {}).get('pubType', [])
        if isinstance(pub_types, str): pub_types = [pub_types]
        pub_types_lower = [str(pt).lower() for pt in pub_types]
        title_lower = title.lower()

        # Check not protocol, editorial, letter, correction
        if any(pt in ['editorial', 'letter', 'published erratum', 'retracted publication'] for pt in pub_types_lower) or 'correction:' in title_lower or 'protocol' in title_lower:
            excluded_list.append({'pmid': pmid, 'title': title, 'reason': 'Excluded: Protocol/Correction/Letter/Editorial'})
            continue

        # Check condition in title or abstract
        ab = (r.get('abstractText') or '').lower()
        if condition.lower() not in title_lower and condition.lower() not in ab:
            excluded_list.append({'pmid': pmid, 'title': title, 'reason': f'Excluded: Condition {condition} not found'})
            continue

        # Check if primary topic is off-topic (e.g. rheumatoid arthritis, h. pylori, dental)
        if any(other in title_lower for other in ['rheumatoid arthritis', 'pylori', 'dental', 'periodontitis', 'breast cancer', 'hepatitis']):
            excluded_list.append({'pmid': pmid, 'title': title, 'reason': 'Excluded: Primary disease is off-topic'})
            continue

        # Check Egypt affiliation
        if not any(kw in aff.lower() for kw in ['egypt', 'cairo', 'ain shams', 'alexandria', 'mansoura', 'assiut', 'zagazig', 'tanta', 'menoufia', 'al-azhar']):
            excluded_list.append({'pmid': pmid, 'title': title, 'reason': 'Excluded: No verified Egyptian affiliation in record'})
            continue

        verified_list.append({
            'verified_pmid': pmid,
            'verified_doi': doi,
            'verified_title': title,
            'verified_publication_type': pub_types,
            'pub_year': year,
            'egypt_relevance': f'Verified Affiliation: {aff[:100]}...',
            'clinical_relevance': f'Confirmed on-topic clinical investigation of {condition}',
            'original_url': f'https://doi.org/{doi}' if doi else f'https://pubmed.ncbi.nlm.nih.gov/{pmid}/',
            'verification_source': 'Europe PMC & MEDLINE Direct Record Verification',
            'verification_timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat()
        })
    except Exception as e:
        excluded_list.append({'pmid': pmid, 'reason': str(e)})

print(f"=== VERIFIED EGYPTIAN STUDIES ({len(verified_list)}) ===")
for v in verified_list:
    print(f"• PMID: {v['verified_pmid']} | DOI: {v['verified_doi']}")
    print(f"  Title: {v['verified_title']}")
    print(f"  Types: {v['verified_publication_type']}")
    print(f"  URL  : {v['original_url']}")
    print(f"  Affil: {v['egypt_relevance']}")
    print(f"  Time : {v['verification_timestamp']}")
    print("-" * 60)

print(f"\n=== EXCLUDED STUDIES ({len(excluded_list)}) ===")
for ex in excluded_list:
    print(f"• PMID: {ex.get('pmid')} -> {ex.get('title', 'N/A')}")
    print(f"  Reason: {ex.get('reason')}")
    print("-" * 60)
