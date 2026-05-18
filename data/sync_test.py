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

# Fixed Production Paths: Resolves correctly on both Local PC and GitHub Runner Workspace
base_dir = os.getcwd()
DATA_DIR = os.path.join(base_dir, "data")
IMAGES_ROOT = os.path.join(base_dir, "images")

os.makedirs(DATA_DIR, exist_ok=True)

def load_existing_descriptions():
    """Load already scraped descriptions to prevent re-fetching and timeouts."""
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
            except:
                pass
    return cached_desc

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
        target_url = f"http://api.scrape.do?token={SCRAPE_DO_TOKEN}&render=true&super_proxy=true&url={url}"
        response = requests.get(target_url, timeout=30)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            desc_div = soup.find("div", {"id": "ds_div"})
            return str(desc_div) if desc_div else ""
    except: return ""
    return ""

def sync_store_inventory():
    token = get_ebay_token()
    if not token: 
        print("Error: Missing eBay API Tokens.")
        return
    
    # Load what we already downloaded previously
    description_cache = load_existing_descriptions()
    print(f"Loaded {len(description_cache)} existing descriptions from cache.")
    
    # Querying the entire store directly by seller ID to pull all 96+ items
    url = f"https://api.ebay.com/buy/browse/v1/item_summary/search?filter=sellers:{{{SELLER_ID}}}&limit=100"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        all_data = response.json()
        
        if "itemSummaries" not in all_data:
            print("No items found or API authorization error.")
            return

        # Separate items purely by catalog rules
        lego_items = []
        diecast_items = []
        
        # Scan images across all folders recursively
        search_pattern = os.path.join(IMAGES_ROOT, "**", "*.*")
        valid_images = [f for f in glob.glob(search_pattern, recursive=True) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

        for item in all_data["itemSummaries"]:
            raw_id = item.get('legacyItemId')
            title = item.get('title', '').upper().replace("-", "")
            
            # Smart Gallery Match
            item_images = []
            for img_path in valid_images:
                img_filename = os.path.basename(img_path).split('_')[0].split('.')[0].upper()
                if img_filename in title and len(img_filename) > 3:
                    rel_path = os.path.relpath(img_path, base_dir).replace("\\", "/")
                    item_images.append(f"./{rel_path}")

            # Keep gallery lean: Max 5 custom local photos, prioritize Hero (.png)
            item_images.sort(key=lambda x: (not x.lower().endswith('.png'), x))
            item_images = item_images[:5]
            
            main_img = item.get('image', {}).get('imageUrl')
            item['customGallery'] = item_images + ([main_img] if main_img else [])
            item['itemWebUrl'] = f"https://www.ebay.com/itm/{raw_id}?mkcid=1&mkrid=711-53200-19255-0&campid={CAMPAIGN_ID}&toolid=10001&mkevt=1"
            
            # Check cache first to avoid hitting Scrape.do timeouts
            if raw_id in description_cache:
                item['fullHtmlDescription'] = description_cache[raw_id]
            else:
                print(f"Fetching fresh description for item: {raw_id}")
                item['fullHtmlDescription'] = fetch_full_description(f"https://www.ebay.com/itm/{raw_id}")

            # Sorting into clean lists based on branding keywords
            if "LEGO" in title or any(char.isdigit() for char in title): 
                # Fallback to Lego sorting if it matches common set formats
                if "DIECAST" not in title and "MINI GT" not in title and "POP RACE" not in title:
                    lego_items.append(item)
                    continue
            diecast_items.append(item)

        # Write clean production JSON files directly
        with open(os.path.join(DATA_DIR, "inventory.json"), "w") as f:
            json.dump({"itemSummaries": lego_items, "total": len(lego_items)}, f, indent=4)
            
        with open(os.path.join(DATA_DIR, "diecast.json"), "w") as f:
            json.dump({"itemSummaries": diecast_items, "total": len(diecast_items)}, f, indent=4)
            
        print(f"Sync Complete: Sorted {len(lego_items)} LEGO items and {len(diecast_items)} Diecast items directly to production files.")

    except Exception as e: 
        print(f"Sync Execution Error: {e}")

if __name__ == "__main__":
    sync_store_inventory()
