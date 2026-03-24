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
    """Mints a fresh Application Access Token using the base public scope"""
    url = "https://api.ebay.com/identity/v1/oauth2/token"
    
    auth_str = f"{APP_ID}:{CERT_ID}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {b64_auth}"
    }
    
    # We are using the base scope which is universally granted to all apps
    payload = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope"
    }
    
    response = requests.post(url, headers=headers, data=payload)
    data = response.json()
    
    if response.status_code != 200:
        error_msg = data.get('error_description', 'Unknown Auth Error')
        with open(LOG_FILE, "a") as log:
            log.write(f"Application Auth Failed: {error_msg}\n")
        return None
        
    return data.get('access_token')

def fetch_inventory(token):
    """Pulls live listings for the blkhdz store"""
    # Using the Browse API to search for items from your specific seller ID
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
        
        token = get_access_token()
        if not token:
            print("Authentication failed. Check data/test/sync_log.txt.")
            return

        inventory = fetch_inventory(token)
        
        # Check if we actually got data or an API error
        if 'itemSummaries' not in inventory and 'total' not in inventory:
            error_note = inventory.get('errors', [{'message': 'No data returned'}])[0]['message']
            raise Exception(f"API Error: {error_note}")

        with open(DATA_FILE, "w") as f:
            json.dump(inventory, f, indent=4)
            
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
