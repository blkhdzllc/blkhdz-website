import os
import json
import requests
import base64

# --- 1. SETTINGS & FOLDER SETUP ---
EPN_CAMPAIGN_ID = "5339141674" 
SELLER_ID = "reedpb"

os.makedirs("test", exist_ok=True)
DATA_FILE = os.path.join("test", "inventory.json")

def force_error_to_website(error_msg):
    # This forces the error to show up as a card on your website so we can read it
    error_data = {
        "itemSummaries": [{
            "itemId": "ERROR|000",
            "title": f"🚨 SYSTEM ALERT: {error_msg} 🚨",
            "price": {"value": "0.00", "currency": "USD"},
            "seller": {"username": SELLER_ID}
        }]
    }
    with open(DATA_FILE, "w") as f:
        json.dump(error_data, f, indent=4)
    print(f"Diagnostic Error Logged: {error_msg}")

def get_ebay_token():
    client_id = os.environ.get("APP_ID")
    client_secret = os.environ.get("CERT_ID")
    
    if not client_id or not client_secret:
        force_error_to_website("GITHUB SECRETS MISSING! Cannot find APP_ID or CERT_ID.")
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
        force_error_to_website(f"EBAY API KEY REJECTED! Error: {e}")
        return None

def sync_lego_inventory():
    token = get_ebay_token()
    if not token:
        return

    url = f"https://api.ebay.com/buy/browse/v1/item_summary/search?q=LEGO&filter=sellers:{{{SELLER_ID}}}"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-EBAY-C-ENDUSERCTX": f"affiliateCampaignId={EPN_CAMPAIGN_ID},affiliateReferenceId=blockheadz"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        inventory_data = response.json()

        # The Safety Net
        if "itemSummaries" in inventory_data:
            filtered_items = [
                item for item in inventory_data["itemSummaries"] 
                if item.get("seller", {}).get("username", "").lower() == SELLER_ID.lower()
            ]
            inventory_data["itemSummaries"] = filtered_items
        
        with open(DATA_FILE, "w") as f:
            json.dump(inventory_data, f, indent=4)
            
    except Exception as e:
        force_error_to_website(f"SEARCH FAILED! Error: {e}")

if __name__ == "__main__":
    sync_lego_inventory()
