import os
import json
import requests
import base64
from bs4 import BeautifulSoup

# --- SETTINGS ---
SELLER_ID = "reedpb"
SCRAPE_DO_TOKEN = "3687f040467644d5a62797baa02ffba5f13b60e27d5"

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SANDBOX_DIR = os.path.join(base_dir, "data", "test")
IMAGES_DIR = os.path.join(base_dir, "images")

os.makedirs(SANDBOX_DIR, exist_ok=True)

def get_ebay_token():
    client_id = os.environ.get("APP_ID")
    client_secret = os.environ.get("CERT_ID")
    if not client_id or not client_secret: return None
    auth_str = f"{client_id}:{client_secret}"
    encoded_auth = base64.b64encode(auth_str.encode()).decode()
    url = "https://api.ebay.com/identity/v1/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded", "Authorization": f"Basic {encoded_auth}"}
    payload = {"grant_type": "client_credentials", "scope": "https://api.ebay.com/oauth/api_scope"}
    try:
        response = requests.post(url, headers=headers, data=payload)
        return response.json().get("access_token")
    except: return None

def fetch_full_description(url):
    try:
        target_url = f"http://api.scrape.do?token={SCRAPE_DO_TOKEN}&url={url}"
        response = requests.get(target_url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            desc_div = soup.find("div", {"id": "ds_div"})
            return str(desc_div) if desc_div else ""
    except: return ""
    return ""

def sync_enriched_data(category_name, query):
    token = get_ebay_token()
    if not token: return
    
    search_query = "1/64 diecast" if category_name == "DIECAST" else query
    url = f"https://api.api.ebay.com/buy/browse/v1/item_summary/search?q={search_query}&filter=sellers:{{{SELLER_ID}}}&limit=100"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        items_to_save = []
        
        all_local_images = [f for f in os.listdir(IMAGES_DIR) if f.endswith(".jpg")]

        if "itemSummaries" in data:
            for item in data["itemSummaries"]:
                title = item.get('title', '')
                raw_id = item.get('legacyItemId')
                
                # Identify the ID for the naming match (Set # or SKU)
                # We extract the 5-digit LEGO number or SKU from title if possible
                sku_id = None
                for img_file in all_local_images:
                    potential_id = img_file.split('.')[0].split('_')[0]
                    if potential_id in title:
                        sku_id = potential_id
                        break
                
                # --- GALLERY LOGIC ---
                gallery = []
                if sku_id:
                    # Find all files starting with that ID (e.g., 75274.jpg, 75274_1.jpg)
                    matches = sorted([f"./images/{f}" for f in all_local_images if f.startswith(sku_id)])
                    gallery = matches
                
                item['customGallery'] = gallery if gallery else [item.get('image', {}).get('imageUrl')]
                item['itemWebUrl'] = f"https://www.ebay.com/itm/{raw_id}" if raw_id else "#"
                item['fullHtmlDescription'] = fetch_full_description(item['itemWebUrl']) if raw_id else ""
                
                items_to_save.append(item)

        filename = "inventory.json" if category_name == "LEGO" else "diecast.json"
        with open(os.path.join(SANDBOX_DIR, filename), "w") as f:
            json.dump(data, f, indent=4)
        
    except Exception as e: print(f"Sync Error: {e}")

if __name__ == "__main__":
    sync_enriched_data("LEGO", "LEGO")
    sync_enriched_data("DIECAST", "Hot Wheels")
