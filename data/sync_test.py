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
IMAGES_ROOT = os.path.join(base_dir, "images")

print(f"System Check -> Execution Root Directory: {base_dir}")
print(f"System Check -> Target Data Directory: {DATA_DIR}")

os.makedirs(DATA_DIR, exist_ok=True)

def load_existing_descriptions():
    cached_desc = {}
    for filename in ["inventory.json", "diecast.json"]:
        file_path = os.path.join(DATA_DIR, filename)
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                    for item in data.get("itemSummaries", []):
                        raw_id = item.get('legacyItemId')
                        desc = item.get('fullHtmlDescription')
                        if raw_id and desc:
                            cached_desc[raw_id] = desc
            except Exception as cache_err:
                print(f"Cache Warning -> Could not parse {filename}: {cache_err}")
    return cached_desc

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
        res_data = response.json()
        return res_data.get("access_token")
    except Exception as token_err: 
        print(f"API Critical Error -> Failed to connect to eBay Auth: {token_err}")
        return None

def fetch_full_description(url):
    try:
        target_url = f"http://api.scrape.do?token={SCRAPE_DO_TOKEN}&render=true&super_proxy=true&url={url}"
        response = requests.get(target_url, timeout=30)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            desc_div = soup.find("div", {"id": "ds_div"})
            return str(desc_div) if desc_div else ""
    except Exception as scrape_err: 
        print(f"Scraper Warning -> Failed to fetch URL {url}: {scrape_err}")
    return ""

def sync_store_inventory():
    token = get_ebay_token()
    if not token: 
        print("Sync Aborted -> Master eBay token generation failed.")
        return
    
    description_cache = load_existing_descriptions()
    
    # MASTER SELLER ENDPOINT: Requests every active inventory object directly from your account, ignoring keyword blocks
    url = "https://api.ebay.com/sell/inventory/v1/inventory_item?limit=100&offset=0"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_US"
    }
    
    try:
        response = requests.get(url, headers=headers)
        all_data = response.json()
        
        raw_items = all_data.get("inventoryItems", [])
        if not raw_items:
            print(f"Sync Aborted -> No items returned from seller inventory endpoint. Payload: {all_data}")
            return

        lego_items = []
        diecast_items = []
        
        search_pattern = os.path.join(IMAGES_ROOT, "**", "*.*")
        valid_images = [f for f in glob.glob(search_pattern, recursive=True) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

        for inv_item in raw_items:
            # Normalize the data object format to cleanly align with your index.html layout expectations
            title = inv_item.get("product", {}).get("title", "").upper()
            sku = inv_item.get("sku", "")
            
            # Extract legacy item mapping IDs safely
            listing_details = inv_item.get("listingDetails", {})
            raw_id = listing_details.get("listingId")
            
            if not raw_id:
                continue # Skip drafts or unlisted variants

            # Construct layout item dictionary
            item = {
                "itemId": f"v1|{raw_id}|0",
                "legacyItemId": str(raw_id),
                "title": inv_item.get("product", {}).get("title", ""),
                "price": {
                    "value": inv_item.get("price", {}).get("value", "0.00"),
                    "currency": "USD"
                },
                "image": {
                    "imageUrl": inv_item.get("product", {}).get("imageUrls", [None])[0]
                }
            }

            # Local Graphic Asset Cross-Referencing Engine
            clean_title_search = title.replace("-", "")
            item_images = []
            for img_path in valid_images:
                img_filename = os.path.basename(img_path).split('_')[0].split('.')[0].upper()
                if img_filename in clean_title_search and len(img_filename) > 3:
                    rel_path = os.path.relpath(img_path, base_dir).replace("\\", "/")
                    item_images.append(f"./{rel_path}")

            item_images.sort(key=lambda x: (not x.lower().endswith('.png'), x))
            item_images = item_images[:5]
            
            main_img = item["image"]["imageUrl"]
            item['customGallery'] = item_images + ([main_img] if main_img else [])
            item['itemWebUrl'] = f"https://www.ebay.com/itm/{raw_id}?mkcid=1&mkrid=711-53200-19255-0&campid={CAMPAIGN_ID}&toolid=10001&mkevt=1"
            
            if raw_id in description_cache:
                item['fullHtmlDescription'] = description_cache[raw_id]
            else:
                print(f"Processing -> Fetching fresh description for item ID: {raw_id}")
                item['fullHtmlDescription'] = fetch_full_description(f"https://www.ebay.com/itm/{raw_id}")

            # Smart Split Routing Sorting Matrix
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
            
        print(f"Sync Complete -> Saved {len(lego_items)} LEGO items to {inv_path}")
        print(f"Sync Complete -> Saved {len(diecast_items)} Diecast items to {die_path}")

    except Exception as e: 
        print(f"Sync Critical Failure -> Thread exception encountered: {e}")

if __name__ == "__main__":
    sync_store_inventory()
