import os
import json
import requests
import base64

# --- SETTINGS ---
EPN_CAMPAIGN_ID = "5339141674" 
SELLER_ID = "reedpb"

# NPW Fix: Target the sandbox folder
# Checks if running inside 'data' or root to ensure path accuracy
if os.path.basename(os.getcwd()) == 'data':
    SANDBOX_DIR = "test"
else:
    SANDBOX_DIR = os.path.join("data", "test")

os.makedirs(SANDBOX_DIR, exist_ok=True)

def get_ebay_token():
    client_id = os.environ.get("APP_ID")
    client_secret = os.environ.get("CERT_ID")
    if not client_id or not client_secret:
        return None
    auth_str = f"{client_id}:{client_secret}"
    encoded_auth = base64.b64encode(auth_str.encode()).decode()
    url = "https://api.ebay.com/identity/v1/oauth2/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded", 
        "Authorization": f"Basic {encoded_auth}"
    }
    data = {"grant_type": "client_credentials", "scope": "https://api.ebay.com/oauth/api_scope"}
    try:
        response = requests.post(url, headers=headers, data=data)
        return response.json().get("access_token")
    except:
        return None

def sync_sandbox(category_query, filename):
    token = get_ebay_token()
    if not token: return
    
    # Fetching your seller inventory
    url = f"https://api.ebay.com/buy/browse/v1/item_summary/search?q={category_query}&filter=sellers:{{{SELLER_ID}}}"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        target_path = os.path.join(SANDBOX_DIR, filename)
        with open(target_path, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Sandbox Sync Success: {filename} saved to {target_path}")
    except Exception as e:
        print(f"Sandbox Sync Failed for {filename}: {e}")

if __name__ == "__main__":
    # Sync both categories to the test folder
    sync_sandbox("LEGO", "inventory.json")
    sync_sandbox("Diecast", "diecast.json")
