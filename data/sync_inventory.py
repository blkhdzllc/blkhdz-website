import os
import json
import requests
import base64

# --- 1. FOLDER SETUP ---
# Path is relative to the script's location in the /data folder
DATA_FILE = "test/inventory.json"
LOG_FILE = "test/sync_log.txt"

# Ensure the /test folder exists inside /data
os.makedirs("test", exist_ok=True)

# --- 2. CREDENTIALS ---
APP_ID = os.environ.get('EBAY_APP_ID')
CERT_ID = os.environ.get('EBAY_CERT_ID')
REFRESH_TOKEN = os.environ.get('EBAY_REFRESH_TOKEN')

def get_access_token():
    """Exchanges Refresh Token for a temporary Access Token"""
    url = "https://api.ebay.com/identity/v1/oauth2/token"
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
    return response.json().get('access_token')

def fetch_inventory(token):
    """Pulls live listings for the blkhdz store"""
    # Specifically filters for your eBay username
    url = "https://api.ebay.com/buy/browse/v1/item_summary/search?filter=sellers:blkhdz"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_US"
    }
    
    response = requests.get(url, headers=headers)
    return response.json()

def main():
    try:
        token = get_access_token()
        if not token:
            raise Exception("Failed to acquire Access Token. Check your Secrets.")

        inventory = fetch_inventory(token)
        
        # Save the actual data to the /test folder
        with open(DATA_FILE, "w") as f:
            json.dump(inventory, f, indent=4)
            
        with open(LOG_FILE, "a") as log:
            log.write(f"Sync Successful: Found {inventory.get('total', 0)} items.\n")

    except Exception as e:
        with open(LOG_FILE, "a") as log:
            log.write(f"CRITICAL ERROR: {str(e)}\n")

if __name__ == "__main__":
    main()
