import json
import os
import sys

sys.path.append(os.getcwd())
from services.ebay_client import get_active_ebay_inventory

def assign_tags(title):
    tags = ['all'] # Every item gets 'all' by default
    title_lower = title.lower()

    # --- Categories ---
    if any(kw in title_lower for kw in ['lego', 'minifig', 'polybag', 'brickheadz']):
        tags.append('lego')
    elif any(kw in title_lower for kw in ['diecast', 'hot wheels', 'pop race', 'spark', 'tsm', 'looksmart', '1/64', '1/43']):
        tags.append('diecast')
    elif any(kw in title_lower for kw in ['pc', 'gaming', 'electronics', 'gpu']):
        tags.append('electronics')
    else:
        tags.append('other')

    return list(set(tags))

def sync_inventory():
    print("Starting sync_unified process...")
    
    # 1. Fetch data
    raw_items = get_active_ebay_inventory()
    
    if not raw_items:
        print("CRITICAL ERROR: No items were returned by get_active_ebay_inventory(). Check API filter/query.")
        return

    print(f"Total items fetched from eBay: {len(raw_items)}")
    
    # 2. Process data
    processed_items = []
    for item in raw_items:
        # Ensure title exists, default to empty string if missing
        title = item.get('title', 'Unknown Item')
        item['tags'] = assign_tags(title)
        processed_items.append(item)
            
    # 3. Create structure
    unified_data = {
        "inventory": processed_items,
        "itemSummaries": processed_items # Redundant key to satisfy both old/new lookups
    }
    
    # 4. Save file
    output_dir = 'data'
    output_path = os.path.join(output_dir, 'inventory.json')
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        with open(output_path, 'w') as f:
            json.dump(unified_data, f, indent=4)
        print(f"Successfully wrote {len(processed_items)} items to {output_path}")
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to write JSON file: {e}")

if __name__ == "__main__":
    sync_inventory()
