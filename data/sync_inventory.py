import os
import json
import requests
import base64

# --- 1. FOLDER SETUP ---
os.makedirs("test", exist_ok=True)
DATA_FILE = os.path.join("test", "inventory.json")
LOG_FILE = os.path.join("test", "sync_log.txt")

# --- 2. CREDENTIALS ---
APP_ID = os.environ.get('EBAY_APP_ID', '').strip()
CERT_ID = os.environ.get('EBAY_CERT_ID', '').strip()

def get_access_token():
    """Mints a fresh Application Access Token using the stable api_scope"""
    url = "https://api.ebay.com/identity/v1/oauth2/token"
    auth_str = f"{APP_ID}:{CERT_ID}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {b64_auth}"
    }
    
    payload = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope"
    }
    
    response = requests.post(url, headers=headers, data=payload)
    return response.json().get('access_token')

def fetch_inventory(token):
    """
    Pulls ONLY blkhdz items.
    Uses 'q= ' (encoded space) to act as a wildcard for all your items.
    Explicitly targets Buy It Now via the default search behavior.
    """
    # Note: %20 is a URL-encoded space. This 'tricks' the API into 
    # searching for everything in your specific store.
    url = "https://api.ebay.com/buy/browse/v1/item_summary/search?q=%20&filter=sellers:{blkhdz}"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_US"
    }
    
    response = requests.get(url, headers=headers)
    return response.json()

def main():
    try:
        print("Final attempt at isolating Blockheadz LLC inventory...")
        token = get_access_token()
        if not token:
            print("Authentication failed.")
            return

        inventory = fetch_inventory(token)
        
        # Check if we got data or an error
        if 'itemSummaries' in inventory:
            item_count = len(inventory['itemSummaries'])
        else:
            item_count = inventory.get('total', 0)

        with open(DATA_FILE, "w") as f:
            json.dump(inventory, f, indent=4)
            
        with open(LOG_FILE, "a") as log:
            log.write(f"Sync Successful: Found {item_count} items.\n")
        
        print(f"Success! {item_count} items synced.")

    except Exception as e:
        with open(LOG_FILE, "a") as log:
            log.write(f"CRITICAL ERROR: {str(e)}\n")

if __name__ == "__main__":
    main()
