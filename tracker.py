import os
import json
import datetime
import csv
from services.market_intel import get_aggregated_valuation
from services.ebay_client import get_active_ebay_inventory 

# --- 1. CONFIGURATION ---
DATA_PATH = 'data.json'
HISTORY_PATH = 'data/market_history.csv'

def log_historical_data(inventory_list, category):
    """Appends data to historical CSV for market intelligence."""
    file_exists = os.path.isfile(HISTORY_PATH)
    with open(HISTORY_PATH, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['date', 'category', 'id', 'name', 'price'])
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
        for item in inventory_list:
            writer.writerow([timestamp, category, item['id'], item['name'], item['price']])

# --- 2. HARMONIZATION ENGINE ---
def run_harmonization():
    # 1. Fetch live inventory from eBay via your authenticated API client
    # This function should return a list of dictionaries with keys: id, name, url, img
    live_inventory = get_active_ebay_inventory()
    
    output = {
        "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "lego": [],
        "diecast": []
    }
    
    # 2. Process and Harmonize
    for item in live_inventory:
        price_val = get_aggregated_valuation(item['id'])
        
        entry = {
            "id": item['id'],
            "name": item['name'],
            "img": item['img'],
            "price": str(price_val) if isinstance(price_val, str) else f"{price_val:.2f}",
            "url": item['url'],
            "featured": item.get('feat', False)
        }
        
        # Simple categorization logic based on keywords
        category = "lego" if "lego" in item['name'].lower() else "diecast"
        output[category].append(entry)

    # 3. Persistence & History Logging
    try:
        with open(DATA_PATH, 'w') as f:
            json.dump(output, f, indent=4)
        
        log_historical_data(output["lego"], "LEGO")
        log_historical_data(output["diecast"], "DIECAST")
        print(f"Success: {len(live_inventory)} items synchronized.")
        
    except Exception as e:
        print(f"Error during synchronization: {e}")

if __name__ == "__main__":
    run_harmonization()
