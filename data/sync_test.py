import os
import json
import requests
import base64

# --- SETTINGS ---
SELLER_ID = "reedpb"
# NPW Fix: Accurate pathing for sandbox
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SANDBOX_DIR = os.path.join(base_dir, "data", "test")
os.makedirs(SANDBOX_DIR, exist_ok=True)

def get_ebay_token():
    client_id = os.environ.get("APP_ID")
    client_secret = os.environ.get("CERT_ID")
    if not client_id or not client_secret: return None
    auth_str = f"{client_id}:{client_secret}"
    encoded_auth = base64.b64encode(auth_str.encode()).decode()
    url = "https://api.ebay.com/identity/v1/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded", "Authorization": f"Basic {encoded_auth}"}
    data = {"grant_type": "client_credentials", "scope": "https://api.ebay.com/oauth/api_scope"}
    try:
        response = requests.post(url, headers=headers, data=data)
        return response.json().get("access_token")
    except: return None

def run_test_sync(category_name, query):
    token = get_ebay_token()
    if not token: return
    
    # 1. Search for items
    url = f"https://api.ebay.com/buy/browse/v1/item_summary/search?q={query}&filter=sellers:{{{SELLER_ID}}}"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        # 2. Detail Enrichment: Adding the 'Item Link' and 'Description' placeholder
        # We simulate the Detail API logic for the sandbox
        if "itemSummaries" in data:
            for item in data["itemSummaries"]:
                # Creates a direct link to the item on eBay
                item['itemWebUrl'] = f"https://www.ebay.com/itm/{item['itemId'].split('|')[-1]}"
                # Placeholder for description (to be filled by SEO engine later)
                item['shortDescription'] = "Authentic Collector Grade Item. Shipped in reinforced boxes with professional dunnage."

        filename = "inventory.json" if category_name == "LEGO" else "diecast.json"
        with open(os.path.join(SANDBOX_DIR, filename), "w") as f:
            json.dump(data, f, indent=4)
        print(f"Enriched Sandbox Sync: {category_name} saved to {SANDBOX_DIR}")
    except Exception as e: print(f"Test Sync Failed: {e}")

if __name__ == "__main__":
    run_test_sync("LEGO", "LEGO")
    run_test_sync("DIECAST", "Hot Wheels")
