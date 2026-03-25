import os
import json
import requests
import base64

# --- 1. SETTINGS & FOLDER SETUP ---
# Blockheadz LLC - eBay Partner Network Integration
EPN_CAMPAIGN_ID = "5339141674" 

# FIXED: Hardcoded seller ID to prevent global trending leak
SELLER_ID = "reedpb"

os.makedirs("test", exist_ok=True)
DATA_FILE = os.path.join("test", "inventory.json")

def get_ebay_token():
    # This remains the same - ensure your ENV variables are set in GitHub Secrets
    client_id = os.environ.get("APP_ID")
    client_secret = os.environ.get("CERT_ID")
    
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
    
    response = requests.post(url, headers=headers, data=data)
    return response.json().get("access_token")

def sync_lego_inventory():
    token = get_ebay_token()
    if not token:
        print("Failed to retrieve eBay Token")
        return

    # FIXED URL: Correctly formatted seller filter and keywords
    # Using sellers:{{seller_id}} per eBay API requirements
    url = f"https://api.ebay.com/buy/browse/v1/item_summary/search?q=LEGO&filter=sellers:{{{SELLER_ID}}}"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-EBAY-C-ENDUSERCTX": f"affiliateCampaignId={EPN_CAMPAIGN_ID},affiliateReferenceId=blockheadz"
    }

    response = requests.get(url, headers=headers)
    inventory_data = response.json()

    # Final Verification: Manually filter to ensure ONLY blkhdz items are saved
    if "itemSummaries" in inventory_data:
        filtered_items = [
            item for item in inventory_data["itemSummaries"] 
            if item.get("seller", {}).get("username") == SELLER_ID
        ]
        inventory_data["itemSummaries"] = filtered_items
        print(f"Successfully synced {len(filtered_items)} LEGO items for {SELLER_ID}")
    else:
        print("Warning: No items found or API error occurred.")

    with open(DATA_FILE, "w") as f:
        json.dump(inventory_data, f, indent=4)

if __name__ == "__main__":
    sync_lego_inventory()
