import os
import requests
from flask import Flask, request, jsonify
import time
from collections import defaultdict

app = Flask(__name__)

LICENSE_URL = "https://gist.githubusercontent.com/longbmtgithub/a104c4c7c27608d9420e7ce94578b56c/raw/licenses.json"
GARENA_API_BASE = "https://kgvn-api.mobagarena.com"

_licenses = None
_last_fetch = 0

# In-memory usage tracker for free trial
_free_uses = defaultdict(int)

def get_licenses():
    global _licenses, _last_fetch
    now = time.time()
    if not _licenses or (now - _last_fetch > 60):
        try:
            r = requests.get(LICENSE_URL, timeout=10)
            _licenses = r.json()
            _last_fetch = now
        except:
            pass
    return _licenses or {}

def check_did(did):
    if not did: return False
    lics = get_licenses()
    if 'licenses' not in lics: return False
    
    # Check paid keys
    for k, v in lics['licenses'].items():
        if k == '*': continue
        devs = v.get('devices', [])
        if did in devs:
            return True
            
    # Check free key
    free_key = lics['licenses'].get('*')
    if free_key:
        free_uses = free_key.get('uses', [])
        devs = set(e.split('|')[0] for e in free_uses)
        if did in devs: return True
        
        # Free trial in memory (2 uses max)
        max_uses = 2
        if _free_uses[did] < max_uses:
            _free_uses[did] += 1
            return True
            
    return False

@app.route('/')
def index():
    return "Flowborn Proxy Server Running"

@app.route('/proxy', methods=['POST'])
def proxy():
    data = request.json
    if not data: return jsonify({"code": -1, "msg": "Invalid JSON"}), 400
    
    did = data.get('did')
    endpoint = data.get('endpoint')
    payload = data.get('payload', {})
    headers = data.get('headers', {})
    
    if not did or not endpoint:
        return jsonify({"code": -1, "msg": "Missing did or endpoint"}), 400
        
    if not check_did(did):
        return jsonify({"code": -999, "msg": "License KHONG hop le hoac het luot Free! Vui long mua key."}), 403
        
    try:
        for h in ['host', 'content-length', 'connection', 'accept-encoding']:
            headers.pop(h, None)
            
        r = requests.post(
            GARENA_API_BASE + endpoint,
            json=payload,
            headers=headers,
            timeout=30
        )
        try:
            return jsonify(r.json())
        except:
            return jsonify({"code": -1, "msg": f"Garena Error {r.status_code}"})
    except Exception as e:
        return jsonify({"code": -1, "msg": f"Proxy Error: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
