import os
import json
import requests
import base64

# --- 1. SETTINGS ---
EPN_CAMPAIGN_ID = "5339141674" 
SELLER_ID = "reedpb"
# NPW Fix: Target the exact root file used by the front-end
DATA_FILE = "diecast.json" 

def get_ebay_token():
    """Retrieves OAuth token from eBay using GitHub Secrets."""
    client_id = os.environ.get("APP_ID")
    client_secret = os.environ.get("CERT_ID")
    
    if not client_id or not client_secret:
        print("ERROR: APP_ID or CERT_ID not found in environment.")
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
    except Exception as e:
        print(f"Token Retrieval Error: {e}")
        return None

def sync_diecast_inventory():
    """Pulls diecast inventory and filters out sold/out-of-stock items."""
    token = get_ebay_token()
    if not token:
        return

    # Category 222 = Diecast & Toy Vehicles
    url = f"https://api.ebay.com/buy/browse/v1/item_summary/search?category_ids=222&filter=sellers:{{{SELLER_ID}}}"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-EBAY-C-ENDUSERCTX": f"affiliateCampaignId={EPN_CAMPAIGN_ID},affiliateReferenceId=blockheadz"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        inventory_data = response.json()

        if "itemSummaries" in inventory_data:
            # NPW logic: 
            # 1. Match Seller ID
            # 2. Exclude anything marked OUT_OF_STOCK
            filtered_items = [
                item for item in inventory_data["itemSummaries"] 
                if item.get("seller", {}).get("username", "").lower() == SELLER_ID.lower() and
                item.get("estimatedAvailabilityStatus") != "OUT_OF_STOCK"
            ]
            inventory_data["itemSummaries"] = filtered_items
            print(f"Sync complete: {len(filtered_items)} active items found.")

            # Overwrite the root file so the website updates immediately
            with open(DATA_FILE, "w") as f:
                json.dump(inventory_data, f, indent=4)
        else:
            print("No items found for this seller.")
            
    except Exception as e:
        print(f"Sync Error: {e}")

if __name__ == "__main__":
    sync_diecast_inventory()
