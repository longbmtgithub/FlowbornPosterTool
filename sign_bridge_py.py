#!/usr/bin/env python3
"""
sign_bridge_py.py — Python-based sign bridge (no Node.js needed!)
Uses PyMiniRacer (V8 engine) to run camp-security-oversea.js
For iOS/iSH where Node.js is too slow.

Usage: python3 sign_bridge_py.py [port]
"""
import http.server
import json
import os
import sys
import threading

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 19876

# Try to import a JS engine
_engine = None
_ctx = None

def init_js_engine():
    global _engine, _ctx
    
    # Try py_mini_racer (fastest, uses V8)
    try:
        from py_mini_racer import MiniRacer
        _engine = "mini_racer"
        _ctx = MiniRacer()
        return True
    except ImportError:
        pass
    
    # Try js2py (pure Python, slower but works everywhere)
    try:
        import js2py
        _engine = "js2py"
        _ctx = js2py.EvalJs()
        return True
    except ImportError:
        pass
    
    return False

# Browser shims for the security library
BROWSER_SHIM = """
var window = this;
var self = this;
var globalThis = this;
var crypto = {
    getRandomValues: function(arr) {
        for (var i = 0; i < arr.length; i++) arr[i] = Math.floor(Math.random() * 256);
        return arr;
    }
};
var btoa = function(s) { return ''; };
var atob = function(s) { return ''; };
var navigator = {
    userAgent: 'Mozilla/5.0 (Linux; Android 16) AppleWebKit/537.36',
    platform: 'Linux armv81', language: 'vi-VN',
    languages: ['vi-VN','vi','en-US','en'],
    cookieEnabled: true, onLine: true,
    hardwareConcurrency: 4, maxTouchPoints: 5
};
var location = {
    hostname: 'kgvn-camp.mobagarena.com',
    href: 'https://kgvn-camp.mobagarena.com/',
    protocol: 'https:', origin: 'https://kgvn-camp.mobagarena.com',
    host: 'kgvn-camp.mobagarena.com', pathname: '/'
};
var screen = { width: 412, height: 915, colorDepth: 24 };
var innerWidth = 412; var innerHeight = 915;
var devicePixelRatio = 2.625;
var document = {
    createElement: function() { return {style:{},setAttribute:function(){},appendChild:function(){},classList:{add:function(){},remove:function(){},contains:function(){return false}},dataset:{},getBoundingClientRect:function(){return {top:0,left:0,width:100,height:100}}}; },
    createTextNode: function() { return {}; },
    head: {appendChild:function(){},removeChild:function(){}},
    body: {appendChild:function(){},removeChild:function(){},style:{}},
    getElementById: function() { return null; },
    querySelector: function() { return null; },
    querySelectorAll: function() { return []; },
    addEventListener: function() {},
    documentElement: {classList:{add:function(){}},style:{},getAttribute:function(){return null}},
    cookie: '', readyState: 'complete',
    location: {hostname:'kgvn-camp.mobagarena.com'}
};
var XMLHttpRequest = function() { this.readyState=0; this.status=0; };
XMLHttpRequest.prototype = {open:function(){},send:function(){},setRequestHeader:function(){},getResponseHeader:function(){return null},addEventListener:function(){}};
var fetch = function() { return Promise.resolve({json:function(){return {}},text:function(){return ''},ok:true}); };
var Image = function() {};
var HTMLElement = function() {};
var localStorage = {getItem:function(){return null},setItem:function(){},removeItem:function(){}};
var sessionStorage = {getItem:function(){return null},setItem:function(){},removeItem:function(){}};
var requestAnimationFrame = function(cb) { return setTimeout(cb, 16); };
var cancelAnimationFrame = function(id) { clearTimeout(id); };
var MutationObserver = function() {}; MutationObserver.prototype = {observe:function(){},disconnect:function(){}};
var IntersectionObserver = function() {}; IntersectionObserver.prototype = {observe:function(){},disconnect:function(){}};
var ResizeObserver = function() {}; ResizeObserver.prototype = {observe:function(){},disconnect:function(){}};
var matchMedia = function() { return {matches:false,addEventListener:function(){},addListener:function(){}}; };
var getComputedStyle = function() { return new Proxy({},{get:function(){return ''}}); };
var performance = { now: function() { return Date.now(); }, getEntriesByType: function() { return []; } };
"""

_initialized = False
_tcsj_ready = False

def load_security_lib():
    global _tcsj_ready
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sec_path = os.path.join(script_dir, "camp-security-oversea.0.1.0.js")
    
    if not os.path.isfile(sec_path):
        print("[bridge] ERROR: camp-security-oversea.0.1.0.js not found!", file=sys.stderr)
        return False
    
    print("[bridge] Loading JS engine ({})...".format(_engine), file=sys.stderr)
    
    with open(sec_path, "r", encoding="utf-8", errors="ignore") as f:
        sec_code = f.read()
    
    try:
        if _engine == "mini_racer":
            _ctx.eval(BROWSER_SHIM)
            _ctx.eval(sec_code)
            _tcsj_ready = True
            print("[bridge] Security lib loaded!", file=sys.stderr)
            return True
        elif _engine == "js2py":
            _ctx.execute(BROWSER_SHIM + "\n" + sec_code)
            _tcsj_ready = True
            print("[bridge] Security lib loaded!", file=sys.stderr)
            return True
    except Exception as e:
        print("[bridge] Load error: {}".format(str(e)[:100]), file=sys.stderr)
        return False

def call_set_login_res(encryption, camp_roleid):
    global _initialized
    if _engine == "mini_racer":
        _ctx.eval("__TCSJ__.setLoginRes('{}', '{}')".format(
            encryption.replace("'", "\\'"), camp_roleid.replace("'", "\\'")))
    elif _engine == "js2py":
        _ctx.execute("__TCSJ__.setLoginRes('{}', '{}')".format(
            encryption.replace("'", "\\'"), camp_roleid.replace("'", "\\'")))
    _initialized = True
    print("[bridge] setLoginRes OK", file=sys.stderr)

def get_encode_param(roleid=""):
    if _engine == "mini_racer":
        return _ctx.eval("__TCSJ__.getEncodeParam('{}')".format(roleid.replace("'", "\\'")))
    elif _engine == "js2py":
        _ctx.execute("var _ep = __TCSJ__.getEncodeParam('{}')".format(roleid.replace("'", "\\'")))
        return str(_ctx._ep)

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress logs
    
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "ok",
                "tcsj": _tcsj_ready,
                "initialized": _initialized,
                "engine": _engine,
                "methods": ["setLoginRes", "getEncodeParam"] if _tcsj_ready else []
            }).encode())
            return
        self.send_response(404)
        self.end_headers()
    
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode() if length > 0 else "{}"
        data = json.loads(body) if body else {}
        
        if self.path == "/init":
            try:
                if not data.get("encryption"):
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Missing encryption"}).encode())
                    return
                call_set_login_res(data["encryption"], data.get("campRoleid", ""))
                test_ep = get_encode_param(data.get("campRoleid", ""))
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "ok": True, "initialized": True, "testEncodeparam": test_ep
                }).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
            return
        
        if self.path == "/sign":
            try:
                ep = get_encode_param(data.get("roleid", ""))
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"encodeparam": ep}).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
            return
        
        self.send_response(404)
        self.end_headers()

if __name__ == "__main__":
    if not init_js_engine():
        print("[!] Can cai JS engine. Chay:", file=sys.stderr)
        print("    pip3 install py_mini_racer", file=sys.stderr)
        print("  hoac:", file=sys.stderr)
        print("    pip3 install js2py", file=sys.stderr)
        sys.exit(1)
    
    print("[bridge] Engine: {}".format(_engine), file=sys.stderr)
    
    if not load_security_lib():
        sys.exit(1)
    
    server = http.server.HTTPServer(("127.0.0.1", PORT), Handler)
    print("[bridge] Server on http://127.0.0.1:{}".format(PORT), file=sys.stderr)
    print(json.dumps({"ready": True, "port": PORT}))
    sys.stdout.flush()
    server.serve_forever()
