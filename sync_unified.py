import json
import os
import sys

# Ensure we can import from our services
sys.path.append(os.getcwd())
from services.ebay_client import get_active_ebay_inventory

def sync_inventory():
    print("Starting sync_unified process...")
    
    # 1. Fetch raw items from your eBay service
    raw_items = get_active_ebay_inventory()
    print(f"Total items fetched from eBay: {len(raw_items)}")
    
    # 2. Initialize the structure
    unified_data = {
        "lego": [],
        "diecast": []
    }
    
    # 3. Categorization logic
    # We check the title for keywords to sort them
    for item in raw_items:
        title = item.get('title', '').lower()
        
        # Simple keyword-based sorting
        if any(keyword in title for keyword in ['lego', 'star wars', 'ninjago', 'technic', 'speed champions']):
            unified_data["lego"].append(item)
        else:
            # Everything else currently defaults to diecast
            unified_data["diecast"].append(item)
            
    # 4. Save to the file
    output_path = os.path.join('data', 'inventory.json')
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(unified_data, f, indent=4)
        
    print(f"Sync complete. LEGO: {len(unified_data['lego'])}, Diecast: {len(unified_data['diecast'])}")

if __name__ == "__main__":
    sync_inventory()
