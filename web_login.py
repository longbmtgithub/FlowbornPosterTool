#!/usr/bin/env python3
"""
Flowborn Poster Tool - Web License Wrapper
Dùng cho Cloud Shell: kiểm tra license bằng username thay vì Device ID
"""
import hashlib, json, os, sys, getpass

try:
    import requests
except ImportError:
    os.system('pip install requests Pillow -q')
    import requests

LICENSE_URL = "https://gist.githubusercontent.com/longbmtgithub/a104c4c7c27608d9420e7ce94578b56c/raw/licenses.json"
CRED_FILE = os.path.expanduser("~/.fp_web_cred")

def sha256(s):
    return hashlib.sha256(s.encode()).hexdigest()

def load_cred():
    if os.path.isfile(CRED_FILE):
        try:
            with open(CRED_FILE) as f:
                d = json.load(f)
                return d.get('user'), d.get('hash')
        except:
            pass
    return None, None

def save_cred(user, h):
    with open(CRED_FILE, 'w') as f:
        json.dump({'user': user, 'hash': h}, f)

def check_web_license():
    """Check license by username account"""
    saved_user, saved_hash = load_cred()
    
    if saved_user and saved_hash:
        print(f"\033[96m  > Dang nhap tu dong: {saved_user}\033[0m")
        user, phash = saved_user, saved_hash
    else:
        print("\033[93m  === DANG NHAP ===\033[0m")
        print("\033[90m  Dang ky tai: https://longbmtgithub.github.io/FlowbornPosterTool/buy.html\033[0m")
        user = input("  Username: ").strip().lower()
        pwd = getpass.getpass("  Password: ").strip()
        if not user or not pwd:
            print("\033[91m  [!] Nhap day du thong tin!\033[0m")
            return False
        phash = sha256(pwd + '_fp_salt_' + user)
    
    # Fetch licenses
    print("\033[90m  > Kiem tra license...\033[0m")
    try:
        r = requests.get(LICENSE_URL, timeout=10)
        data = r.json()
    except:
        print("\033[91m  [!] Khong ket noi duoc server license!\033[0m")
        return False
    
    accounts = data.get('accounts', {})
    acc = accounts.get(user)
    
    if not acc:
        print(f"\033[91m  [!] Tai khoan '{user}' khong ton tai!\033[0m")
        print("\033[90m  Dang ky tai: https://longbmtgithub.github.io/FlowbornPosterTool/buy.html\033[0m")
        if os.path.isfile(CRED_FILE):
            os.remove(CRED_FILE)
        return False
    
    if acc.get('pass') != phash:
        print("\033[91m  [!] Sai mat khau!\033[0m")
        if os.path.isfile(CRED_FILE):
            os.remove(CRED_FILE)
        return False
    
    # Save cred for auto-login
    save_cred(user, phash)
    
    # Check devices/licenses linked to account
    devices = acc.get('devices', [])
    licenses = data.get('licenses', {})
    
    # Check if any device has valid license
    has_valid = False
    for did in devices:
        lic = licenses.get(did, {})
        if isinstance(lic, dict):
            exp = lic.get('expires', '')
            if exp:
                from datetime import datetime
                try:
                    if datetime.strptime(exp, '%Y-%m-%d') >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
                        has_valid = True
                        max_uses = lic.get('max', 0)
                        name = lic.get('name', '')
                        if '[CHO THANH TOAN]' in name:
                            continue
                        print(f"\033[92m  ✓ License: {did} ({max_uses} luot, het han {exp})\033[0m")
                        break
                except:
                    has_valid = True
                    break
            else:
                has_valid = True
                break
    
    # Also check free key *
    free = licenses.get('*', {})
    if isinstance(free, dict):
        exp = free.get('expires', '')
        if exp:
            from datetime import datetime
            try:
                if datetime.strptime(exp, '%Y-%m-%d') >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
                    has_valid = True
                    print(f"\033[92m  ✓ Free key: {free.get('max',0)} luot, het han {exp}\033[0m")
            except:
                pass
    
    # Check web_licenses (account-based, no device needed)
    web_lics = data.get('web_licenses', {})
    web_lic = web_lics.get(user)
    if isinstance(web_lic, dict):
        exp = web_lic.get('expires', '')
        if exp:
            from datetime import datetime
            try:
                if datetime.strptime(exp, '%Y-%m-%d') >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
                    has_valid = True
                    print(f"\033[92m  ✓ Web License: {web_lic.get('max',999)} luot, het han {exp}\033[0m")
            except:
                pass
        else:
            has_valid = True
    
    if not has_valid:
        print("\033[91m  [!] Khong co license hop le!\033[0m")
        print("\033[93m  Mua key tai: https://longbmtgithub.github.io/FlowbornPosterTool/buy.html\033[0m")
        return False
    
    print(f"\033[92m  ✓ Xin chao, {acc.get('name', user)}!\033[0m")
    return True

if __name__ == '__main__':
    # When run directly, check license then exec main tool
    if '--help' in sys.argv or '-h' in sys.argv:
        os.execvp(sys.executable, [sys.executable, 'flowborn_poster.py'] + sys.argv[1:])
    
    if not check_web_license():
        sys.exit(1)
    
    # Remove license-related args, pass rest to main tool
    # Set env var to skip device license check in main tool
    os.environ['FP_WEB_AUTH'] = '1'
    os.execvp(sys.executable, [sys.executable, 'flowborn_poster.py'] + sys.argv[1:])
