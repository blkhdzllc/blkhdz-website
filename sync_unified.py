import json
import os
import sys

sys.path.append(os.getcwd())
from services.ebay_client import get_active_ebay_inventory

def sync_inventory():
    print("Starting sync_unified process...")
    
    raw_items = get_active_ebay_inventory()
    print(f"Total items fetched from eBay: {len(raw_items)}")
    
    lego_items = []
    diecast_items = []
    
    for item in raw_items:
        title = item.get('title', '').lower()
        
        # Categorize items into lego or diecast based on the title
        if 'lego' in title:
            lego_items.append(item)
        else:
            diecast_items.append(item)
            
    unified_data = {
        "lego": lego_items,
        "diecast": diecast_items
    }
    
    output_path = os.path.join('data', 'inventory.json')
    os.makedirs('data', exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(unified_data, f, indent=4)
        
    print(f"Sync complete. LEGO: {len(lego_items)}, Diecast: {len(diecast_items)}")

if __name__ == "__main__":
    sync_inventory()
