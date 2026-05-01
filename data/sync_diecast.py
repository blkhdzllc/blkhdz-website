import os
import json
import requests
import base64

# --- 1. SETTINGS & FOLDER SETUP ---
EPN_CAMPAIGN_ID = "5339141674" 
SELLER_ID = "reedpb"

# NPW Fix: Target the EXACT path your index.html uses to load diecast data
# We check if already in 'data' folder to avoid 'data/data' nesting
if os.path.basename(os.getcwd()) == 'data':
    BASE_DIR = "diecast"
else:
    BASE_DIR = os.path.join("data", "diecast")

os.makedirs(BASE_DIR, exist_ok=True)
DATA_FILE = os.path.join(BASE_DIR, "diecast.json")

def get_ebay_token():
    """Retrieves OAuth token using GitHub Secrets."""
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
    data = {"grant_type": "client_credentials", "scope": "https://api.ebay.com/oauth/api_scope"}
    
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json().get("access_token")
    except Exception:
        return None

def sync_diecast_inventory():
    """Pulls current eBay Diecast inventory and removes OUT_OF_STOCK items."""
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
            # 1. Filter for your items that are in stock
            filtered_items = [
                item for item in inventory_data["itemSummaries"] 
                if item.get("seller", {}).get("username", "").lower() == SELLER_ID.lower() and
                item.get("estimatedAvailabilityStatus") != "OUT_OF_STOCK"
            ]
            
            # 2. Process each item to add the SEO Schema
            for item in filtered_items:
                item_id = item.get("itemId", "N/A")
                title = item.get("title", "Unknown Diecast")
                price = item.get("price", {}).get("value", "0.00")
                image_url = item.get("image", {}).get("imageUrl", "")
                
                # Hidden ID card for Google Search
                item["seo_schema"] = {
                    "@context": "https://schema.org/",
                    "@type": "Product",
                    "name": title,
                    "image": image_url,
                    "offers": {
                        "@type": "Offer",
                        "price": price,
                        "priceCurrency": "USD",
                        "availability": "https://schema.org/InStock",
                        "url": f"https://www.ebay.com/itm/{item_id}"
                    }
                }
            
            inventory_data["itemSummaries"] = filtered_items

if __name__ == "__main__":
    sync_diecast_inventory()
