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
    """Mints a fresh Application Access Token"""
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
    data = response.json()
    return data.get('access_token')

def fetch_inventory(token):
    """Pulls only blkhdz items. Note the exact curly brace syntax."""
    # We use q=LEGO and the sellers filter. 
    # If this still pulls 1.7M, we will try the URL without 'q' entirely.
    url = "https://api.ebay.com/buy/browse/v1/item_summary/search?q=LEGO&filter=sellers:{blkhdz}"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_US"
    }
    
    response = requests.get(url, headers=headers)
    return response.json()

def main():
    try:
        print("Syncing Blockheadz LLC Inventory...")
        token = get_access_token()
        if not token:
            return

        inventory = fetch_inventory(token)
        
        # Check if the filter failed and returned global results
        total_found = inventory.get('total', 0)
        if total_found > 1000000:
             print("Filter ignored by eBay. Retrying with explicit category seed...")
             # Using Category 220 (Toys & Hobbies) to narrow the scope if global fails
             url_retry = "https://api.ebay.com/buy/browse/v1/item_summary/search?category_ids=220&filter=sellers:{blkhdz}"
             headers = {"Authorization": f"Bearer {token}", "X-EBAY-C-MARKETPLACE-ID": "EBAY_US"}
             inventory = requests.get(url_retry, headers=headers).json()

        with open(DATA_FILE, "w") as f:
            json.dump(inventory, f, indent=4)
            
        final_count = inventory.get('total', 0)
        with open(LOG_FILE, "a") as log:
            log.write(f"Sync Successful: Found {final_count} items.\n")
        
        print(f"Success! {final_count} items synced.")

    except Exception as e:
        with open(LOG_FILE, "a") as log:
            log.write(f"CRITICAL ERROR: {str(e)}\n")

if __name__ == "__main__":
    main()
