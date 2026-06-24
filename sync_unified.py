import json
import os
import sys

# Ensure import works
sys.path.append(os.getcwd())
from services.ebay_client import get_active_ebay_inventory

def assign_tags(title):
    t = title.lower()
    tags = ['all']
    if any(x in t for x in ['lego', 'minifig', 'brickheadz', 'polybag']): tags.append('lego')
    elif any(x in t for x in ['diecast', 'pop race', 'hot wheels', 'mini gt', 'tarmac', 'spark']): tags.append('diecast')
    elif any(x in t for x in ['pc', 'gaming', 'electronics', 'gpu']): tags.append('electronics')
    return list(set(tags))

def sync_inventory():
    print("Starting sync...")
    raw_items = get_active_ebay_inventory()
    
    if not raw_items:
        print("No items returned. Inventory file will be empty.")

    processed_items = []
    for item in raw_items:
        item['tags'] = assign_tags(item.get('title', ''))
        processed_items.append(item)
            
    output_path = os.path.join(os.getcwd(), 'data', 'inventory.json')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    data_structure = {
        "inventory": processed_items,
        "itemSummaries": processed_items
    }
    
    with open(output_path, 'w') as f:
        json.dump(data_structure, f, indent=4)
        f.flush()
        os.fsync(f.fileno())
        
    print(f"Successfully saved {len(processed_items)} items.")

if __name__ == "__main__":
    sync_inventory()
