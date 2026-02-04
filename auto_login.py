#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lunes Host Auto Keepalive - Universal Version
Supports custom server URLs and 2FA
"""

import os
import sys
import re
import time
import requests

# Try to import cloudscraper for Cloudflare bypass
try:
    import cloudscraper
    USE_CLOUDSCRAPER = True
    print("✅ Using cloudscraper to bypass Cloudflare")
except ImportError:
    USE_CLOUDSCRAPER = False
    print("⚠️ cloudscraper not installed, using standard requests")

# Configuration from environment variables
LUNES_EMAIL = os.environ.get('LUNES_EMAIL')
LUNES_PASSWORD = os.environ.get('LUNES_PASSWORD')
LUNES_SERVER_URL = os.environ.get('LUNES_SERVER_URL')  # Custom server URL
TG_BOT_TOKEN = os.environ.get('TG_BOT_TOKEN')
TG_CHAT_ID = os.environ.get('TG_CHAT_ID')

# Default URLs
BASE_URL = "https://ctrl.lunes.host"
LOGIN_URL = f"{BASE_URL}/auth/login"
DASHBOARD_URL = f"{BASE_URL}/dashboard"

# Use custom server URL if provided, otherwise use dashboard
KEEPALIVE_URL = LUNES_SERVER_URL if LUNES_SERVER_URL else DASHBOARD_URL

def send_tg_message(message):
    """Send Telegram notification"""
    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": TG_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        requests.post(url, data=data, timeout=10)
    except:
        pass

def create_session():
    """Create session with cloudscraper or requests"""
    if USE_CLOUDSCRAPER:
        session = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
    else:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    return session

def wait_for_2fa_code(timeout=60):
    """Wait for 2FA code via Telegram"""
    print(f"Waiting for 2FA code ({timeout}s)...")
    print("Please send in Telegram: /code 123456")
    
    start_time = time.time()
    last_update_id = None
    
    while time.time() - start_time < timeout:
        try:
            url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/getUpdates"
            params = {"offset": last_update_id, "limit": 10} if last_update_id else {"limit": 10}
            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()
            
            if data.get("ok") and data.get("result"):
                for update in data["result"]:
                    last_update_id = update["update_id"] + 1
                    
                    if "message" not in update:
                        continue
                    
                    message = update["message"]
                    chat_id = message["chat"]["id"]
                    
                    if str(chat_id) != str(TG_CHAT_ID):
                        continue
                    
                    text = message.get("text", "")
                    
                    if text.startswith("/code "):
                        code = text.replace("/code ", "").strip()
                        if code.isdigit() and len(code) == 6:
                            print(f"✅ Received 2FA code: {code}")
                            return code
        except:
            pass
        
        time.sleep(3)
    
    print("❌ 2FA code timeout")
    return None

def login_lunes():
    """Login to Lunes Host"""
    session = create_session()
    
    try:
        print("=" * 60)
        print("Lunes Host Auto Keepalive")
        print(f"Using: {'cloudscraper' if USE_CLOUDSCRAPER else 'requests'}")
        print(f"Target: {KEEPALIVE_URL}")
        print("=" * 60)
        
        # Validate configuration
        if not LUNES_EMAIL or not LUNES_PASSWORD:
            print("❌ Error: Missing LUNES_EMAIL or LUNES_PASSWORD")
            send_tg_message("❌ <b>Lunes Keepalive Failed</b>\nMissing credentials")
            return False
        
        if not LUNES_SERVER_URL:
            print("⚠️ Warning: LUNES_SERVER_URL not set, using dashboard")
        
        print(f"\nEmail: {LUNES_EMAIL[:3]}***")
        
        # Add delay to appear more human-like
        print("\n[1/4] Initializing...")
        time.sleep(2)
        
        # 1. Visit login page
        print("\n[2/4] Visiting login page...")
        try:
            login_page = session.get(LOGIN_URL, timeout=30)
            print(f"Status: {login_page.status_code}")
            
            if login_page.status_code == 403:
                print("❌ 403 Forbidden - Blocked by Cloudflare")
                send_tg_message("❌ <b>Lunes Keepalive Failed</b>\n403 Forbidden")
                return False
        except Exception as e:
            print(f"❌ Failed to access login page: {e}")
            send_tg_message(f"❌ <b>Lunes Keepalive Failed</b>\n{e}")
            return False
        
        # 2. Extract CSRF token
        print("\n[3/4] Extracting CSRF Token...")
        csrf_token = None
        patterns = [
            r'name=["\']_token["\']\s+value=["\']([^"\']+)["\']',
            r'name=["\']csrf[_-]token["\']\s+value=["\']([^"\']+)["\']',
            r'value=["\']([^"\']+)["\']\s+name=["\']_token["\']',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, login_page.text)
            if match:
                csrf_token = match.group(1)
                print(f"✅ Found CSRF token")
                break
        
        if not csrf_token:
            print("⚠️ CSRF token not found, trying without it")
        
        time.sleep(1)
        
        # 3. Submit login
        print("\n[4/4] Submitting login...")
        
        login_data = {
            'email': LUNES_EMAIL,
            'password': LUNES_PASSWORD,
        }
        if csrf_token:
            login_data['_token'] = csrf_token
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': LOGIN_URL,
            'Origin': BASE_URL,
        }
        
        login_resp = session.post(
            LOGIN_URL,
            data=login_data,
            headers=headers,
            timeout=30,
            allow_redirects=True
        )
        
        print(f"Status: {login_resp.status_code}")
        print(f"URL: {login_resp.url}")
        
        # Check if 2FA is required
        if '2fa' in login_resp.url.lower() or 'two-factor' in login_resp.text.lower():
            print("🔐 2FA required")
            send_tg_message("🔐 <b>2FA Code Required</b>\nPlease send: /code 123456")
            
            code = wait_for_2fa_code(timeout=60)
            if not code:
                send_tg_message("❌ <b>Lunes Keepalive Failed</b>\n2FA timeout")
                return False
            
            # Submit 2FA
            twofa_data = {'code': code}
            if csrf_token:
                twofa_data['_token'] = csrf_token
            
            twofa_resp = session.post(
                login_resp.url,
                data=twofa_data,
                headers=headers,
                timeout=30,
                allow_redirects=True
            )
            print(f"After 2FA: {twofa_resp.status_code} - {twofa_resp.url}")
        
        # Verify login
        print("\nVerifying login...")
        dashboard_resp = session.get(DASHBOARD_URL, timeout=30)
        print(f"Dashboard: {dashboard_resp.status_code}")
        
        if dashboard_resp.status_code == 200 and 'auth/login' not in dashboard_resp.url:
            print("✅ Login successful!")
            
            # Visit the target server page
            print(f"\nVisiting keepalive target: {KEEPALIVE_URL}")
            try:
                keepalive_resp = session.get(KEEPALIVE_URL, timeout=30)
                print(f"Server page status: {keepalive_resp.status_code}")
                
                if keepalive_resp.status_code == 200:
                    print("✅ Server page visited successfully!")
                else:
                    print(f"⚠️ Server page returned: {keepalive_resp.status_code}")
            except Exception as e:
                print(f"⚠️ Failed to visit server page: {e}")
            
            # Visit additional pages for activity
            for page in ['/servers', '/account']:
                try:
                    session.get(f"{BASE_URL}{page}", timeout=10)
                    time.sleep(1)
                except:
                    pass
            
            print("\n" + "=" * 60)
            print("✅ Keepalive completed!")
            print("=" * 60)
            
            send_tg_message(f"✅ <b>Lunes Host Keepalive Success</b>\nVisited: {KEEPALIVE_URL}")
            return True
        else:
            print(f"❌ Login failed: {dashboard_resp.url}")
            send_tg_message("❌ <b>Lunes Keepalive Failed</b>\nCannot access Dashboard")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        send_tg_message(f"❌ <b>Error</b>\n{str(e)}")
        return False

if __name__ == "__main__":
    success = login_lunes()
    sys.exit(0 if success else 1)