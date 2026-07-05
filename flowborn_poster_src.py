#!/usr/bin/env python3
import argparse
import hashlib
import hmac as hmac_lib
import io
import json
import os
import socket
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path
from datetime import datetime

_LICENSE_URL = "https://gist.githubusercontent.com/longbmtgithub/a104c4c7c27608d9420e7ce94578b56c/raw/licenses.json"
_USES_FILE = os.path.expanduser("~/.fp_uses")
_0xSESSION = None  # License session - REQUIRED for API calls

def _0xD1():
    try:
        h = socket.gethostname()
        u = os.environ.get('USER', os.environ.get('USERNAME', 'unknown'))
        return hashlib.sha256(f"{h}:{u}:flowborn_poster".encode()).hexdigest()[:16]
    except:
        return hashlib.sha256(b"fallback_device").hexdigest()[:16]

def _0xD2():
    try:
        with open(_USES_FILE) as f: return int(f.read().strip())
    except: return 0

def _0xD3(n):
    try:
        with open(_USES_FILE, 'w') as f: f.write(str(n))
    except: pass

def _0xXR(data, key):
    """XOR decode."""
    return bytes(data[i] ^ key[i % len(key)] for i in range(len(data)))

def _0xD4():
    """License check — returns session dict or None. Session contains decrypted API endpoint."""
    global _0xSESSION
    did = _0xD1()
    try:
        import requests as _r
        resp = _r.get(_LICENSE_URL, timeout=10)
        data = resp.json()
        lics = data.get('licenses', {})
        lic = lics.get(did) or lics.get('*')
        if not lic:
            print(f"\033[91m  [!] Device chua duoc cap phep: {did}\033[0m")
            print(f"\033[93m  Mua key tai: https://longbmtgithub.github.io/FlowbornPosterTool/buy.html\033[0m")
            return None
        if isinstance(lic, dict):
            exp = lic.get('expires', '')
            if exp:
                try:
                    if datetime.strptime(exp, '%Y-%m-%d') < datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
                        print(f"\033[91m  [!] License het han: {exp}\033[0m"); return None
                except: pass
            max_uses = lic.get('max', 999)
            current = _0xD2()
            if current >= max_uses:
                print(f"\033[91m  [!] Da het {max_uses} luot su dung!\033[0m"); return None
            name = lic.get('name', '')
            if '[CHO THANH TOAN]' in name:
                print(f"\033[91m  [!] License chua thanh toan!\033[0m"); return None
            print(f"\033[92m  \u2713 License: {did} ({current+1}/{max_uses})\033[0m")
        # Decrypt API endpoint from license server key
        _sk = data.get('_sk', '')
        if not _sk:
            return None
        try:
            import base64
            _gk = _LICENSE_URL.split('/')[-4][:16]  # Gist ID prefix as key
            _ep = _0xXR(base64.b64decode(_sk), _gk.encode()).decode('utf-8')
        except:
            return None
        _0xSESSION = {'did': did, 'ep': _ep, 'ts': time.time()}
        return _0xSESSION
    except:
        return None

def _0xCK():
    """Checkpoint — verify license session is still valid."""
    if not _0xSESSION: sys.exit(1)
    if time.time() - _0xSESSION.get('ts', 0) > 7200: sys.exit(1)
    if not _0xSESSION.get('ep', '').startswith('https://'): sys.exit(1)

def _0xEP():
    """Get API base from session — tool CANNOT work without this."""
    _0xCK()
    return _0xSESSION['ep']

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    print("\033[91m[!] Thieu: pip install requests\033[0m")
    sys.exit(1)

try:
    from PIL import Image as _PIL_Image
    PILLOW_OK = True
except ImportError:
    PILLOW_OK = False

# =============================================================================
# ANSI COLORS
# =============================================================================

class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"

    # Foreground
    RED    = "\033[91m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    BLUE   = "\033[94m"
    PURPLE = "\033[95m"
    CYAN   = "\033[96m"
    WHITE  = "\033[97m"
    GRAY   = "\033[90m"

    # Background accents
    BG_BLUE   = "\033[44m"
    BG_GREEN  = "\033[42m"
    BG_RED    = "\033[41m"
    BG_PURPLE = "\033[45m"

def ok(msg):   return "{}✓  {}{}".format(C.GREEN,  msg, C.RESET)
def err(msg):  return "{}✗  {}{}".format(C.RED,    msg, C.RESET)
def warn(msg): return "{}⚠  {}{}".format(C.YELLOW, msg, C.RESET)
def info(msg): return "{}›  {}{}".format(C.CYAN,   msg, C.RESET)
def dim(msg):  return "{}{}{}".format(C.GRAY, msg, C.RESET)
def bold(msg): return "{}{}{}".format(C.BOLD, msg, C.RESET)

def hdr(title, width=62):
    inner = " {} ".format(title)
    pad   = max(0, width - len(inner) - 2)
    l, r  = pad // 2, pad - pad // 2
    return ("{}{}{} {}{}{}{} {}{}".format(
        C.BG_PURPLE, C.WHITE, C.BOLD,
        "─"*l, inner, "─"*r,
        C.RESET, C.PURPLE, C.RESET))

def sep(width=62, char="─", color=C.GRAY):
    return "{}{}{}".format(color, char*width, C.RESET)

# =============================================================================
# CAU HINH
# =============================================================================

COS_BUCKET          = "aovcamp-h5-ugc-1254801811"
COS_REGION          = "ap-singapore"
COS_HOST            = "{}.cos.{}.myqcloud.com".format(COS_BUCKET, COS_REGION)
CDN_BASE            = "https://kg-camp-ugc.mobagarena.com"
CDN_OFFICIAL        = "https://kg-camp.mobagarena.com"
API_BASE            = None  # Set by license session
IMAGE_EXTS          = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".mp4"}
DEFAULT_HAR         = "auto"
OFFICIAL_STICKER_ID = "190"
NAMEPLATE_ID        = "49"
NAMEPLATE_PICURL    = "https://kg-camp.mobagarena.com/manage/flowborn_official/ZeoMxjHs.png"
MAX_MEDIA_PER_ACC   = 6

# Delay (giay) giua moi poster thread de tranh -1999 frequency limited
POSTER_STAGGER      = 3.6
# Delay giua cac vong lap
ROUND_DELAY         = 3.0
# Delay khoi dong moi acc thread
ACC_STAGGER         = 2.0
# Sign bridge port
SIGN_BRIDGE_PORT    = 19876
SIGN_BRIDGE_URL     = "http://127.0.0.1:{}".format(SIGN_BRIDGE_PORT)

# ROLE_CONFIG: key = (main_job, gender)
ROLE_CONFIG = {
    (1,1): {"label":"Assassin Nam"},
    (1,2): {"label":"Assassin Nu"},
    (2,1): {"label":"Tank Nam"},
    (2,2): {"label":"Tank Nu"},
    (3,1): {"label":"Support Nam"},
    (3,2): {"label":"Support Nu"},
    (4,1): {"label":"Mid Nam",
            "baseInfo_id":"62",
            "baseInfo_picUrl": CDN_OFFICIAL+"/manage/flowborn_official/5fXAjyuq.png"},
    (4,2): {"label":"Mid Nu",
            "baseInfo_id":"63",
            "baseInfo_picUrl": CDN_OFFICIAL+"/manage/flowborn_official/5fXAjyuq.png"},
    (5,1): {"label":"Ad Nam",
            "baseInfo_id":"32",
            "baseInfo_picUrl": CDN_OFFICIAL+"/manage/flowborn_official/Pd7zTH2f.png"},
    (5,2): {"label":"Ad Nu",
            "baseInfo_id":"33",
            "baseInfo_picUrl": CDN_OFFICIAL+"/manage/flowborn_official/Pd7zTH2f.png"},
    (6,1): {"label":"Jungle Nam"},
    (6,2): {"label":"Jungle Nu"},
}

# Fallback User-Agent / sec-ch-ua — se bi override boi gia tri lay tu HAR
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Linux; Android 16; CPH2747 Build/BP2A.250605.015; wv) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/149.0.7827.91 "
    "Mobile Safari/537.36 MSDK/5.36.000 mQQAppId/1105779914 "
    "mWXAppId/wx7a814e3ceeda8320 mGameId/1137 MSDKdeviceId/disable"
)
DEFAULT_SEC_CH_UA = '"Android WebView";v="149", "Chromium";v="149", "Not)A;Brand";v="24"'

FIXED_HEADERS = {
    "camp-source":        "AOV-CAMP",
    "msdk-gameid":        "1137",
    "camp-authtype":      "msdk",
    "areaid":             "1",
    "msdk-os":            "1",
    "logicworldid":       "1011",
    "aov-language":       "VN",
    "msdk-channelid":     "10",
    "aov-region":         "1137",
    "origin":             "https://kgvn-camp.mobagarena.com",
    "x-requested-with":   "com.garena.game.kgvn",
    "referer":            "https://kgvn-camp.mobagarena.com/",
    "sec-ch-ua-mobile":   "?1",
    "sec-ch-ua-platform": '"Android"',
    "sec-fetch-site":     "same-site",
    "sec-fetch-mode":     "cors",
    "sec-fetch-dest":     "empty",
    "accept":             "*/*",
    "accept-language":    "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    "accept-encoding":    "gzip, deflate, br, zstd",
}

_print_lock = threading.Lock()
def tprint(msg):
    with _print_lock:
        print(msg, flush=True)

# =============================================================================
# SIGN BRIDGE (Node.js subprocess for encodeparam generation)
# =============================================================================

_sign_bridge_proc = None
_sign_session     = None
_sign_lock        = threading.Lock()
_camp_roleid      = ""

def _find_node():
    """Tim Node.js binary."""
    for cmd in ["node", "nodejs"]:
        try:
            r = subprocess.run([cmd, "--version"],
                               capture_output=True, timeout=5)
            if r.returncode == 0:
                return cmd
        except (FileNotFoundError, subprocess.SubprocessError):
            continue
    # Termux path
    termux = os.environ.get("PREFIX", "/data/data/com.termux/files/usr")
    node_path = os.path.join(termux, "bin", "node")
    if os.path.isfile(node_path):
        return node_path
    return None

def start_sign_bridge():
    """Khoi dong sign bridge. Thu Python bridge truoc (cho iSH), roi Node.js."""
    global _sign_bridge_proc, _sign_session

    script_dir = os.path.dirname(os.path.abspath(__file__))
    security_js = os.path.join(script_dir, "camp-security-oversea.0.1.0.js")
    if not os.path.isfile(security_js):
        tprint(warn("camp-security-oversea.0.1.0.js khong tim thay!"))
        return False

    # --- Thu Python bridge (nhanh hon tren iSH) ---
    py_bridge = os.path.join(script_dir, "sign_bridge_py.py")
    _is_ish = os.path.isfile("/etc/alpine-release") if sys.platform != "win32" else False
    if _is_ish and os.path.isfile(py_bridge):
        tprint(info("Thu Python sign bridge (iSH mode)..."))
        try:
            python_cmd = sys.executable or "python3"
            _sign_bridge_proc = subprocess.Popen(
                [python_cmd, py_bridge, str(SIGN_BRIDGE_PORT)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                cwd=script_dir,
            )
            # Doi Python bridge san sang (co the nhanh hon Node)
            import time as _t
            for _ in range(120):  # 60s max
                _t.sleep(0.5)
                if _sign_bridge_proc.poll() is not None:
                    break
                try:
                    _sign_session = requests.Session()
                    r = _sign_session.get(SIGN_BRIDGE_URL + "/health", timeout=2)
                    if r.status_code == 200:
                        tprint(ok("Python sign bridge san sang!"))
                        return True
                except Exception:
                    pass
            tprint(warn("Python bridge khong san sang, thu Node.js..."))
            try:
                _sign_bridge_proc.terminate()
            except Exception:
                pass
            _sign_bridge_proc = None
        except Exception as e:
            tprint(warn("Python bridge loi: " + str(e)[:60]))

    # --- Node.js bridge ---
    node = _find_node()
    if not node:
        tprint(warn("Node.js khong tim thay!"))
        tprint(info("  Cai dat: pkg install nodejs"))
        return False

    tprint(info("Node.js: {}".format(node)))

    bridge_js = os.path.join(script_dir, "sign_bridge.js")
    if not os.path.isfile(bridge_js):
        tprint(warn("sign_bridge.js khong tim thay!"))
        return False

    tprint(info("Khoi dong sign bridge..."))
    try:
        _sign_bridge_proc = subprocess.Popen(
            [node, bridge_js, "--serve", str(SIGN_BRIDGE_PORT)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=script_dir,
        )

        # Doc stdout va stderr bang thread de tranh block
        _stdout_buf = []
        _stderr_buf = []

        def _read_stream(stream, buf):
            try:
                for line in iter(stream.readline, b""):
                    buf.append(line)
            except Exception:
                pass

        t_out = threading.Thread(target=_read_stream,
                                 args=(_sign_bridge_proc.stdout, _stdout_buf),
                                 daemon=True)
        t_err = threading.Thread(target=_read_stream,
                                 args=(_sign_bridge_proc.stderr, _stderr_buf),
                                 daemon=True)
        t_out.start()
        t_err.start()

        # iSH (iOS) chay cham hon -> timeout lon hon
        _is_ish = os.path.isfile("/etc/alpine-release") or "ish" in os.uname().nodename.lower() if hasattr(os, "uname") else False
        _bridge_timeout = 60 if _is_ish else 10
        deadline = time.time() + _bridge_timeout
        ready = False
        while time.time() < deadline:
            if _sign_bridge_proc.poll() is not None:
                # Process exited
                t_out.join(timeout=1)
                t_err.join(timeout=1)
                stderr_txt = b"".join(_stderr_buf).decode(errors="ignore")
                tprint(err("Sign bridge thoat som!"))
                # Hien thi stderr de debug
                for line in stderr_txt.strip().split("\n")[:8]:
                    if line.strip():
                        tprint(dim("  [node] " + line.strip()[:80]))
                _sign_bridge_proc = None
                return False

            # Kiem tra stdout co {"ready":true}
            for line in _stdout_buf:
                try:
                    data = json.loads(line.decode().strip())
                    if data.get("ready"):
                        ready = True
                        break
                except Exception:
                    pass
            if ready:
                break
            time.sleep(0.3)

        if ready:
            _sign_session = requests.Session()
            # Kiem tra health
            try:
                r = _sign_session.get(
                    SIGN_BRIDGE_URL + "/health", timeout=5)
                if r.status_code == 200:
                    data = r.json()
                    tprint(ok("Sign bridge san sang (tcsj={}, methods={})".format(
                        data.get("tcsj"),
                        ",".join(data.get("methods",[])))))
                    return True
                else:
                    tprint(warn("Sign bridge health fail: {}".format(r.status_code)))
                    return False
            except Exception as e:
                tprint(warn("Sign bridge health loi: " + str(e)[:60]))
                return False
        else:
            # Khong ready
            t_out.join(timeout=1)
            t_err.join(timeout=1)
            stderr_txt = b"".join(_stderr_buf).decode(errors="ignore")
            tprint(warn("Sign bridge TIMEOUT ({}s)".format(_bridge_timeout)))
            for line in stderr_txt.strip().split("\n")[:10]:
                if line.strip():
                    tprint(dim("  [node] " + line.strip()[:80]))
            # Tat process
            try:
                _sign_bridge_proc.terminate()
            except Exception:
                pass
            _sign_bridge_proc = None
            return False

    except Exception as e:
        tprint(err("Loi khoi dong sign bridge: " + str(e)[:80]))
        return False

def stop_sign_bridge():
    """Tat sign bridge."""
    global _sign_bridge_proc
    if _sign_bridge_proc:
        try:
            _sign_bridge_proc.terminate()
            _sign_bridge_proc.wait(timeout=3)
        except Exception:
            try: _sign_bridge_proc.kill()
            except Exception: pass
        _sign_bridge_proc = None

def get_fresh_encodeparam(body_str="{}", roleid="", fallback_ep=None):
    """
    Lay encodeparam moi tu sign bridge.
    Neu sign bridge khong chay: tra ve fallback_ep (tu HAR, co the fail).
    """
    if not _sign_session or not _sign_bridge_proc:
        return fallback_ep
    # Kiem tra process con song khong
    if _sign_bridge_proc.poll() is not None:
        tprint(warn("Sign bridge process da thoat!"))
        return fallback_ep
    # Dung campRoleid da luu tu init (quan trong!)
    rid = roleid or _camp_roleid
    with _sign_lock:
        try:
            r = _sign_session.post(
                SIGN_BRIDGE_URL + "/sign",
                json={"roleid": rid},
                timeout=5,
            )
            if r.status_code == 200:
                data = r.json()
                ep = data.get("encodeparam")
                if ep and len(ep) > 10:
                    return ep
                else:
                    tprint(warn("Sign bridge tra ve ep rong: {}".format(
                        str(data)[:80])))
            else:
                tprint(warn("Sign bridge HTTP {}: {}".format(
                    r.status_code, r.text[:80])))
        except Exception as e:
            tprint(warn("Sign bridge loi: {}".format(str(e)[:60])))
    return fallback_ep

def init_sign_bridge_for_acc(session, auth_token, encode_param,
                             har_ua, har_sec_ch_ua):
    """
    Goi API getselfuserinfo de lay encryption + campRoleid,
    roi gui cho sign bridge /init de setLoginRes.
    Phai goi TRUOC khi dung get_fresh_encodeparam.
    """
    if not _sign_session or not _sign_bridge_proc:
        return False

    tprint(info("  Khoi tao sign bridge (getselfuserinfo)..."))

    # Goi getselfuserinfo - endpoint nay skipAuthGate nen khong can encodeparam
    hdrs = dict(FIXED_HEADERS)
    hdrs["content-type"]         = "application/json"
    hdrs["msdk-itopencodeparam"] = auth_token
    hdrs["traceparent"]          = gen_traceparent()
    hdrs["priority"]             = "u=1, i"
    hdrs["user-agent"]           = har_ua or DEFAULT_USER_AGENT
    hdrs["sec-ch-ua"]            = har_sec_ch_ua or DEFAULT_SEC_CH_UA
    # Dung encode_param tu HAR cho request nay (skipAuthGate co the chap nhan)
    if encode_param:
        hdrs["encodeparam"]      = encode_param

    try:
        r = session.post(
            _0xEP() + "/api/user/game/getselfuserinfo",
            headers=hdrs,
            json={},
            timeout=10,
        )
        data = r.json()
        if data.get("code") != 0:
            tprint(warn("  getselfuserinfo code={} msg={}".format(
                data.get("code"), data.get("msg","")[:60])))
            return False

        userdata = data.get("data", {})
        encryption = userdata.get("encryption")
        role = userdata.get("role", {})
        camp_roleid = role.get("campRoleid", "")

        if not encryption:
            tprint(warn("  getselfuserinfo: khong co encryption"))
            return False

        tprint(info("  campRoleid={}".format(camp_roleid)))

        # Luu campRoleid de dung cho get_fresh_encodeparam
        global _camp_roleid
        _camp_roleid = camp_roleid

        # Gui cho sign bridge /init
        r2 = _sign_session.post(
            SIGN_BRIDGE_URL + "/init",
            json={"encryption": encryption, "campRoleid": camp_roleid},
            timeout=5,
        )
        if r2.status_code == 200:
            init_data = r2.json()
            if init_data.get("ok"):
                test_ep = init_data.get("testEncodeparam", "")
                tprint(ok("  Sign bridge init OK! (ep={})".format(
                    test_ep[:30] + "..." if test_ep else "?")))
                return True
            else:
                tprint(warn("  Sign bridge init response: {}".format(
                    str(init_data)[:80])))
                return False
        else:
            tprint(warn("  Sign bridge init HTTP {}: {}".format(
                r2.status_code, r2.text[:80])))
            return False

    except Exception as e:
        tprint(warn("  init_sign_bridge loi: {}".format(str(e)[:80])))
        return False

# =============================================================================
# UTILS
# =============================================================================

def gen_traceparent():
    return "00-{}-{}-01".format(os.urandom(16).hex(), os.urandom(8).hex())

def check_connectivity():
    for host in ["kgvn-api.mobagarena.com", "8.8.8.8"]:
        try:
            socket.setdefaulttimeout(5)
            socket.getaddrinfo(host, 443)
            return True
        except socket.gaierror:
            continue
    return False

def make_session():
    s = requests.Session()
    r = Retry(total=3, backoff_factor=1.5,
              status_forcelist=[500,502,503,504],
              allowed_methods=["POST","PUT","GET"])
    a = HTTPAdapter(max_retries=r)
    s.mount("https://", a); s.mount("http://", a)
    return s

def ask_choice(prompt, options):
    print("\n" + "{}{}{}".format(C.CYAN, prompt, C.RESET))
    for k, v in options.items():
        print("    {}[{}]{} {}".format(C.YELLOW+C.BOLD, k, C.RESET, v))
    while True:
        try:
            c = input("    {}Chon: {}".format(C.PURPLE, C.RESET)).strip()
            if c in options:
                return c
            print(warn("Nhap: " + " / ".join(options.keys())))
        except KeyboardInterrupt:
            print("\n" + err("Huy")); sys.exit(0)

def cinput(prompt):
    """Input co mau."""
    try:
        return input("{}{}{}".format(C.PURPLE, prompt, C.RESET)).strip()
    except KeyboardInterrupt:
        print("\n" + err("Huy")); sys.exit(0)

def has_ffmpeg():
    try:
        subprocess.run(["ffmpeg","-version"], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False

def countdown(msg, secs):
    """Hien thi dem nguoc co mau."""
    for i in range(int(secs), 0, -1):
        tprint("{}  {} {}{}s...{}".format(
            C.GRAY, msg, C.YELLOW, i, C.RESET))
        time.sleep(1)

# =============================================================================
# COS SIGNING
# =============================================================================

def _hmac_sha1(key, msg):
    return hmac_lib.new(key, msg.encode(), hashlib.sha1).hexdigest()

def build_cos_auth(sid, skey, method, pathname, clen):
    now   = int(time.time())
    end   = now + 86400
    kt    = "{};{}".format(now, end)
    sk    = _hmac_sha1(skey.encode(), kt)
    hh    = "content-length={}&host={}".format(clen, COS_HOST)
    hs    = "{}\n{}\n\n{}\n".format(method.lower(), pathname, hh)
    hhttp = hashlib.sha1(hs.encode()).hexdigest()
    s2s   = "sha1\n{}\n{}\n".format(kt, hhttp)
    sig   = _hmac_sha1(sk.encode(), s2s)
    return ("q-sign-algorithm=sha1&q-ak={}"
            "&q-sign-time={}&q-key-time={}"
            "&q-header-list=content-length;host&q-url-param-list="
            "&q-signature={}").format(sid, kt, kt, sig)

# =============================================================================
# PARSE HAR
# =============================================================================

def parse_har(har_path):
    """
    Tra ve: (auth_token, encode_param, user_path, main_job, gender,
             baseInfo_raw, har_ua, har_sec_ch_ua)
    - Lay token/encodeparam MOI NHAT (cuoi HAR) de dam bao chua het han
    - Lay user-agent + sec-ch-ua tu HAR de khop voi session
    Uu tien baseInfo: getpostereditinfo RESPONSE > save* REQUEST > default
    """
    with open(har_path, "r", encoding="utf-8", errors="ignore") as f:
        har = json.load(f)

    auth_token    = None
    encode_param  = None
    har_ua        = None
    har_sec_ch_ua = None
    user_path     = None
    main_job      = 5
    gender        = 2
    bi_raw        = {}

    for entry in har["log"]["entries"]:
        if "getpostereditinfo" not in entry["request"]["url"]:
            continue
        try:
            body = json.loads(
                entry.get("response",{}).get("content",{}).get("text","{}"))
            bi = body.get("data",{}).get("picInfo",{}).get("baseInfo",{})
            if bi:
                main_job = int(bi.get("mainJob", main_job))
                gender   = int(bi.get("gender",  gender))
                bi_raw   = bi
        except Exception:
            pass

    # Duyet TAT CA entries — LUON ghi de token/encodeparam → lay ban MOI NHAT
    for entry in har["log"]["entries"]:
        req = entry["request"]
        url = req["url"]

        if "kgvn-api.mobagarena.com" in url and req.get("method") == "POST":
            hdrs = {h["name"].lower(): h["value"]
                    for h in req.get("headers",[])}
            # Luon ghi de → cuoi cung se la ban moi nhat
            if "msdk-itopencodeparam" in hdrs:
                auth_token = hdrs["msdk-itopencodeparam"]
            if "encodeparam" in hdrs:
                encode_param = hdrs["encodeparam"]
            # Lay user-agent + sec-ch-ua tu HAR
            if "user-agent" in hdrs:
                har_ua = hdrs["user-agent"]
            if "sec-ch-ua" in hdrs:
                har_sec_ch_ua = hdrs["sec-ch-ua"]

        if req["method"] == "PUT" and COS_HOST in url and not user_path:
            path  = url.split(COS_HOST)[1].split("?")[0]
            parts = path.strip("/").split("/")
            if len(parts) >= 3:
                user_path = "/" + "/".join(parts[:3]) + "/"

        if not bi_raw and any(
            k in url for k in ("saveposter","savepostereditinfo")
        ):
            try:
                body = json.loads(req.get("postData",{}).get("text","{}"))
                bi   = body.get("picInfo",{}).get("baseInfo",{})
                if bi:
                    main_job = int(bi.get("mainJob", main_job))
                    gender   = int(bi.get("gender",  gender))
                    bi_raw   = bi
                elif "mainJob" in body:
                    main_job = int(body["mainJob"])
            except Exception:
                pass

    return (auth_token, encode_param, user_path,
            main_job, gender, bi_raw,
            har_ua, har_sec_ch_ua)

def get_role_label(mj, gdr):
    return ROLE_CONFIG.get((mj,gdr),{}).get("label",
           "Job{} G{}".format(mj,gdr))

def role_color(mj, gdr):
    """Mau theo vai tro."""
    colors = {4: C.CYAN, 5: C.YELLOW, 1: C.RED,
              2: C.BLUE, 3: C.GREEN,  6: C.PURPLE}
    return colors.get(mj, C.WHITE)

# =============================================================================
# MEDIA PROCESSING
# =============================================================================

def prepare_media(file_path):
    """
    Xu ly media truoc khi upload.
    Tra ve dict:
      png_bytes  : bytes PNG de server render (bat buoc)
      anim_bytes : bytes GIF (None neu khong phai GIF/MP4)
      anim_ext   : "gif" | None
      label      : mo ta ngan
      name       : ten file goc
    """
    file_path = Path(file_path)
    ext       = file_path.suffix.lower()
    raw       = file_path.read_bytes()

    # ---- JPG / PNG / WEBP ---------------------------------------------------
    if ext in (".jpg",".jpeg",".png",".webp"):
        return {
            "png_bytes":  raw,
            "anim_bytes": None,
            "anim_ext":   None,
            "label":      "{} {:,}B".format(ext.upper().lstrip("."), len(raw)),
            "name":       file_path.name,
        }

    # ---- GIF ----------------------------------------------------------------
    if ext == ".gif":
        if not PILLOW_OK:
            print(err("GIF can Pillow: pip install Pillow")); sys.exit(1)
        try:
            gif = _PIL_Image.open(io.BytesIO(raw))
            gif.seek(0)
            buf = io.BytesIO()
            gif.convert("RGBA").save(buf, format="PNG")
            png_b = buf.getvalue()
            print(info("    GIF: frame1→PNG {:,}B  +  GIF goc {:,}B".format(
                len(png_b), len(raw))))
            return {
                "png_bytes":  png_b,
                "anim_bytes": raw,
                "anim_ext":   "gif",
                "label":      "GIF {:,}B anim".format(len(raw)),
                "name":       file_path.name,
            }
        except Exception as e:
            print(err("Loi GIF: " + str(e))); sys.exit(1)

    # ---- MP4 ----------------------------------------------------------------
    if ext == ".mp4":
        if not has_ffmpeg():
            print(err("MP4 can ffmpeg: pkg install ffmpeg")); sys.exit(1)
        # Dung NamedTemporaryFile an toan hon mktemp (tuong thich Termux)
        tmp_dir = os.environ.get("TMPDIR", tempfile.gettempdir())
        tmp_mp4 = os.path.join(tmp_dir, "v2_tmp_{}.mp4".format(os.getpid()))
        tmp_gif = os.path.join(tmp_dir, "v2_tmp_{}.gif".format(os.getpid()))
        tmp_png = os.path.join(tmp_dir, "v2_tmp_{}.png".format(os.getpid()))
        try:
            with open(tmp_mp4,"wb") as f: f.write(raw)
            print(info("    MP4 → GIF (fps=10 scale=320)..."))
            subprocess.run(
                ["ffmpeg","-i",tmp_mp4,
                 "-vf","fps=10,scale=320:-1:flags=lanczos",
                 "-loop","0", tmp_gif, "-y"],
                capture_output=True, check=True
            )
            with open(tmp_gif,"rb") as f: gif_b = f.read()
            subprocess.run(
                ["ffmpeg","-i",tmp_gif,"-vframes","1",
                 "-f","image2",tmp_png,"-y"],
                capture_output=True, check=True
            )
            with open(tmp_png,"rb") as f: png_b = f.read()
            for fp in [tmp_mp4,tmp_gif,tmp_png]:
                try: os.unlink(fp)
                except OSError: pass
            print(info("    PNG render {:,}B  GIF anim {:,}B".format(
                len(png_b), len(gif_b))))
            return {
                "png_bytes":  png_b,
                "anim_bytes": gif_b,
                "anim_ext":   "gif",
                "label":      "MP4→GIF {:,}B anim".format(len(gif_b)),
                "name":       file_path.name,
            }
        except subprocess.CalledProcessError as e:
            print(err("ffmpeg that bai: " + str(e))); sys.exit(1)
        except Exception as e:
            print(err("Loi MP4: " + str(e))); sys.exit(1)

    print(err("Dinh dang khong ho tro: " + ext)); sys.exit(1)

# =============================================================================
# SCAN FILES
# =============================================================================

def scan_media(directory):
    files = sorted([
        p for p in Path(directory).iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS
    ])
    if not files:
        print(err("Khong tim thay media trong: " + directory))
        sys.exit(1)
    return files

def find_har_files(directory="."):
    return sorted(Path(directory).glob("*.har"))

# =============================================================================
# API HELPERS
# =============================================================================

def api_post(session, endpoint, payload, auth_token,
             encode_param=None, har_ua=None, har_sec_ch_ua=None,
             roleid="",
             retry_on_code1=False, max_retries=3, delay=3.0):
    hdrs = dict(FIXED_HEADERS)
    hdrs["content-type"]         = "application/json"
    hdrs["msdk-itopencodeparam"] = auth_token
    hdrs["traceparent"]          = gen_traceparent()
    hdrs["priority"]             = "u=1, i"
    # User-Agent + sec-ch-ua tu HAR (khop session), fallback sang default
    hdrs["user-agent"]           = har_ua or DEFAULT_USER_AGENT
    hdrs["sec-ch-ua"]            = har_sec_ch_ua or DEFAULT_SEC_CH_UA
    data = {}
    for attempt in range(max_retries):
        # Tao encodeparam MOI cho MOI lan thu (moi request can ep rieng)
        body_str = json.dumps(payload, separators=(',',':'))
        ep = get_fresh_encodeparam(body_str, roleid, encode_param)
        if ep:
            hdrs["encodeparam"] = ep
        # Tao traceparent moi cho moi retry
        hdrs["traceparent"] = gen_traceparent()
        try:
            _0xCK()
            r = session.post(_0xEP()+endpoint,
                             json=payload, headers=hdrs, timeout=25)
            # Khong dung raise_for_status — doc response body du 4xx
            try:
                data = r.json()
            except (ValueError, Exception):
                data = {"code":-1,"msg":"HTTP {} - {}".format(
                    r.status_code, r.text[:80])}
            if data is None:
                data = {"code":-1,"msg":"response body is null"}
            if r.status_code != 200:
                ep_info = "fresh" if (ep and ep != encode_param) else "HAR"
                tprint(warn("  HTTP {} trên {} [{}/{}] (ep={})".format(
                    r.status_code, endpoint.split('/')[-1],
                    attempt+1, max_retries, ep_info)))
                if r.status_code == 403:
                    tprint(dim("  body: {}".format(str(data)[:100])))
                if attempt < max_retries-1:
                    time.sleep(delay); continue
                return data
            if retry_on_code1 and data.get("code") == 1:
                wait = delay*(attempt+1)
                tprint(warn("  code=1 thu lai {}s [{}/{}]".format(
                    int(wait), attempt+1, max_retries)))
                time.sleep(wait); continue
            return data
        except requests.exceptions.ConnectionError as e:
            tprint(err("Loi ket noi: "+str(e)))
            return {"code":-1,"msg":str(e)}
        except requests.exceptions.Timeout:
            if attempt < max_retries-1:
                tprint(warn("  Timeout [{}/{}] thu lai...".format(
                    attempt+1, max_retries)))
                time.sleep(delay)
            else:
                return {"code":-1,"msg":"timeout"}
        except (ValueError, requests.exceptions.JSONDecodeError):
            tprint(warn("  Response khong phai JSON [{}/{}]".format(
                attempt+1, max_retries)))
            if attempt < max_retries-1:
                time.sleep(delay)
            else:
                return {"code":-1,"msg":"invalid json response"}
        except requests.exceptions.HTTPError as e:
            tprint(err("HTTP error: "+str(e)[:50]))
            if attempt < max_retries-1:
                time.sleep(delay)
            else:
                return {"code":-1,"msg":"http error: "+str(e)[:40]}
    return data if data else {"code":-1,"msg":"max retries"}

def cos_put(session, url, data, headers, label=""):
    for attempt in range(3):
        try:
            resp = session.put(url, data=data, headers=headers, timeout=60)
            if resp.status_code == 200:
                return resp
            tprint(warn("  COS {} [{}]: {}".format(
                label, resp.status_code, resp.text[:120])))
            if attempt < 2: time.sleep(2)
        except requests.exceptions.ConnectionError as e:
            tprint(err("COS loi: "+str(e))); return None
    return resp



# =============================================================================
# BUILD picInfo
# =============================================================================

def build_pic_info(pic_info_raw, bi_har, sticker_url,
                   main_job, gender,
                   nameplate_text=None, nameplate_picurl=None):
    bg  = pic_info_raw.get("bg") or {}
    bpi = pic_info_raw.get("baseInfo") or {}
    cfg = ROLE_CONFIG.get((main_job,gender)) or {}
    bi_har = bi_har or {}
    bi  = {
        "id":       (bi_har.get("id")
                     or bpi.get("id")
                     or cfg.get("baseInfo_id","32")),
        "gender":   int(bi_har.get("gender")    or bpi.get("gender",    gender)),
        "mainJob":  int(bi_har.get("mainJob")   or bpi.get("mainJob",   main_job)),
        "picUrl":   (bi_har.get("picUrl")
                     or bpi.get("picUrl")
                     or cfg.get("baseInfo_picUrl",
                                 CDN_OFFICIAL+"/manage/flowborn_official/Pd7zTH2f.png")),
        "skinColor":int(bi_har.get("skinColor") or bpi.get("skinColor",1)),
    }
    result = {
        "bg":{"id":bg.get("id","30"),
               "picUrl":bg.get("picUrl",
                               CDN_OFFICIAL+"/manage/flowborn_official/4uxOQChv.png")},
        "baseInfo": bi,
        "stickerList": [{
            "id":     OFFICIAL_STICKER_ID,
            "picUrl": sticker_url,
            "width":  484.1990950226244,
            "height": 484.1990950226244,
            "posX":   -124.24919457013574,
            "posY":   -76.04248388393627,
            "rotate": 0, "source":1, "type":1,
        }],
    }
    if nameplate_text:
        result["nameplateList"] = [{
            "id": NAMEPLATE_ID,
            "picUrl": nameplate_picurl or NAMEPLATE_PICURL,
            "content": nameplate_text,
            "font":0,"fontSize":0,"textLength":0,
            "width":256,"height":59.91396199095023,
            "posX":0,"posY":204.82141004190632,"rotate":0,
        }]
    return result

# =============================================================================
# COMPOSITE NAMEPLATE
# =============================================================================

def composite_nameplate(png_bytes, name_text, session):
    if not PILLOW_OK:
        return png_bytes
    from PIL import ImageDraw, ImageFont
    NP_Y = 204.82/264.73; NP_H = 59.91/264.73
    img  = _PIL_Image.open(io.BytesIO(png_bytes)).convert("RGBA")
    W, H = img.size
    nh   = max(40, int(H*NP_H))
    ny   = H - nh
    tmpl = None
    try:
        resp = session.get(NAMEPLATE_PICURL, timeout=10)
        if resp.status_code == 200:
            tmpl = _PIL_Image.open(io.BytesIO(resp.content)).convert("RGBA")
            tmpl = tmpl.resize((W,nh), _PIL_Image.LANCZOS)
    except Exception:
        pass
    if tmpl is None:
        tmpl = _PIL_Image.new("RGBA",(W,nh),(0,0,0,0))
        dt   = ImageDraw.Draw(tmpl)
        for i in range(nh):
            dt.line([(0,i),(W,i)],
                    fill=(int(80+40*i/nh),int(60+40*i/nh),int(180+40*i/nh),200))
    ov = _PIL_Image.new("RGBA",(W,H),(0,0,0,0))
    ov.paste(tmpl,(0,ny))
    img  = _PIL_Image.alpha_composite(img,ov)
    draw = ImageDraw.Draw(img)
    font = None
    # Termux + Android system font paths
    _termux_prefix = os.environ.get("PREFIX", "/data/data/com.termux/files/usr")
    _font_candidates = [
        # Android system fonts
        "/system/fonts/NotoSansCJK-Regular.ttc",
        "/system/fonts/NotoSans-Regular.ttf",
        "/system/fonts/Roboto-Regular.ttf",
        "/system/fonts/DroidSans.ttf",
        # Termux fonts
        os.path.join(_termux_prefix, "share/fonts/TTF/DejaVuSans.ttf"),
        os.path.join(_termux_prefix, "share/fonts/TTF/DejaVuSansMono.ttf"),
        os.path.join(_termux_prefix, "share/fonts/NotoSans-Regular.ttf"),
    ]
    for fp in _font_candidates:
        try:
            font = ImageFont.truetype(fp, max(16,int(nh*0.52))); break
        except Exception:
            pass
    if font is None:
        font = ImageFont.load_default()
    bb   = draw.textbbox((0,0), name_text, font=font)
    tw,th= bb[2]-bb[0], bb[3]-bb[1]
    tx   = (W-tw)//2
    ty   = ny + (nh-th)//2 - bb[1]
    draw.text((tx+2,ty+2), name_text, font=font, fill=(0,0,0,180))
    draw.text((tx,ty),     name_text, font=font, fill=(255,255,255,255))
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="PNG")
    return buf.getvalue()

# =============================================================================
# POSTER WORKER  (1 media / 1 thread)
# =============================================================================

def poster_worker(idx, acc_lbl, auth_token, encode_param, user_path,
                  main_job, gender, bi_har,
                  media, pic_info_raw, is_share,
                  nameplate_text, nameplate_picurl,
                  har_ua, har_sec_ch_ua, results):
    tag     = "{}[{} P{:02d}]{}".format(
        C.BLUE+C.BOLD, acc_lbl[:14], idx, C.RESET)
    session = make_session()

    png_b    = media["png_bytes"]
    anim_b   = media["anim_bytes"]
    anim_ext = media["anim_ext"]
    fname    = media.get("name","?")

    try:
        # A. createposter
        tprint("{} Tao poster {}...".format(tag, dim(fname[:16])))
        r = api_post(session,"/api/game/poster/flowborn/createposter",
                     {},auth_token, encode_param, har_ua, har_sec_ch_ua)
        if r.get("code") != 0:
            tprint("{} {}".format(tag, err("createposter: "+r.get("msg","")[:40])))
            results[idx-1]=(False,"createposter: "+r.get("msg","")[:40]); return
        pid = r["data"]["posterId"]
        tprint("{} PosterID={}{}{}".format(tag, C.YELLOW, pid, C.RESET))
        time.sleep(0.5)

        # A2. Helper: lay COS credentials rieng cho tung file
        def get_cos_creds(fname_short, label=""):
            rc = api_post(session,"/api/game/poster/getcoscredential",
                          {"scene":"FlowbornPoster","fileName":fname_short},
                          auth_token, encode_param, har_ua, har_sec_ch_ua)
            if rc.get("code") != 0:
                tprint("{} {}".format(tag, err(
                    "getCos {} FAIL: {}".format(label, rc.get("msg","")[:40]))))
                return None
            return rc["data"]

        def mkhdr(crd, key, buf, ct):
            return {
                "Authorization":        build_cos_auth(
                    crd["tmpSecretId"],crd["tmpSecretKey"],"PUT",key,len(buf)),
                "Content-Type":         ct,
                "Content-Length":       str(len(buf)),
                "Host":                 COS_HOST,
                "x-cos-security-token": crd["token"],
                "Origin":               "https://kgvn-camp.mobagarena.com",
                "Referer":              "https://kgvn-camp.mobagarena.com/",
            }

        # B. COS upload — moi file lay credentials rieng
        ck   = "{}{}/1/{}.png".format(user_path, main_job, pid)
        ck_l = "{}{}/1/{}_large.png".format(user_path, main_job, pid)

        # B1. Upload _large.png (lay creds rieng)
        tprint("{} COS credentials _large...".format(tag))
        creds_l = get_cos_creds("{}/1/{}_large.png".format(main_job, pid), "_large")
        if creds_l is None:
            results[idx-1]=(False,"getCos _large fail"); return
        r_l = cos_put(session,"https://"+COS_HOST+ck_l,
                      png_b, mkhdr(creds_l,ck_l,png_b,"image/png"), "_large")
        if r_l is not None and r_l.status_code == 200:
            tprint("{} COS _large {} {:,}B".format(tag, ok("OK"), len(png_b)))
        else:
            tprint("{} {}".format(tag, warn("COS _large FAIL")))
        time.sleep(0.3)

        # B2. Upload .png (lay creds rieng)
        tprint("{} COS credentials .png...".format(tag))
        creds_p = get_cos_creds("{}/1/{}.png".format(main_job, pid), ".png")
        if creds_p is None:
            results[idx-1]=(False,"getCos .png fail"); return
        r2 = cos_put(session,"https://"+COS_HOST+ck,
                     png_b, mkhdr(creds_p,ck,png_b,"image/jpeg"), ".png")
        if r2 is None or r2.status_code != 200:
            tprint("{} {}".format(tag, err("COS .png FAIL")))
            results[idx-1]=(False,"COS .png fail"); return
        tprint("{} COS .png {} {:,}B".format(tag, ok("OK"), len(png_b)))

        sticker_url = CDN_BASE + ck

        # B3. GIF/MP4 animation upload
        if anim_b is not None and anim_ext:
            ck_a = "{}{}/1/{}.{}".format(user_path, main_job, pid, anim_ext)
            creds_a = get_cos_creds(
                "{}/1/{}.{}".format(main_job, pid, anim_ext), "."+anim_ext)
            if creds_a is not None:
                r_a = cos_put(session,"https://"+COS_HOST+ck_a,
                              anim_b, mkhdr(creds_a,ck_a,anim_b,"image/png"),
                              "."+anim_ext)
                if r_a is not None and r_a.status_code == 200:
                    sticker_url = CDN_BASE + ck_a
                    tprint("{} COS .{} {} {:,}B {}".format(
                        tag, anim_ext, ok("OK"), len(anim_b),
                        dim("(animation)")))
                else:
                    tprint("{} {}".format(
                        tag, warn(".{} FAIL → dung .png".format(anim_ext))))
            else:
                tprint("{} {}".format(
                    tag, warn("getCos .{} FAIL → dung .png".format(anim_ext))))

        time.sleep(0.5)

        # C-E. save
        pi = build_pic_info(pic_info_raw, bi_har, sticker_url,
                            main_job, gender,
                            nameplate_text, nameplate_picurl)

        rs = api_post(session,
                      "/api/game/poster/flowborn/savepostereditinfo",
                      {"mainJob":main_job,"picInfo":pi},
                      auth_token, encode_param, har_ua, har_sec_ch_ua,
                      retry_on_code1=True, max_retries=4, delay=4.0)
        tprint("{} editInfo {}".format(
            tag, ok("OK") if rs.get("code")==0 else warn("code={}".format(rs.get("code")))))
        time.sleep(1.5)

        rp = api_post(session,
                      "/api/game/poster/flowborn/saveposter",
                      {"posterId":pid,"isApply":True,"isShare":is_share,
                       "mainJob":main_job,"picInfo":pi,
                       "picUrl":CDN_BASE+user_path},
                      auth_token, encode_param, har_ua, har_sec_ch_ua,
                      retry_on_code1=True, max_retries=4, delay=4.0)

        unavail = (rp.get("data") or {}).get("unavailableResources",[])
        kind    = "{}GIF{}".format(C.CYAN,C.RESET) if anim_b else "IMG"

        if rp.get("code")==0 and not unavail:
            tprint("{} {} ID={}{}{}  [{}]".format(
                tag, ok("THANH CONG"), C.GREEN, pid, C.RESET, kind))
            results[idx-1]=(True, pid, sticker_url, kind)
        elif rp.get("code")==0:
            tprint("{} {} (co resource bi tu choi)".format(tag, ok("OK")))
            results[idx-1]=(True, pid, sticker_url, kind)
        else:
            tprint("{} {} {}".format(
                tag, err("THAT BAI"), rp.get("msg","")[:40]))
            results[idx-1]=(False,"saveposter: "+rp.get("msg","")[:40])

    except Exception as e:
        tprint("{} {}".format(tag, err("EXCEPTION: "+str(e)[:50])))
        results[idx-1]=(False,"exception: "+str(e)[:40])

# =============================================================================
# ACC WORKER  (1 acc / 1 thread)
# =============================================================================

def acc_worker(acc, media_list, rounds, is_share,
               nameplate_text, nameplate_picurl, mod_mode, acc_results):
    lbl  = acc["label"]
    har  = acc["har"]
    rc   = role_color(acc["main_job"], acc["gender"])

    tprint("\n" + sep(62, "═", C.PURPLE))
    tprint("{}{}  START  {}{}".format(C.PURPLE+C.BOLD, "▶", lbl, C.RESET))
    tprint(sep(62, "═", C.PURPLE))

    auth_token, encode_param, user_path, _mj_har, _gdr_har, bi_har, \
        har_ua, har_sec_ch_ua = parse_har(har)
    if not auth_token or not user_path:
        tprint(err("  [{}] Khong co token/path — bo qua".format(lbl)))
        acc_results[lbl]={"ok":0,"fail":0,"rounds":[]}; return
    if not encode_param:
        tprint(warn("  [{}] Khong co encodeparam — co the bi 403".format(lbl)))

    # Init sign bridge (getselfuserinfo -> setLoginRes)
    sess = make_session()
    bridge_ok = init_sign_bridge_for_acc(
        sess, auth_token, encode_param, har_ua, har_sec_ch_ua)
    if not bridge_ok:
        tprint(warn("  [{}] Sign bridge init FAIL — dung encodeparam tu HAR".format(lbl)))

    # Uu tien main_job/gender da duoc nguoi dung tuy chinh (neu co override)
    main_job = acc.get("main_job", _mj_har)
    gender   = acc.get("gender",   _gdr_har)

    tprint("  {}Vai tro : {}{}{}{} (job={} gender={})".format(
        C.GRAY, rc+C.BOLD, get_role_label(main_job,gender),
        C.RESET, C.GRAY, main_job, gender) + C.RESET)
    tprint(dim("  Token   : {}...".format(auth_token[:35])))
    tprint(dim("  COS     : {}".format(user_path)))

    sess = make_session()

    # COS credentials — lay trong poster_worker (can posterId + fileName)

    # Poster edit info
    tprint(info("  [1/2] Lay picInfo hien tai..."))
    r = api_post(sess,"/api/game/poster/flowborn/getpostereditinfo",
                 {"mainJob":main_job},auth_token, encode_param,
                 har_ua, har_sec_ch_ua)
    if (r.get("code")==0
            and (r.get("data") or {}).get("picInfo")):
        pic_info_raw = r["data"]["picInfo"] or {}
        if not bi_har:
            bi_har = pic_info_raw.get("baseInfo") or {}
        tprint(ok("  picInfo OK"))
    else:
        pic_info_raw = {}
        tprint(warn("  Dung cau hinh mac dinh"))
    time.sleep(0.5)

    # Validate nameplate
    np_url = nameplate_picurl
    if mod_mode == "2" and nameplate_text:
        tprint(info("  [2/2] Validate nameplate \"{}\"...".format(nameplate_text)))
        rc2 = api_post(sess,"/api/game/poster/flowborn/textsynccheck",
                       {"text":nameplate_text},auth_token, encode_param,
                       har_ua, har_sec_ch_ua)
        if rc2.get("code") != 0:
            tprint(warn("  Server tu choi ten → bo qua nameplate"))
            nameplate_text = None
        else:
            tprint(ok("  Ten hop le"))
            nr = api_post(sess,"/api/game/poster/flowborn/geteditorresource",
                          {"type":2,"mainJob":main_job,"page":1,"pageSize":20},
                          auth_token, encode_param, har_ua, har_sec_ch_ua)
            if nr.get("code")==0 and (nr.get("data") or {}).get("list"):
                np_url = (nr["data"]["list"][0]
                          .get("nameplate",{})
                          .get("picUrl") or NAMEPLATE_PICURL)

    # Apply composite nameplate
    working_media = []
    for m in media_list:
        if mod_mode == "2" and nameplate_text:
            new_png = composite_nameplate(m["png_bytes"], nameplate_text, sess)
            working_media.append({**m, "png_bytes": new_png})
        else:
            working_media.append(m)

    n_media    = len(working_media)
    total_ok   = total_fail = 0
    round_logs = []

    for rnd in range(1, rounds+1):
        tprint("")
        tprint("{}  [{}] Vong {:02d}/{:02d}  —  {} media song song{}".format(
            C.CYAN+C.BOLD, lbl[:16], rnd, rounds, n_media, C.RESET))

        results = [None]*n_media
        threads = []
        for i, m in enumerate(working_media, 1):
            t = threading.Thread(
                target=poster_worker,
                args=(i, lbl, auth_token, encode_param, user_path,
                      main_job, gender, bi_har,
                      m, pic_info_raw, is_share,
                      nameplate_text, np_url,
                      har_ua, har_sec_ch_ua, results),
                daemon=True,
            )
            threads.append(t)

        for t in threads:
            t.start()
            # ---- 3.6s stagger giua moi poster de fix -1999 frequency limited ----
            time.sleep(POSTER_STAGGER)

        for t in threads:
            t.join()

        ok_n  = sum(1 for res in results if res and res[0])
        fail_n= n_media - ok_n
        total_ok   += ok_n
        total_fail += fail_n
        round_logs.append((rnd, results))

        summary = "{} OK  {} FAIL".format(
            "{}{}{}".format(C.GREEN, ok_n,   C.RESET),
            "{}{}{}".format(C.RED,   fail_n, C.RESET))
        tprint("  {}[{}] Vong {:02d}: {}{}".format(
            C.BOLD, lbl[:16], rnd, summary, C.RESET))

        if rnd < rounds:
            tprint(dim("  [{}] Nghi {}s truoc vong tiep...".format(
                lbl[:16], ROUND_DELAY)))
            time.sleep(ROUND_DELAY)

    # Tong ket acc
    tprint("")
    tprint("{}┌─ DONE: {} {}".format(C.GREEN+C.BOLD, lbl, C.RESET))
    for rnd, results in round_logs:
        for i, res in enumerate(results,1):
            g = (rnd-1)*n_media+i
            if res and res[0]:
                kind = res[3] if len(res)>3 else "?"
                tprint("{}│{}  V{:02d}#{:02d} {}  [{}]  ID={}".format(
                    C.GREEN, C.RESET, rnd, g, ok("OK"), kind, res[1]))
            else:
                msg = str(res[1])[:35] if res else "?"
                tprint("{}│{}  V{:02d}#{:02d} {}  {}".format(
                    C.GREEN, C.RESET, rnd, g, err("FAIL"), msg))
    tprint("{}└─ OK:{} {}{}{}  FAIL:{} {}{}{}  TONG:{}{}".format(
        C.GREEN,
        C.RESET, C.GREEN+C.BOLD, total_ok,   C.RESET,
        C.RESET, C.RED+C.BOLD,   total_fail, C.RESET,
        C.BOLD, rounds*n_media) + C.RESET)

    acc_results[lbl]={"ok":total_ok,"fail":total_fail,"rounds":round_logs}

# =============================================================================
# BOOST WORKER
# =============================================================================

def boost_worker(acc_lbl, auth_token, encode_param,
                 har_ua, har_sec_ch_ua,
                 poster_id, role_id,
                 count, delay_s, boost_results):
    session = make_session()
    tprint(info("[{}] Boost {}x  delay={}s".format(acc_lbl, count, delay_s)))
    ok_n=fail_n=0
    for i in range(1,count+1):
        rc = api_post(session,
                      "/api/game/poster/flowborn/getposterunusableresource",
                      {"posterId":poster_id,"roleId":role_id},
                      auth_token, encode_param, har_ua, har_sec_ch_ua)
        if rc.get("data",{}).get("unavailableResources"):
            tprint(warn("[{}][{}] Poster bi khoa — dung".format(acc_lbl,i))); break
        r = api_post(session,
                     "/api/game/poster/flowborn/quickapplyposter",
                     {"posterId":poster_id,"roleId":role_id},
                     auth_token, encode_param, har_ua, har_sec_ch_ua)
        if r.get("code")==0:
            ok_n+=1
            tprint(ok("[{}][{}] OK  (tong={})".format(acc_lbl,i,ok_n)))
        else:
            fail_n+=1
            tprint(err("[{}][{}] FAIL  code={}  msg={}".format(
                acc_lbl,i,r.get("code"),r.get("msg",""))))
            if fail_n>=3:
                tprint(warn("[{}] 3 fail lien tiep — dung".format(acc_lbl))); break
        time.sleep(delay_s)
    tprint("{}[{}] Boost xong: {} ok  {} fail{}".format(
        C.BOLD, acc_lbl, ok_n, fail_n, C.RESET))
    boost_results[acc_lbl]={"ok":ok_n,"fail":fail_n}

# =============================================================================
# MAIN
# =============================================================================

def run(har_path_arg, image_dir, rounds_arg):
    # Banner
    print("")
    print("{}{}".format(C.PURPLE, "═"*62))
    print("{}  Flowborn Poster Tool v1.3          by beterHa90  ".format(
        C.WHITE+C.BOLD))
    print("{}  JPG · PNG · WEBP · GIF · MP4  |  Dynamic Sign  ".format(C.CYAN))
    print("{}{}".format(C.PURPLE, "═"*62) + C.RESET)

    print("\n" + info("Kiem tra license..."))
    _sess = _0xD4()
    if not _sess:
        print(err("Khong co license hop le!"))
        sys.exit(1)
    global API_BASE
    API_BASE = _sess['ep']

    print("\n" + info("Kiem tra ket noi..."))
    if not check_connectivity():
        print(err("Khong co ket noi internet!")); sys.exit(1)
    print(ok("Mang OK"))

    # ---- Khoi dong Sign Bridge (tao encodeparam moi moi request) ----
    bridge_ok = start_sign_bridge()
    if not bridge_ok:
        print(warn("Sign bridge KHONG HOAT DONG."))
        print(warn("Se dung encodeparam tu HAR (co the bi -5001:auth failed)."))
        print(info("De fix: cai Node.js (pkg install nodejs) va dat sign_bridge.js cung thu muc."))

    # ---- Tim HAR ----
    use_one = (har_path_arg and har_path_arg != DEFAULT_HAR
               and os.path.exists(har_path_arg))
    if use_one:
        har_files = [Path(har_path_arg)]
    else:
        har_files = find_har_files(".")
        if not har_files and os.path.exists(DEFAULT_HAR):
            har_files = [Path(DEFAULT_HAR)]
    har_files = [h for h in har_files if h.exists()]

    if not har_files:
        print(err("Khong tim thay .har nao!")); sys.exit(1)

    # ---- Parse + hien thi ----
    print("\n" + bold("Phan tich {} file HAR:".format(len(har_files))))
    print("  {}{:<28}  {:<22}  {}{}".format(
        C.GRAY, "File", "Vai tro", "Trang thai", C.RESET))
    print("  " + sep(58, "─", C.GRAY))
    acc_info = []
    for idx_h, h in enumerate(har_files, 1):
        tok,ep,upath,mj,gdr,bi,h_ua,h_sec = parse_har(str(h))
        role   = get_role_label(mj,gdr)
        rc     = role_color(mj,gdr)
        status = ok("OK") if (tok and upath) else err("THIEU TOKEN/PATH")
        lbl    = "{} [{}]".format(h.stem, role)
        print("  {}{:02d}.{} {:<25}  {}{:<22}{}  {}".format(
            C.YELLOW, idx_h, C.RESET,
            h.name[:25],
            rc+C.BOLD, role, C.RESET,
            status))
        acc_info.append({
            "har":str(h), "token":tok, "encode_param":ep,
            "user_path":upath,
            "main_job":mj, "gender":gdr, "baseInfo":bi, "label":lbl,
            "har_ua":h_ua, "har_sec_ch_ua":h_sec
        })

    valid = [a for a in acc_info if a["token"] and a["user_path"]]
    if not valid:
        print(err("Khong co acc nao hop le!")); sys.exit(1)

    # ---- Chon acc ----
    selected = valid
    if len(valid) > 1:
        print("")
        print("  {}Nhap 'all' / ENTER = dung TAT CA {} acc{}".format(
            C.CYAN, len(valid), C.RESET))
        print("  {}Nhap STT cach nhau (vd: 1 3) = chon rieng{}".format(
            C.GRAY, C.RESET))
        raw = cinput("  > ")

        if raw and raw.lower() != "all":
            try:
                idxs = [int(x)-1 for x in raw.split()]
                sel  = [acc_info[i] for i in idxs
                        if 0<=i<len(acc_info) and acc_info[i]["token"]]
                if sel: selected = sel
                else: print(warn("Khong hop le → Dung tat ca"))
            except Exception:
                print(warn("Nhap sai → Dung tat ca"))

    n_acc = len(selected)
    print("\n  {} acc se chay {}SONG SONG{}:".format(
        n_acc, C.GREEN+C.BOLD, C.RESET))
    for a in selected:
        rc = role_color(a["main_job"], a["gender"])
        print("    {}●{} {}{}{}".format(
            rc, C.RESET, rc, a["label"], C.RESET))

    # ---- Tuy chinh lane / gioi tinh? ----
    LANE_NAMES = {
        "1": "Assassin", "2": "Tank",   "3": "Support",
        "4": "Mid",      "5": "Ad",     "6": "Jungle",
    }
    GENDER_NAMES = {"1": "Nam", "2": "Nu"}

    print("")
    ov = cinput(
        "  {}Ban muon chon lane / gioi tinh khac khong?{} (y/n, ENTER=n): ".format(
            C.CYAN, C.RESET))
    if ov.lower() == "y":
        print("\n" + bold("  Tuy chinh lane:"))
        for k, v in LANE_NAMES.items():
            rc2 = role_color(int(k), 1)
            print("    {}[{}]{} {}{}{}".format(
                C.YELLOW+C.BOLD, k, C.RESET, rc2, v, C.RESET))
        while True:
            raw_job = cinput("  Chon lane (1-6): ")
            if raw_job in LANE_NAMES:
                break
            print(warn("Vui long nhap so tu 1 den 6"))

        print("\n" + bold("  Tuy chinh gioi tinh:"))
        print("    {}[1]{} Nam  {}[2]{} Nu".format(
            C.YELLOW+C.BOLD, C.RESET, C.YELLOW+C.BOLD, C.RESET))
        while True:
            raw_gdr = cinput("  Chon gioi tinh (1/2): ")
            if raw_gdr in ("1", "2"):
                break
            print(warn("Vui long nhap 1 (Nam) hoac 2 (Nu)"))

        new_job = int(raw_job)
        new_gdr = int(raw_gdr)
        new_role_lbl = get_role_label(new_job, new_gdr)
        print(ok("  → {}{}{}".format(
            role_color(new_job, new_gdr)+C.BOLD, new_role_lbl, C.RESET)))

        for a in selected:
            old_stem = Path(a["har"]).stem
            a["main_job"] = new_job
            a["gender"]   = new_gdr
            a["label"]    = "{} [{}]".format(old_stem, new_role_lbl)

        print("\n  {} acc sau khi doi:".format(n_acc))
        for a in selected:
            rc3 = role_color(a["main_job"], a["gender"])
            print("    {}●{} {}{}{}".format(
                rc3, C.RESET, rc3, a["label"], C.RESET))

    # ---- Chuc nang ----
    main_mode = ask_choice(
        "Chon chuc nang:",
        {"1":"{}Mod media poster{} (JPG / PNG / GIF / MP4)".format(
            C.GREEN+C.BOLD, C.RESET),
         "2":"{}Tang luot dung nen{} (Boost)".format(
            C.YELLOW+C.BOLD, C.RESET)}
    )

    # ===========================================================
    # BOOST
    # ===========================================================
    if main_mode == "2":
        print("\n" + bold("Nhap thong tin poster:"))
        poster_id = cinput("  PosterId  : ")
        role_id   = cinput("  RoleId    : ")
        try:
            count = int(cinput("  So lan    : "))
            d     = cinput("  Delay giay [mac dinh 1.0]: ")
            delay_s = float(d) if d else 1.0
        except ValueError:
            print(err("Nhap sai")); sys.exit(1)

        boost_results = {}
        threads = [threading.Thread(
            target=boost_worker,
            args=(a["label"],a["token"],a.get("encode_param"),
                  a.get("har_ua"),a.get("har_sec_ch_ua"),
                  poster_id,role_id,
                  count,delay_s,boost_results),
            daemon=True,
        ) for a in selected]

        print("\n" + bold("Bat dau boost {} acc SONG SONG...".format(n_acc)))
        for t in threads: t.start()
        for t in threads: t.join()

        print("\n" + sep(62, "═", C.PURPLE))
        print("{}  BOOST TONG KET  ({} acc song song){}".format(
            C.WHITE+C.BOLD, n_acc, C.RESET))
        print(sep(62, "─", C.GRAY))
        grand_ok=grand_fail=0
        for lbl,res in boost_results.items():
            print("  {:<32}  {}OK:{:<5}{}  {}FAIL:{}{}".format(
                lbl[:32],
                C.GREEN, res["ok"],   C.RESET,
                C.RED,   res["fail"], C.RESET))
            grand_ok+=res["ok"]; grand_fail+=res["fail"]
        print(sep(62, "─", C.GRAY))
        print("  {}TONG: OK={}  FAIL={}{}".format(
            C.BOLD, grand_ok, grand_fail, C.RESET))
        print(sep(62, "═", C.PURPLE))
        return

    # ===========================================================
    # MOD POSTER
    # ===========================================================

    print("\n" + info("Quet media trong: " + image_dir))
    all_files = scan_media(image_dir)
    print("  Tim thay {} file:".format(len(all_files)))
    TYPE_COLORS = {
        ".jpg":"{}JPG{}".format(C.YELLOW,C.RESET),
        ".jpeg":"{}JPG{}".format(C.YELLOW,C.RESET),
        ".png":"{}PNG{}".format(C.CYAN,C.RESET),
        ".webp":"{}WEBP{}".format(C.CYAN,C.RESET),
        ".gif":"{}GIF{}".format(C.GREEN+C.BOLD,C.RESET),
        ".mp4":"{}MP4{}".format(C.PURPLE+C.BOLD,C.RESET),
    }
    for i,p in enumerate(all_files,1):
        tc = TYPE_COLORS.get(p.suffix.lower(), p.suffix.upper())
        print("  {}[{}]{}  {}  {}  {:.1f} KB".format(
            C.YELLOW, i, C.RESET,
            tc, p.name,
            p.stat().st_size/1024))

    # Phan cong anh
    if len(all_files)==1:
        img_mode="2"
        print("\n" + info("1 file duy nhat → tat ca acc dung chung."))
    else:
        if len(all_files) < n_acc:
            print("\n" + warn("{} file < {} acc — mode 1 se lap vong anh.".format(
                len(all_files), n_acc)))
        img_mode = ask_choice(
            "Che do phan cong media:",
            {"1":"Moi acc {}1 bo rieng{}  (acc1→file1, acc2→file2, ...)".format(
                C.BOLD, C.RESET),
             "2":"Tat ca acc dung {}chung{}  (toi da {} file/acc)".format(
                C.BOLD, C.RESET, MAX_MEDIA_PER_ACC)}
        )

    if img_mode=="1":
        print("\n  Phan cong (rieng):")
        for i,a in enumerate(selected):
            f  = all_files[i % len(all_files)]
            rc = role_color(a["main_job"],a["gender"])
            print("    {}{}{}  →  {}".format(rc, a["label"][:30], C.RESET, f.name))
    else:
        shared = all_files[:MAX_MEDIA_PER_ACC]
        print("\n" + info("Dung chung {} file: {}".format(
            len(shared), ", ".join(p.name for p in shared))))

    # Che do luu
    save_mode = ask_choice(
        "Che do LUU poster:",
        {"1":"{}Luu rieng{}  (chi minh toi dung)".format(C.CYAN,C.RESET),
         "2":"{}Quang truong{}  (moi nguoi thay)".format(C.YELLOW,C.RESET)}
    )
    is_share = (save_mode=="2")

    # Che do MOD
    mod_mode = ask_choice(
        "Che do MOD:",
        {"1":"Chi mod media",
         "2":"Mod media + {}composite ten nhan vat{}  (can Pillow)".format(
             C.CYAN, C.RESET)}
    )
    nameplate_text   = None
    nameplate_picurl = NAMEPLATE_PICURL
    if mod_mode=="2":
        if not PILLOW_OK:
            print(warn("pip install Pillow → Bo qua nameplate."))
            mod_mode="1"
        else:
            nameplate_text = cinput("\n  Ten nhan vat: ")
            if not nameplate_text:
                print(warn("Ten trong → bo qua")); mod_mode="1"

    # So vong
    if rounds_arg:
        rounds = max(1, rounds_arg)
    else:
        raw = cinput("\n  So vong lap (moi vong = {}s stagger/poster, ENTER=1): ".format(
            POSTER_STAGGER))
        try:
            rounds = int(raw) if raw else 1
            rounds = max(1, rounds)
        except ValueError:
            rounds = 1

    if img_mode=="1":
        grand_total = rounds * n_acc
    else:
        imgs_per    = min(len(all_files), MAX_MEDIA_PER_ACC)
        grand_total = rounds * imgs_per * n_acc

    print("\n  {} acc  ×  {} vong  ≈  {}{}{}  poster tong".format(
        n_acc, rounds, C.GREEN+C.BOLD, grand_total, C.RESET))
    print(dim("  Stagger poster: {}s  |  Delay vong: {}s  |  Stagger acc: {}s".format(
        POSTER_STAGGER, ROUND_DELAY, ACC_STAGGER)))

    # Pre-process media
    print("\n" + info("Xu ly media truoc khi chay..."))
    shared_media_list = None
    if img_mode=="2":
        shared_files = all_files[:MAX_MEDIA_PER_ACC]
        shared_media_list = []
        for p in shared_files:
            print(info("  Xu ly: {}".format(p.name)))
            shared_media_list.append(prepare_media(p))

    acc_media_map = {}
    for i,a in enumerate(selected):
        lbl = a["label"]
        if img_mode=="1":
            f = all_files[i % len(all_files)]
            print(info("  {} → {}".format(lbl[:25], f.name)))
            acc_media_map[lbl] = [prepare_media(f)]
        else:
            acc_media_map[lbl] = shared_media_list

    # Confirm
    confirm = cinput("\n  Nhap 'ok' de bat dau, Ctrl+C de huy: ")
    if confirm.lower() != "ok":
        print(err("Huy")); sys.exit(0)

    # ===========================================================
    # SPAWN ACC THREADS — tat ca song song
    # ===========================================================
    acc_results = {}
    threads     = []

    print("\n" + bold("Bat dau {} acc SONG SONG...".format(n_acc)))
    for a in selected:
        t = threading.Thread(
            target=acc_worker,
            args=(a, acc_media_map[a["label"]],
                  rounds, is_share,
                  nameplate_text, nameplate_picurl, mod_mode,
                  acc_results),
            daemon=True,
        )
        threads.append(t)

    for t in threads:
        t.start()
        time.sleep(ACC_STAGGER)   # stagger khoi dong acc

    for t in threads:
        t.join()

    # ===========================================================
    # TONG KET CUOI
    # ===========================================================
    print("")
    print(sep(62, "═", C.PURPLE))
    print("{}  TONG KET  ({} acc song song){}".format(
        C.WHITE+C.BOLD, n_acc, C.RESET))
    print(sep(62, "─", C.GRAY))
    grand_ok=grand_fail=0
    for a in selected:
        res = acc_results.get(a["label"],{"ok":0,"fail":0})
        ok_a,fail_a = res["ok"],res["fail"]
        grand_ok+=ok_a; grand_fail+=fail_a
        rc = role_color(a["main_job"],a["gender"])
        print("  {}{:<30}{}  {}OK:{:<4}{}  {}FAIL:{:<4}{}  TONG:{}".format(
            rc, a["label"][:30], C.RESET,
            C.GREEN, ok_a,   C.RESET,
            C.RED,   fail_a, C.RESET,
            ok_a+fail_a))
    print(sep(62, "─", C.GRAY))
    print("  {}TONG CONG:  OK={}{}{}  FAIL={}{}{}  /  {} poster{}".format(
        C.BOLD,
        C.GREEN, grand_ok,   C.RESET+C.BOLD,
        C.RED,   grand_fail, C.RESET+C.BOLD,
        grand_total, C.RESET))
    print(sep(62, "═", C.PURPLE))
    print("\n  {}Mo game → Flowborn Poster de thay sticker custom!{}\n".format(
        C.CYAN, C.RESET))

    if grand_ok > 0:
        _0xD3(_0xD2() + 1)
    stop_sign_bridge()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Flowborn Poster Tool v1.3 by beterHa90",formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--har",default=DEFAULT_HAR)
    ap.add_argument("--dir",default=".")
    ap.add_argument("--rounds",type=int,default=None)
    ap.add_argument("--test-sign",action="store_true",help="Test sign bridge")
    ap.add_argument("--device-id",action="store_true",help="Show Device ID")
    args = ap.parse_args()

    if args.device_id:
        did = _0xD1()
        print(f"\n  Device ID: {did}\n")
        print(f"  Dang ky tai: https://longbmtgithub.github.io/FlowbornPosterTool/buy.html")
        sys.exit(0)

    if args.test_sign:
        print(bold("=== TEST SIGN BRIDGE ==="))
        ok_flag = start_sign_bridge()
        if ok_flag:
            print(ok("Sign bridge san sang!"))
            # Tim HAR de lay token
            har_files = sorted(Path(".").glob("*.har"))
            if not har_files:
                print(err("Khong tim thay file .har de test"))
                stop_sign_bridge()
                sys.exit(1)
            h = har_files[0]
            print(info("Dung HAR: {}".format(h.name)))
            tok, ep, upath, mj, gdr, bi, h_ua, h_sec = parse_har(str(h))
            if not tok:
                print(err("Khong co token trong HAR"))
                stop_sign_bridge()
                sys.exit(1)
            # Init sign bridge voi getselfuserinfo
            sess = make_session()
            init_ok = init_sign_bridge_for_acc(
                sess, tok, ep, h_ua, h_sec)
            if init_ok:
                print(ok("Init OK! Thu tao 3 encodeparam..."))
                for i in range(3):
                    fresh_ep = get_fresh_encodeparam("{}", "")
                    if fresh_ep:
                        print(ok("  #{}: {} (len={})".format(
                            i+1, fresh_ep[:40]+"...", len(fresh_ep))))
                    else:
                        print(err("  #{}: FAIL".format(i+1)))
            else:
                print(err("Init FAIL!"))
                print(info("Token co the het han - capture HAR moi"))
        else:
            print(err("Sign bridge KHONG hoat dong!"))
            print(info("Kiem tra:"))
            print(info("  1. node --version"))
            print(info("  2. node sign_bridge.js --test"))
        stop_sign_bridge()
        sys.exit(0 if ok_flag else 1)

    try:
        run(args.har, args.dir, args.rounds)
    finally:
        stop_sign_bridge()

