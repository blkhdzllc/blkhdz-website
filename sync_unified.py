import json
import os
import sys

sys.path.append(os.getcwd())
from services.ebay_client import get_active_ebay_inventory

def assign_tags(title):
    t = title.lower()
    if any(kw in t for kw in ['lego', 'minifig', 'brickheadz', 'polybag', 'star wars', 'ninjago', 'city']): 
        return ['lego']
    if any(kw in t for kw in ['diecast', 'pop race', 'hot wheels', 'mini gt', 'tarmac', 'spark']): 
        return ['diecast']
    return ['other']

def sync_inventory():
    raw_items = get_active_ebay_inventory()
    processed = []
    for item in raw_items:
        item['tags'] = assign_tags(item.get('title', ''))
        processed.append(item)
            
    output_path = os.path.join(os.getcwd(), 'data', 'inventory.json')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump({"inventory": processed}, f, indent=4)

if __name__ == "__main__":
    sync_inventory()
