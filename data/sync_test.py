import os
import json
import requests
import base64
import glob
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
SELLER_ID = "reedpb"
CAMPAIGN_ID = "5339053531" 
SCRAPE_DO_TOKEN = "3687f040467644d5a62797baa02ffba5f13b60e27d5"

# Fixed Production Paths
base_dir = os.getcwd()
DATA_DIR = os.path.join(base_dir, "data")
DESC_DIR = os.path.join(DATA_DIR, "descriptions")
IMAGES_ROOT = os.path.join(base_dir, "images")

print(f"System Check -> Target Data Directory: {DATA_DIR}")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(DESC_DIR, exist_ok=True)

def get_ebay_token():
    client_id = os.environ.get("APP_ID")
    client_secret = os.environ.get("CERT_ID")
    if not client_id or not client_secret: 
        print("API Error -> Environment variables APP_ID or CERT_ID are missing.")
        return None
    auth_str = f"{client_id}:{client_secret}"
    encoded_auth = base64.b64encode(auth_str.encode()).decode()
    url = "https://api.ebay.com/identity/v1/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded", "Authorization": f"Basic {encoded_auth}"}
    payload = {"grant_type": "client_credentials", "scope": "https://api.ebay.com/oauth/api_scope"}
    try:
        response = requests.post(url, headers=headers, data=payload)
        return response.json().get("access_token")
    except Exception as token_err: 
        print(f"API Critical Error -> Failed to connect to eBay Auth: {token_err}")
        return None

def fetch_and_save_description(raw_id):
    """Fetch description text and save it to an isolated lightweight text file."""
    file_path = os.path.join(DESC_DIR, f"{raw_id}.html")
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        return  # Cached copy looks healthy, preserve it

    try:
        url = f"https://www.ebay.com/itm/{raw_id}"
        target_url = f"http://api.scrape.do?token={SCRAPE_DO_TOKEN}&render=true&super_proxy=true&url={url}"
        response = requests.get(target_url, timeout=30)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            desc_div = soup.find("div", {"id": "ds_div"})
            clean_html = str(desc_div) if desc_div else '<div style="text-align:center; padding:30px;">SPECIFICATIONS RECORDED ON PARENT PLATFORM.</div>'
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(clean_html)
            print(f"Processing -> Isolated fresh description saved for item: {raw_id}")
    except Exception as scrape_err: 
        print(f"Scraper Warning -> Failed to write details for {raw_id}: {scrape_err}")

def sync_store_inventory():
    token = get_ebay_token()
    if not token: 
        print("Sync Aborted -> Master eBay token generation failed.")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    raw_items = []
    search_queries = ["1:64", "64", "lego", "gt", "diecast", "scale", "tarmac", "wheels", "car", "pack", "set", "lot"]
    
    for q_term in search_queries:
        url = f"https://api.ebay.com/buy/browse/v1/item_summary/search?q={q_term}&filter=sellers:{{{SELLER_ID}}}&limit=100"
        try:
            response = requests.get(url, headers=headers)
            res_json = response.json()
            if "itemSummaries" in res_json:
                raw_items.extend(res_json["itemSummaries"])
        except Exception as e:
            print(f"Pass Warning -> Search failed for query target '{q_term}': {e}")

    if not raw_items:
        print("Sync Aborted -> Public marketplace lookup returned zero objects.")
        return

    unique_items = {item['itemId']: item for item in raw_items}.values()
    lego_items = []
    diecast_items = []
    
    search_pattern = os.path.join(IMAGES_ROOT, "**", "*.*")
    valid_images = [f for f in glob.glob(search_pattern, recursive=True) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    for item in unique_items:
        raw_id = item.get('legacyItemId')
        title = item.get('title', '').upper().replace("-", "")
        
        item_images = []
        for img_path in valid_images:
            img_filename = os.path.basename(img_path).split('_')[0].split('.')[0].upper()
            if img_filename in title and len(img_filename) > 3:
                rel_path = os.path.relpath(img_path, base_dir).replace("\\", "/")
                item_images.append(f"./{rel_path}")

        item_images.sort(key=lambda x: (not x.lower().endswith('.png'), x))
        item_images = item_images[:5]
        
        main_img = item.get('image', {}).get('imageUrl')
        item['customGallery'] = item_images + ([main_img] if main_img else [])
        item['itemWebUrl'] = f"https://www.ebay.com/itm/{raw_id}?mkcid=1&mkrid=711-53200-19255-0&campid={CAMPAIGN_ID}&toolid=10001&mkevt=1"
        
        # Pull description cleanly into its own file path safely
        fetch_and_save_description(raw_id)

        if "LEGO" in title or any(char.isdigit() for char in title): 
            if "DIECAST" not in title and "MINI GT" not in title and "POP RACE" not in title and "TARMAC" not in title:
                lego_items.append(item)
                continue
        diecast_items.append(item)

    inv_path = os.path.join(DATA_DIR, "inventory.json")
    die_path = os.path.join(DATA_DIR, "diecast.json")
    
    with open(inv_path, "w") as f:
        json.dump({"itemSummaries": lego_items, "total": len(lego_items)}, f, indent=4)
        
    with open(die_path, "w") as f:
        json.dump({"itemSummaries": diecast_items, "total": len(diecast_items)}, f, indent=4)
        
    print(f"Sync Complete -> Saved {len(lego_items)} LEGO metadata items to {inv_path}")
    print(f"Sync Complete -> Saved {len(diecast_items)} Diecast metadata items to {die_path}")

if __name__ == "__main__":
    sync_store_inventory()
