import json
import os
import sys

# Ensure the script can find the services folder
sys.path.append(os.getcwd())
from services.ebay_client import get_active_ebay_inventory

def assign_tags(title):
    """Assigns tags based on item title."""
    t = title.lower()
    tags = ['all']
    if any(x in t for x in ['lego', 'minifig', 'brickheadz']): tags.append('lego')
    if any(x in t for x in ['diecast', 'pop race', 'hot wheels', 'mini gt']): tags.append('diecast')
    if any(x in t for x in ['pc', 'gaming', 'electronics', 'gpu']): tags.append('electronics')
    return list(set(tags))

def sync_inventory():
    print("Starting sync...")
    
    # 1. Fetch
    raw_items = get_active_ebay_inventory()
    
    # 2. Safety Check
    if not raw_items:
        print("ERROR: No items returned. Aborting save.")
        sys.exit(1)

    # 3. Process
    processed_items = []
    for item in raw_items:
        item['tags'] = assign_tags(item.get('title', ''))
        processed_items.append(item)
    
    # 4. Save
    output_path = os.path.join(os.getcwd(), 'data', 'inventory.json')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    data_to_save = {
        "inventory": processed_items,
        "itemSummaries": processed_items
    }
    
    with open(output_path, 'w') as f:
        json.dump(data_to_save, f, indent=4)
        f.flush()
        os.fsync(f.fileno())
        
    print(f"Successfully saved {len(processed_items)} items to {output_path}")

if __name__ == "__main__":
    sync_inventory()
