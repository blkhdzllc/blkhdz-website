import os
import json
import requests
import base64
from bs4 import BeautifulSoup

# --- SETTINGS ---
SELLER_ID = "reedpb"
CAMPAIGN_ID = "5339053531" 
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
    """Deep fetch using render=true to pull the actual HTML description content."""
    try:
        # CRITICAL: render=true ensures Scrape.do waits for the eBay description iframe to load
        target_url = f"http://api.scrape.do?token={SCRAPE_DO_TOKEN}&render=true&url={url}"
        response = requests.get(target_url, timeout=25)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Primary target for professional eBay listings
            desc_div = soup.find("div", {"id": "ds_div"})
            return str(desc_div) if desc_div else ""
    except: return ""
    return ""

def sync_enriched_data(category_name, query):
    token = get_ebay_token()
    if not token: return
    
    search_query = "1/64 diecast" if category_name == "DIECAST" else query
    url = f"https://api.ebay.com/buy/browse/v1/item_summary/search?q={search_query}&filter=sellers:{{{SELLER_ID}}}&limit=100"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        items_to_save = []
        
        all_local_images = sorted([f for f in os.listdir(IMAGES_DIR) if f.endswith(".jpg")])

        if "itemSummaries" in data:
            for item in data["itemSummaries"]:
                raw_id = item.get('legacyItemId')
                if not raw_id: continue

                # Image Priority: Hero Image (the one with your logo) must be first
                main_img = item.get('image', {}).get('imageUrl')
                ebay_images = [main_img] if main_img else []

                # Fetch the full gallery from the detail endpoint
                detail_url = f"https://api.ebay.com/buy/browse/v1/item/get_item_by_legacy_id?legacy_item_id={raw_id}"
                detail_res = requests.get(detail_url, headers=headers)
                if detail_res.status_code == 200:
                    details = detail_res.json()
                    if 'additionalImages' in details:
                        for d_img in details['additionalImages']:
                            if d_img['imageUrl'] not in ebay_images:
                                ebay_images.append(d_img['imageUrl'])

                # Match Local High-Res Overrides
                sku_id = None
                for img_file in all_local_images:
                    potential_id = img_file.split('.')[0].split('_')[0]
                    if potential_id in item.get('title', ''):
                        sku_id = potential_id
                        break
                
                local_gallery = [f"./images/{f}" for f in all_local_images if sku_id and f.startswith(sku_id)]
                
                # FINAL GALLERY: Local First -> Main Hero -> Extra eBay Gallery
                item['customGallery'] = local_gallery + ebay_images
                
                # Affiliate Tracking Link
                item['itemWebUrl'] = f"https://www.ebay.com/itm/{raw_id}?mkcid=1&mkrid=711-53200-19255-0&campid={CAMPAIGN_ID}&toolid=10001&mkevt=1"
                
                # DEEP SYNC DESCRIPTION
                print(f"Deep Fetching BLKHDZ SEO Data for: {raw_id}")
                item['fullHtmlDescription'] = fetch_full_description(f"https://www.ebay.com/itm/{raw_id}")
                
                items_to_save.append(item)

        filename = "inventory.json" if category_name == "LEGO" else "diecast.json"
        with open(os.path.join(SANDBOX_DIR, filename), "w") as f:
            json.dump(data, f, indent=4)
        
    except Exception as e: print(f"Sync Error: {e}")

if __name__ == "__main__":
    sync_enriched_data("LEGO", "LEGO")
    sync_enriched_data("DIECAST", "Hot Wheels")
