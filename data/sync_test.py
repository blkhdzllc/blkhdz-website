import os
import json
import requests
import base64

# --- SETTINGS ---
EPN_CAMPAIGN_ID = "5339141674" 
SELLER_ID = "reedpb"

# NPW Fix: Ensures path accuracy whether run by bot or human
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SANDBOX_DIR = os.path.join(base_dir, "data", "test")
os.makedirs(SANDBOX_DIR, exist_ok=True)

def get_ebay_token():
    client_id = os.environ.get("APP_ID")
    client_secret = os.environ.get("CERT_ID")
    if not client_id or not client_secret: return None
    auth_str = f"{client_id}:{client_secret}"
    encoded_auth = base64.b64encode(auth_str.encode()).decode()
    url = "https://api.ebay.com/identity/v1/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded", "Authorization": f"Basic {encoded_auth}"}
    data = {"grant_type": "client_credentials", "scope": "https://api.ebay.com/oauth/api_scope"}
    try:
        response = requests.post(url, headers=headers, data=data)
        return response.json().get("access_token")
    except: return None

def sync_sandbox(query, filename):
    token = get_ebay_token()
    if not token: return
    url = f"https://api.ebay.com/buy/browse/v1/item_summary/search?q={query}&filter=sellers:{{{SELLER_ID}}}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers)
        target_path = os.path.join(SANDBOX_DIR, filename)
        with open(target_path, "w") as f:
            json.dump(response.json(), f, indent=4)
        print(f"Sandbox Sync: {filename} saved to {target_path}")
    except Exception as e: print(f"Failed: {e}")

if __name__ == "__main__":
    sync_sandbox("LEGO", "inventory.json")
    sync_sandbox("Diecast", "diecast.json")
