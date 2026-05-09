import os
import json
import requests
import base64
import glob
from bs4 import BeautifulSoup

# --- SETTINGS ---
SELLER_ID = "reedpb"
CAMPAIGN_ID = "5339053531" 
SCRAPE_DO_TOKEN = "3687f040467644d5a62797baa02ffba5f13b60e27d5"

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SANDBOX_DIR = os.path.join(base_dir, "data", "test")
IMAGES_ROOT = os.path.join(base_dir, "images")

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
    """Deep fetch with render and super_proxy to ensure custom HTML loads."""
    try:
        target_url = f"http://api.scrape.do?token={SCRAPE_DO_TOKEN}&render=true&super_proxy=true&url={url}"
        response = requests.get(target_url, timeout=30)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            desc_div = soup.find("div", {"id": "ds_div"})
            return str(desc_div) if desc_div else ""
    except: return ""
    return ""

def sync_enriched_data(category_name, query):
    token = get_ebay_token()
    if not token: return
    
    filename = "inventory.json" if category_name == "LEGO" else "diecast.json"
    filepath = os.path.join(SANDBOX_DIR, filename)
    
    existing_descriptions = {}
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                old_data = json.load(f)
                for old_item in old_data.get('itemSummaries', []):
                    if old_item.get('legacyItemId') and old_item.get('fullHtmlDescription'):
                        existing_descriptions[old_item['legacyItemId']] = old_item['fullHtmlDescription']
        except: pass

    search_query = "1/64 diecast" if category_name == "DIECAST" else query
    url = f"https://api.ebay.com/buy/browse/v1/item_summary/search?q={search_query}&filter=sellers:{{{SELLER_ID}}}&limit=100"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        # NPW: Find ALL images in ALL subfolders recursively
        search_pattern = os.path.join(IMAGES_ROOT, "**", "*.*")
        all_local_paths = glob.glob(search_pattern, recursive=True)
        valid_images = [f for f in all_local_paths if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

        if "itemSummaries" in data:
            for item in data["itemSummaries"]:
                raw_id = item.get('legacyItemId')
                title = item.get('title', '').upper().replace("-", "")
                
                # Match images where the SKU (filename) is in the eBay Title
                item_images = []
                for img_path in valid_images:
                    img_filename = os.path.basename(img_path).split('_')[0].split('.')[0].upper()
                    if img_filename in title and len(img_filename) > 3:
                        rel_path = os.path.relpath(img_path, base_dir).replace("\\", "/")
                        item_images.append(f"./{rel_path}")

                # Prioritize .png for Hero shots, then sort the rest
                item_images.sort(key=lambda x: (not x.lower().endswith('.png'), x))
                
                main_img = item.get('image', {}).get('imageUrl')
                item['customGallery'] = item_images + ([main_img] if main_img else [])
                item['itemWebUrl'] = f"https://www.ebay.com/itm/{raw_id}?mkcid=1&mkrid=711-53200-19255-0&campid={CAMPAIGN_ID}&toolid=10001&mkevt=1"
                
                if raw_id in existing_descriptions:
                    item['fullHtmlDescription'] = existing_descriptions[raw_id]
                else:
                    item['fullHtmlDescription'] = fetch_full_description(f"https://www.ebay.com/itm/{raw_id}")

        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
        
    except Exception as e: print(f"Sync Error: {e}")

if __name__ == "__main__":
    sync_enriched_data("LEGO", "LEGO")
    sync_enriched_data("DIECAST", "Hot Wheels")
