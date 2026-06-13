import os
import json
from services.ebay_client import get_active_ebay_inventory 
from services.market_intel import get_aggregated_valuation

# Path must match what index.html expects
DATA_DIR = 'data'
DATA_PATH = os.path.join(DATA_DIR, 'inventory.json')

def run_unified_sync():
    print("Starting Unified Sync...")
    live_inventory = get_active_ebay_inventory()
    
    # Initialize structure to prevent engine faults
    output = {"lego": [], "diecast": []}
    
    if isinstance(live_inventory, list):
        for item in live_inventory:
            price_val = get_aggregated_valuation(item['id'])
            entry = {
                "id": item['id'].split('|')[1] if '|' in item['id'] else item['id'],
                "name": item['title'],
                "img": item['image']['imageUrl'] if 'image' in item else '',
                "price": f"{float(item['price']['value']):.2f}",
                "url": item.get('itemAffiliateWebUrl', item.get('itemWebUrl', '#'))
            }
            
            # Categorize based on title
            category = "lego" if "lego" in item['title'].lower() else "diecast"
            output[category].append(entry)
    
    # Ensure directory exists and write
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    with open(DATA_PATH, 'w') as f:
        json.dump(output, f, indent=4)
    print(f"Sync complete. LEGO: {len(output['lego'])}, Diecast: {len(output['diecast'])}")

if __name__ == "__main__":
    run_unified_sync()
