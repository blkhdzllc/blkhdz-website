import os
import json
import requests
import base64

# --- 1. SETTINGS & FOLDER SETUP ---
EPN_CAMPAIGN_ID = "5339141674" 
SELLER_ID = "reedpb"

# NPW Fix: Target the production folder that the website actually reads
# We check the current folder to ensure we don't double-nest 'data/data'
if os.path.basename(os.getcwd()) == 'data':
    BASE_DIR = "brick-collection"
else:
    BASE_DIR = os.path.join("data", "brick-collection")

os.makedirs(BASE_DIR, exist_ok=True)
DATA_FILE = os.path.join(BASE_DIR, "inventory.json")

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
    data = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope"
    }
    
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json().get("access_token")
    except Exception:
        return None

def sync_lego_inventory():
    token = get_ebay_token()
    if not token:
        return

    # Category search for LEGO items from your specific seller ID
    url = f"https://api.ebay.com/buy/browse/v1/item_summary/search?q=LEGO&filter=sellers:{{{SELLER_ID}}}"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-EBAY-C-ENDUSERCTX": f"affiliateCampaignId={EPN_CAMPAIGN_ID},affiliateReferenceId=blockheadz"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        inventory_data = response.json()

        if "itemSummaries" in inventory_data:
            # Filters for your username and ensures items are available
            filtered_items = [
                item for item in inventory_data["itemSummaries"] 
                if item.get("seller", {}).get("username", "").lower() == SELLER_ID.lower() and
                item.get("estimatedAvailabilityStatus") != "OUT_OF_STOCK"
            ]
            inventory_data["itemSummaries"] = filtered_items
        
        with open(DATA_FILE, "w") as f:
            json.dump(inventory_data, f, indent=4)
        print(f"Success: {len(filtered_items)} LEGO items synced to {DATA_FILE}")
            
    except Exception as e:
        print(f"Search Failed: {e}")

if __name__ == "__main__":
    sync_lego_inventory()
