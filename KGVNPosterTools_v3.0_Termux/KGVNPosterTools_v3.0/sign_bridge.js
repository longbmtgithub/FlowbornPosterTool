#!/usr/bin/env node
/**
 * sign_bridge.js — Node.js bridge for camp-security-oversea encodeparam generation
 * 
 * Usage:
 *   node sign_bridge.js --serve [port]    # HTTP server mode (default 19876)
 *   node sign_bridge.js --test            # Test mode
 * 
 * API:
 *   POST /init   body: {"encryption":"...", "campRoleid":"..."}  -> init setLoginRes
 *   POST /sign   body: {"roleid":"..."}                          -> get encodeparam
 *   GET  /health
 */

// === Robust Browser environment shim ===
const cryptoModule = require('crypto');
const globalObj = typeof globalThis !== 'undefined' ? globalThis : global;

globalObj.window = globalObj;
globalObj.self = globalObj;

if (!globalObj.crypto || !globalObj.crypto.getRandomValues) {
  globalObj.crypto = {
    getRandomValues: (arr) => { cryptoModule.randomFillSync(arr); return arr; },
    subtle: cryptoModule.webcrypto ? cryptoModule.webcrypto.subtle : undefined,
  };
}

globalObj.btoa = (s) => Buffer.from(s, 'binary').toString('base64');
globalObj.atob = (s) => Buffer.from(s, 'base64').toString('binary');

const noop = () => {};
const noopObj = () => ({
  style: {}, setAttribute: noop, getAttribute: () => null,
  appendChild: noop, removeChild: noop,
  addEventListener: noop, removeEventListener: noop,
  getElementsByTagName: () => [], getElementsByClassName: () => [],
  innerHTML: '', textContent: '', offsetWidth: 100, offsetHeight: 100,
  getBoundingClientRect: () => ({ top:0, left:0, bottom:100, right:100, width:100, height:100 }),
  classList: { add: noop, remove: noop, contains: () => false },
  dataset: {},
});

globalObj.document = {
  createElement: noopObj, createTextNode: () => ({}),
  createDocumentFragment: () => ({ appendChild: noop }),
  head: { appendChild: noop, removeChild: noop },
  body: { appendChild: noop, removeChild: noop, style: {} },
  getElementById: () => null, querySelector: () => null, querySelectorAll: () => [],
  addEventListener: noop, removeEventListener: noop,
  documentElement: { classList: { add: noop }, style: {}, getAttribute: () => null },
  cookie: '', readyState: 'complete',
  location: { hostname: 'kgvn-camp.mobagarena.com' },
};

globalObj.navigator = {
  userAgent: 'Mozilla/5.0 (Linux; Android 16; CPH2747 Build/BP2A.250605.015; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/149.0.7827.91 Mobile Safari/537.36',
  platform: 'Linux armv81', language: 'vi-VN', languages: ['vi-VN','vi','en-US','en'],
  appName: 'Netscape', cookieEnabled: true, onLine: true,
  hardwareConcurrency: 4, maxTouchPoints: 5,
};
globalObj.location = {
  hostname: 'kgvn-camp.mobagarena.com',
  href: 'https://kgvn-camp.mobagarena.com/',
  protocol: 'https:', origin: 'https://kgvn-camp.mobagarena.com',
  host: 'kgvn-camp.mobagarena.com', pathname: '/', search: '', hash: '',
};
globalObj.screen = { width: 412, height: 915, availWidth: 412, availHeight: 915, colorDepth: 24 };
globalObj.innerWidth = 412; globalObj.innerHeight = 915;
globalObj.devicePixelRatio = 2.625;
globalObj.XMLHttpRequest = class {
  constructor() { this.readyState = 0; this.status = 0; }
  open() {} send() {} setRequestHeader() {} getResponseHeader() { return null; }
  addEventListener() {} removeEventListener() {} abort() {}
};
globalObj.fetch = async () => ({ json: async () => ({}), text: async () => '', ok: true });
globalObj.Image = class {};
globalObj.HTMLElement = class {};
globalObj.localStorage = { getItem: () => null, setItem: noop, removeItem: noop };
globalObj.sessionStorage = { getItem: () => null, setItem: noop, removeItem: noop };
globalObj.requestAnimationFrame = (cb) => setTimeout(cb, 16);
globalObj.cancelAnimationFrame = (id) => clearTimeout(id);
globalObj.MutationObserver = class { observe(){} disconnect(){} };
globalObj.IntersectionObserver = class { observe(){} disconnect(){} };
globalObj.ResizeObserver = class { observe(){} disconnect(){} };
globalObj.matchMedia = () => ({ matches: false, addEventListener: noop, addListener: noop });
globalObj.getComputedStyle = () => new Proxy({}, { get: () => '' });
globalObj.performance = globalObj.performance || { now: () => Date.now(), getEntriesByType: () => [] };

// === Load security library ===
const path = require('path');
const fs = require('fs');
const securityPath = path.join(__dirname, 'camp-security-oversea.0.1.0.js');
if (!fs.existsSync(securityPath)) {
  console.error('ERROR: camp-security-oversea.0.1.0.js not found');
  process.exit(1);
}

console.error('[bridge] Loading camp-security-oversea...');
try { require(securityPath); } catch (e) {
  console.error('[bridge] Load note:', e.message?.substring(0, 100));
}

// === Wait for __TCSJ__ ===
function waitForTCSJ(maxMs = 5000) {
  return new Promise((resolve, reject) => {
    if (globalObj.__TCSJ__) return resolve(globalObj.__TCSJ__);
    let elapsed = 0;
    const iv = setInterval(() => {
      elapsed += 50;
      if (globalObj.__TCSJ__) { clearInterval(iv); resolve(globalObj.__TCSJ__); }
      else if (elapsed >= maxMs) { clearInterval(iv); reject(new Error('__TCSJ__ timeout')); }
    }, 50);
  });
}

// === State ===
let _tcsj = null;
let _initialized = false;

async function initTCSJ() {
  if (!_tcsj) _tcsj = await waitForTCSJ(5000);
  const methods = Object.keys(_tcsj).filter(k => typeof _tcsj[k] === 'function');
  console.error('[bridge] TCSJ methods:', methods);
  return _tcsj;
}

async function callSetLoginRes(encryption, campRoleid) {
  const tcsj = await initTCSJ();
  if (typeof tcsj.setLoginRes !== 'function') {
    throw new Error('setLoginRes not available');
  }
  tcsj.setLoginRes(encryption, campRoleid);
  _initialized = true;
  console.error('[bridge] setLoginRes OK (roleid=' + campRoleid + ')');
}

async function getEncodeParam(roleid) {
  const tcsj = await initTCSJ();
  if (!_initialized) {
    throw new Error('Not initialized. Call /init first with encryption + campRoleid');
  }
  if (typeof tcsj.getEncodeParam !== 'function') {
    throw new Error('getEncodeParam not available');
  }
  return tcsj.getEncodeParam(roleid || '');
}

// === Parse args ===
const args = process.argv.slice(2);

if (args.includes('--test')) {
  // === TEST MODE ===
  (async () => {
    try {
      const tcsj = await initTCSJ();
      console.log('TCSJ ready! Methods:', Object.keys(tcsj).filter(k => typeof tcsj[k] === 'function'));
      
      // Test without setLoginRes (will fail after first call)
      try {
        const ep1 = tcsj.getEncodeParam('');
        console.log('getEncodeParam (no init):', ep1?.substring(0, 50) + '...');
      } catch (e) {
        console.log('getEncodeParam (no init) error:', e.message);
      }
      
      // Test setLoginRes with dummy data
      console.log('\nTo use properly:');
      console.log('  1. Call /init with {encryption, campRoleid} from getselfuserinfo');
      console.log('  2. Then call /sign with {roleid}');
    } catch (e) {
      console.error('FAILED:', e.message);
      process.exit(1);
    }
  })();
  
} else if (args.includes('--serve')) {
  // === HTTP SERVER MODE ===
  const portIdx = args.indexOf('--serve');
  const port = parseInt(args[portIdx + 1]) || 19876;
  const http = require('http');
  
  // Pre-init TCSJ
  initTCSJ().then(() => {
    console.error('[bridge] TCSJ pre-loaded');
  }).catch(e => {
    console.error('[bridge] TCSJ pre-load failed:', e.message);
  });
  
  const server = http.createServer(async (req, res) => {
    res.setHeader('Content-Type', 'application/json');
    
    if (req.url === '/health') {
      res.end(JSON.stringify({
        status: 'ok',
        tcsj: !!_tcsj,
        initialized: _initialized,
        methods: _tcsj ? Object.keys(_tcsj).filter(k => typeof _tcsj[k] === 'function') : [],
      }));
      return;
    }
    
    if (req.url === '/init' && req.method === 'POST') {
      let body = '';
      req.on('data', c => body += c);
      req.on('end', async () => {
        try {
          const data = JSON.parse(body || '{}');
          if (!data.encryption) {
            res.statusCode = 400;
            res.end(JSON.stringify({ error: 'Missing encryption field' }));
            return;
          }
          await callSetLoginRes(data.encryption, data.campRoleid || '');
          // Test getEncodeParam right after init
          const testEp = _tcsj.getEncodeParam(data.campRoleid || '');
          res.end(JSON.stringify({
            ok: true,
            initialized: true,
            testEncodeparam: testEp,
          }));
        } catch (e) {
          res.statusCode = 500;
          res.end(JSON.stringify({ error: e.message }));
        }
      });
      return;
    }
    
    if (req.url === '/sign' && req.method === 'POST') {
      let body = '';
      req.on('data', c => body += c);
      req.on('end', async () => {
        try {
          const data = JSON.parse(body || '{}');
          const ep = await getEncodeParam(data.roleid || '');
          res.end(JSON.stringify({ encodeparam: ep }));
        } catch (e) {
          res.statusCode = 500;
          res.end(JSON.stringify({ error: e.message }));
        }
      });
      return;
    }
    
    res.statusCode = 404;
    res.end(JSON.stringify({ error: 'Use POST /init, POST /sign, or GET /health' }));
  });
  
  server.listen(port, '127.0.0.1', () => {
    console.error('[bridge] Server on http://127.0.0.1:' + port);
    console.log(JSON.stringify({ ready: true, port }));
  });
}
