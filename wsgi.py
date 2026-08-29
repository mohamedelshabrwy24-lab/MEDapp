import os
import sys
import json
import urllib.parse
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from server import (
    load_env,
    mask_key,
    USAGE_TRACKER,
    epmc_retriever,
    guidelines_retriever,
    egypt_engine,
    MedRefGatewayHandler
)

MIME_TYPES = {
    '.html': 'text/html; charset=utf-8',
    '.css': 'text/css; charset=utf-8',
    '.js': 'application/javascript; charset=utf-8',
    '.json': 'application/json; charset=utf-8',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.svg': 'image/svg+xml',
    '.ico': 'image/x-icon'
}

def application(environ, start_response):
    """Standard WSGI Entrypoint for Gunicorn, Render, and Cloud Containers."""
    path = environ.get('PATH_INFO', '/')
    method = environ.get('REQUEST_METHOD', 'GET').upper()

    # CORS preflight
    if method == 'OPTIONS':
        headers = [
            ('Content-Type', 'text/plain'),
            ('Access-Control-Allow-Origin', '*'),
            ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'),
            ('Access-Control-Allow-Headers', 'Content-Type')
        ]
        start_response('200 OK', headers)
        return [b'']

    # Health Check
    if path == '/api/health' and method == 'GET':
        env = load_env()
        data = {
            'status': 'healthy',
            'phase': 'Phase 4 — Full 6-Track Egypt Research & International Evidence Active',
            'credentials': {
                'gemini_configured': bool(env.get('GEMINI_API_KEY')),
                'gemini_masked': mask_key(env.get('GEMINI_API_KEY')),
                'tavily_configured': bool(env.get('TAVILY_API_KEY')),
                'tavily_masked': mask_key(env.get('TAVILY_API_KEY'))
            },
            'safeguards': {
                'max_searches_per_topic': int(env.get('MAX_SEARCHES_PER_TOPIC', 2)),
                'usage_stats': USAGE_TRACKER
            }
        }
        body = json.dumps(data).encode('utf-8')
        headers = [
            ('Content-Type', 'application/json; charset=utf-8'),
            ('Access-Control-Allow-Origin', '*'),
            ('Content-Length', str(len(body)))
        ]
        start_response('200 OK', headers)
        return [body]

    # Research API Endpoint
    if path == '/api/research' and method == 'POST':
        env = load_env()
        gemini_key = env.get('GEMINI_API_KEY', '').strip()

        if not gemini_key:
            err = json.dumps({'error': 'MISSING_API_KEY', 'message': 'GEMINI_API_KEY is not configured.'}).encode('utf-8')
            start_response('400 Bad Request', [('Content-Type', 'application/json'), ('Access-Control-Allow-Origin', '*')])
            return [err]

        try:
            content_length = int(environ.get('CONTENT_LENGTH', 0))
            raw_body = environ['wsgi.input'].read(content_length).decode('utf-8')
            req_data = json.loads(raw_body)
        except Exception:
            req_data = {}

        condition = req_data.get('condition', '').strip()
        setting = req_data.get('setting', 'emergency').strip().lower()

        if not condition:
            err = json.dumps({'error': 'MISSING_CONDITION', 'message': 'Please provide a condition name.'}).encode('utf-8')
            start_response('400 Bad Request', [('Content-Type', 'application/json'), ('Access-Control-Allow-Origin', '*')])
            return [err]

        # Use MedRef handler helper
        import concurrent.futures
        from server import TopicClassifier

        def fetch_guidelines():
            try:
                return guidelines_retriever.retrieve_guidelines_and_evidence(condition, setting=setting)
            except Exception as e:
                return {"classification": TopicClassifier.classify(condition, setting), "guideline_records": [], "cochrane_and_landmark_evidence": [], "update_search_recent_evidence": [], "counts": {}}

        def fetch_literature():
            try:
                return epmc_retriever.search_medical_literature(condition, setting=setting)
            except Exception as e:
                return {'total_records_retrieved': 0, 'records': [], 'summary': {}}

        def fetch_egypt():
            try:
                return egypt_engine.execute_egypt_research(condition, setting=setting)
            except Exception as e:
                return {}

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            f_guide = executor.submit(fetch_guidelines)
            f_lit = executor.submit(fetch_literature)
            f_egypt = executor.submit(fetch_egypt)

            guidelines_dossier = f_guide.result()
            lit_results = f_lit.result()
            egypt_dossier = f_egypt.result()

        dummy_handler = MedRefGatewayHandler.__new__(MedRefGatewayHandler)
        combined_grounding = dummy_handler._build_compact_grounding_context(guidelines_dossier, lit_results, egypt_dossier)

        try:
            result, active_model = dummy_handler._call_gemini_proxy(gemini_key, condition, setting, combined_grounding)
            result['guidelines_evidence'] = guidelines_dossier
            result['literature_evidence'] = lit_results
            result['egypt_evidence'] = egypt_dossier

            body = json.dumps(result).encode('utf-8')
            start_response('200 OK', [('Content-Type', 'application/json; charset=utf-8'), ('Access-Control-Allow-Origin', '*'), ('Content-Length', str(len(body)))])
            return [body]
        except Exception as e:
            err = json.dumps({'error': 'SERVER_ERROR', 'message': str(e)}).encode('utf-8')
            start_response('500 Internal Server Error', [('Content-Type', 'application/json'), ('Access-Control-Allow-Origin', '*')])
            return [err]

    # Static File Serving
    if path == '/':
        path = '/index.html'

    file_path = BASE_DIR / path.lstrip('/')
    if file_path.exists() and file_path.is_file():
        ext = file_path.suffix.lower()
        content_type = MIME_TYPES.get(ext, 'application/octet-stream')
        with open(file_path, 'rb') as f:
            content = f.read()
        headers = [
            ('Content-Type', content_type),
            ('Access-Control-Allow-Origin', '*'),
            ('Content-Length', str(len(content)))
        ]
        start_response('200 OK', headers)
        return [content]

    # 404 Not Found
    err = json.dumps({'error': 'NOT_FOUND', 'path': path}).encode('utf-8')
    start_response('404 Not Found', [('Content-Type', 'application/json'), ('Access-Control-Allow-Origin', '*')])
    return [err]

# Alias for WSGI servers (gunicorn wsgi:app)
app = application

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    from wsgiref.simple_server import make_server
    print(f"Serving WSGI application on 0.0.0.0:{port}...")
    httpd = make_server('0.0.0.0', port, application)
    httpd.serve_forever()
