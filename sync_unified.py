import json
import os
import sys
import time

# Ensure we can find our internal modules
sys.path.append(os.getcwd())
from services.ebay_client import get_active_ebay_inventory

# Attempt to load your description fetching function if it exists in ebay_client
try:
    from services.ebay_client import get_item_description
except ImportError:
    try:
        from services.ebay_client import get_ebay_item_description as get_item_description
    except ImportError:
        get_item_description = None

def assign_tags(title):
    """Assigns category tags based on title keywords."""
    if not title:
        return ['all', 'other']
        
    t = str(title).lower()
    tags = ['all']
    
    # LEGO detection
    if any(kw in t for kw in ['lego', 'minifig', 'brickheadz', 'polybag', 'star wars', 'ninjago', 'city', 'technic', 'creator', 'icons', 'speed champions']): 
        tags.append('lego')
        if 'star wars' in t: tags.append('star wars')
        if 'city' in t: tags.append('city')
        if 'technic' in t: tags.append('technic')
        if 'ninjago' in t: tags.append('ninjago')
        if 'creator' in t: tags.append('creator')
        if 'icons' in t: tags.append('icons')
        if 'speed champions' in t: tags.append('speed champions')
        if 'brickheadz' in t: tags.append('brickheadz')
        if 'minifig' in t: tags.append('minifigures')

    # Diecast detection (Now tracking Hot Wheels alongside Pop Race & Mini GT)
    if any(kw in t for kw in ['diecast', 'pop race', 'mini gt', 'hot wheels', 'tarmac', 'spark', 'looksmart', '1/64', '1/43']): 
        tags.append('diecast')
        if 'mini gt' in t: tags.append('mini gt')
        if 'pop race' in t: tags.append('pop race')
        if 'hot wheels' in t: tags.append('hot wheels')
        if 'tarmac' in t: tags.append('tarmac works')
        if '1/64' in t: tags.append('1/64 scale')
        if '1/43' in t: tags.append('1/43 scale')

    # Electronics detection
    if any(kw in t for kw in ['pc', 'gaming', 'electronics', 'gpu', 'motherboard', 'nintendo', 'sega', 'playstation', 'xbox']):
        tags.append('electronics')
        if 'nintendo' in t: tags.append('nintendo')
        if 'sega' in t: tags.append('sega')
        if 'xbox' in t: tags.append('xbox')
        if 'playstation' in t or 'ps4' in t or 'ps5' in t: tags.append('playstation')
        if 'pc' in t or 'gpu' in t or 'motherboard' in t: tags.append('pc hardware')
        
    if len(tags) == 1:
        tags.append('other')
        
    return list(set(tags))

def sync_inventory():
    """Fetches data, caches HTML descriptions, and saves as 'itemSummaries' for site compatibility."""
    raw_items = get_active_ebay_inventory()
    
    if raw_items is None:
        raw_items = []

    output_path = os.path.join(os.getcwd(), 'data', 'inventory.json')
    
    # THE SMART CACHE: Load existing inventory to preserve previously fetched descriptions
    cached_descriptions = {}
    if os.path.exists(output_path):
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                items_list = existing_data.get("itemSummaries", [])
                for item in items_list:
                    item_id = item.get('itemId') or item.get('id')
                    desc = item.get('description') or item.get('html_description')
                    if item_id and desc:
                        cached_descriptions[str(item_id)] = desc
        except Exception as e:
            print(f"Warning: Could not read existing cache: {e}")

    processed = []
    new_description_count = 0

    for item in raw_items:
        title = item.get('title', '')
        item['tags'] = assign_tags(title)
        
        # Determine the unique item identifier from eBay data
        item_id = str(item.get('itemId') or item.get('id') or '')
        current_desc = item.get('description') or item.get('html_description')
        
        # Check cache first to avoid pinging eBay
        if not current_desc and item_id in cached_descriptions:
            item['description'] = cached_descriptions[item_id]
        elif not current_desc and item_id and get_item_description is not None:
            print(f"Fetching description for new item {item_id}...")
            try:
                # Executes eBay API fetch
                desc = get_item_description(item_id)
                if desc:
                    item['description'] = desc
                    new_description_count += 1
                    
                    # THE RATE LIMITER: Force a 3-second pause to protect API standing
                    time.sleep(3)
            except Exception as e:
                print(f"Error fetching description for {item_id}: {e}")

        processed.append(item)
            
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({"itemSummaries": processed}, f, indent=4)
        
    print(f"Sync completed successfully. {len(processed)} items synced ({new_description_count} new descriptions pulled).")

if __name__ == "__main__":
    sync_inventory()
