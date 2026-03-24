import os
import json
import requests
import base64

# --- 1. FOLDER SETUP ---
# Ensures the 'test' directory exists inside the 'data' folder
os.makedirs("test", exist_ok=True)

DATA_FILE = os.path.join("test", "inventory.json")
LOG_FILE = os.path.join("test", "sync_log.txt")

# --- 2. CREDENTIALS ---
# .strip() is used here to remove any accidental spaces from GitHub Secrets
APP_ID = os.environ.get('EBAY_APP_ID', '').strip()
CERT_ID = os.environ.get('EBAY_CERT_ID', '').strip()
REFRESH_TOKEN = os.environ.get('EBAY_REFRESH_TOKEN', '').strip()

def get_access_token():
    """Exchanges Refresh Token for a temporary Access Token"""
    url = "https://api.ebay.com/identity/v1/oauth2/token"
    
    # Prepare Base64 Auth String (App ID : Cert ID)
    auth_str = f"{APP_ID}:{CERT_ID}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {b64_auth}"
    }
    
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "scope": "https://api.ebay.com/oauth/api_scope/buy.browse.readonly"
    }
    
    response = requests.post(url, headers=headers, data=payload)
    data = response.json()
    
    if response.status_code != 200:
        # This will write the SPECIFIC eBay error to your sync_log.txt
        error_msg = data.get('error_description', 'Unknown Auth Error')
        with open(LOG_FILE, "a") as log:
            log.write(f"eBay Auth Failed: {error_msg}\n")
        return None
        
    return data.get('access_token')

def fetch_inventory(token):
    """Pulls live listings for the blkhdz store using the Browse API"""
    # Specifically targets your seller username: blkhdz
    url = "https://api.ebay.com/buy/browse/v1/item_summary/search?filter=sellers:blkhdz"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_US"
    }
    
    response = requests.get(url, headers=headers)
    return response.json()

def main():
    try:
        print("Starting Blockheadz LLC Inventory Sync...")
        
        # 1. Get Access Token
        token = get_access_token()
        if not token:
            print("Authentication failed. Check data/test/sync_log.txt for the specific eBay error.")
            return

        # 2. Fetch Data from eBay
        inventory = fetch_inventory(token)
        
        # 3. Save to inventory.json
        with open(DATA_FILE, "w") as f:
            json.dump(inventory, f, indent=4)
            
        # 4. Log the success and count
        item_count = inventory.get('total', 0)
        with open(LOG_FILE, "a") as log:
            log.write(f"Sync Successful: Found {item_count} items.\n")
        
        print(f"Success! {item_count} items synced.")

    except Exception as e:
        error_str = f"CRITICAL SCRIPT ERROR: {str(e)}"
        print(error_str)
        with open(LOG_FILE, "a") as log:
            log.write(f"{error_str}\n")

if __name__ == "__main__":
    main()
