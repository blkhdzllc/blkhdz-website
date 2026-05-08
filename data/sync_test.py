import os
import json
import requests
import base64

# --- SETTINGS ---
SELLER_ID = "reedpb"

# Absolute path logic for both Local and GitHub Bot runs
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SANDBOX_DIR = os.path.join(base_dir, "data", "test")
os.makedirs(SANDBOX_DIR, exist_ok=True)

def get_ebay_token():
    client_id = os.environ.get("APP_ID")
    client_secret = os.environ.get("CERT_ID")
    if not client_id or not client_secret:
        print("CRITICAL: Missing API Secrets (APP_ID or CERT_ID)")
        return None
    
    auth_str = f"{client_id}:{client_secret}"
    encoded_auth = base64.b64encode(auth_str.encode()).decode()
    url = "https://api.ebay.com/identity/v1/oauth2/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded", 
        "Authorization": f"Basic {encoded_auth}"
    }
    payload = {"grant_type": "client_credentials", "scope": "https://api.ebay.com/oauth/api_scope"}
    
    try:
        response = requests.post(url, headers=headers, data=payload)
        return response.json().get("access_token")
    except Exception as e:
        print(f"Token Retrieval Failed: {e}")
        return None

def sync_enriched_data(category_name, query):
    token = get_ebay_token()
    if not token: return
    
    # Using 'limit=100' to capture full inventory
    search_query = "1/64 diecast" if category_name == "DIECAST" else query
        
    url = f"https://api.ebay.com/buy/browse/v1/item_summary/search?q={search_query}&filter=sellers:{{{SELLER_ID}}}&limit=100"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        items_to_save = []
        
        if "itemSummaries" in data:
            for item in data["itemSummaries"]:
                try:
                    if 'itemId' not in item:
                        continue

                    # Robust ID extraction for clickable eBay links
                    raw_id = item.get('legacyItemId')
                    if not raw_id:
                        parts = item['itemId'].split('|')
                        raw_id = parts[1] if len(parts) > 1 else None
                    
                    item['itemWebUrl'] = f"https://www.ebay.com/itm/{raw_id}" if raw_id else "#"
                    
                    # CLEAN: Only use what eBay provides. No added text or guarantees.
                    item['shortDescription'] = item.get('shortDescription', '').strip()
                    
                    items_to_save.append(item)
                except Exception:
                    continue

        data['itemSummaries'] = items_to_save
        filename = "inventory.json" if category_name == "LEGO" else "diecast.json"
        target_path = os.path.join(SANDBOX_DIR, filename)
        
        with open(target_path, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Success: Saved {len(items_to_save)} {category_name} items.")
        
    except Exception as e:
        print(f"General Sync Error: {e}")
        raise 

if __name__ == "__main__":
    sync_enriched_data("LEGO", "LEGO")
    sync_enriched_data("DIECAST", "Hot Wheels")
