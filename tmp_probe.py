import os, urllib.request, urllib.parse, json
from pathlib import Path

key = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')
url = os.getenv('SUPABASE_URL', '')
bucket = os.getenv('SUPABASE_BUCKET_NAME', '')
print('URL', url)
print('BUCKET', bucket)

for path in ['test_upload.v', 'jobs/JOB_0001/test_upload.v']:
    encoded = urllib.parse.quote(path, safe='/')
    u = f'{url}/storage/v1/object/{bucket}/{encoded}'
    print('REQUEST', u)
    req = urllib.request.Request(u, data=b'abc', method='POST', headers={'Authorization': f'Bearer {key}', 'apikey': key, 'Content-Type': 'application/octet-stream'})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            print('STATUS', resp.status)
            print(resp.read().decode('utf-8', 'replace'))
    except Exception as e:
        print(type(e).__name__, e)
        if hasattr(e, 'read'):
            print(e.read().decode('utf-8', 'replace'))
