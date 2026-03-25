import os
import json
import requests
import base64

# --- 1. SETTINGS & FOLDER SETUP ---
# Blockheadz LLC - eBay Partner Network Integration
EPN_CAMPAIGN_ID = "5339141674" 

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
    return response.json().get('access_token')

def fetch_affiliate_inventory(token):
    """Pulls inventory and tells eBay to 'affiliatize' the links automatically"""
    # Using the proven 'Space Trick' (%20) with your seller filter
    url = "https://api.ebay.com/buy/browse/v1/item_summary/search?q=%20&filter=sellers:{blkhdz}"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
        # This header converts standard links into EPN Affiliate links
        "X-EBAY-C-ENDUSERCTX": f"affiliateCampaignId={EPN_CAMPAIGN_ID},affiliateReferenceId=blockheadz-site"
    }
    
    response = requests.get(url, headers=headers)
    return response.json()

def main():
    try:
        print("Starting Blockheadz LLC Affiliate Sync...")
        token = get_access_token()
        if not token:
            print("Authentication failed.")
            return

        inventory = fetch_affiliate_inventory(token)
        
        # Check if we have items
        items = inventory.get('itemSummaries', [])
        item_count = len(items)

        # Save the full data (now including 'itemAffiliateWebUrl')
        with open(DATA_FILE, "w") as f:
            json.dump(inventory, f, indent=4)
            
        with open(LOG_FILE, "a") as log:
            log.write(f"Affiliate Sync Successful: Found {item_count} items with tracking.\n")
        
        print(f"Success! {item_count} affiliate-ready items synced.")

    except Exception as e:
        with open(LOG_FILE, "a") as log:
            log.write(f"CRITICAL ERROR: {str(e)}\n")

if __name__ == "__main__":
    main()

