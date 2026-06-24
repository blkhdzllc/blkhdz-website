import json
import os
import sys

sys.path.append(os.getcwd())
from services.ebay_client import get_active_ebay_inventory

def sync_inventory():
    print("Starting sync...")
    raw_items = get_active_ebay_inventory()
    
    # STRICT CHECK: If no items, stop immediately!
    if not raw_items or len(raw_items) == 0:
        print("ERROR: API returned 0 items. Aborting save to prevent blank inventory.")
        sys.exit(1) # This will turn your GitHub Action RED so you know it failed

    processed = []
    for item in raw_items:
        # Simple tag logic
        title = item.get('title', '').lower()
        tags = ['all']
        if 'lego' in title: tags.append('lego')
        if any(x in title for x in ['diecast', 'pop race', 'hot wheels']): tags.append('diecast')
        if any(x in title for x in ['pc', 'gaming', 'electronics']): tags.append('electronics')
        
        item['tags'] = tags
        processed.append(item)
            
    output_path = os.path.join(os.getcwd(), 'data', 'inventory.json')
    with open(output_path, 'w') as f:
        json.dump({"inventory": processed}, f, indent=4)
        
    print(f"Successfully saved {len(processed)} items.")

if __name__ == "__main__":
    sync_inventory()
