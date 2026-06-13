import os
import json
import sys

# Ensure root is in path so 'services' is found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.ebay_client import get_active_ebay_inventory 
from services.market_intel import get_aggregated_valuation

# Configuration
DATA_DIR = 'data'
DATA_PATH = os.path.join(DATA_DIR, 'inventory.json')

def run_unified_sync():
    print("Starting Unified Sync...")
    live_inventory = get_active_ebay_inventory()
    
    # Initialize structure to prevent engine faults
    output = {"lego": [], "diecast": []}
    
    if isinstance(live_inventory, list):
        for item in live_inventory:
            price_val = get_aggregated_valuation(item.get('id', ''))
            entry = {
                "id": item.get('id', 'N/A'),
                "name": item.get('name', 'Unknown Item'),
                "img": item.get('img', ''),
                "price": str(price_val),
                "url": item.get('url', '#')
            }
            
            # Categorize
            name_lower = entry['name'].lower()
            if "lego" in name_lower:
                output["lego"].append(entry)
            else:
                output["diecast"].append(entry)
    
    # Write to disk
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    with open(DATA_PATH, 'w') as f:
        json.dump(output, f, indent=4)
    print(f"Sync complete. LEGO: {len(output['lego'])}, Diecast: {len(output['diecast'])}")

if __name__ == "__main__":
    run_unified_sync()
