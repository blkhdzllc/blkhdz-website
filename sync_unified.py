import json
import os
import sys

sys.path.append(os.getcwd())
from services.ebay_client import get_active_ebay_inventory

def assign_tags(title):
    tags = []
    title_lower = title.lower()

    # --- LEGO Categories ---
    if any(kw in title_lower for kw in ['lego', 'minifig', 'polybag', 'brickheadz']):
        tags.append('lego')
        
        # Sub-themes
        if 'speed champion' in title_lower: tags.append('speed champions')
        if 'nintendo' in title_lower: tags.append('nintendo')
        if 'star wars' in title_lower: tags.append('star wars')
        if 'sega' in title_lower or 'sonic' in title_lower: tags.append('sega')
        if 'marvel' in title_lower: tags.append('marvel')
        if 'creator' in title_lower: tags.append('creator')
        if 'city' in title_lower: tags.append('city')
        if 'minifig' in title_lower or 'polybag' in title_lower: tags.append('minifigs')
        if 'icons' in title_lower: tags.append('icons')
        if 'brickheadz' in title_lower: tags.append('brickheadz')
        if 'technic' in title_lower: tags.append('technic')
        if 'architecture' in title_lower: tags.append('architecture')
        if 'botanical' in title_lower: tags.append('botanicals')
        if 'pirate' in title_lower: tags.append('pirates')
        if 'harry potter' in title_lower: tags.append('harry potter')
        if 'ideas' in title_lower: tags.append('ideas')
        if 'lotr' in title_lower or 'lord of the rings' in title_lower: tags.append('lotr')
        if 'ninjago' in title_lower: tags.append('ninjago')
        if 'hobbit' in title_lower: tags.append('the hobbit')

    # --- Diecast Categories ---
    if any(kw in title_lower for kw in ['diecast', '1/64', '1/43', 'hot wheels', 'pop race', 'spark', 'tsm', 'looksmart']):
        tags.append('diecast')
        
        # Scales
        if '1/64' in title_lower: tags.append('1/64')
        if '1/43' in title_lower: tags.append('1/43')
        
        # Makes and Brands
        makes = ['honda', 'mazda', 'ferrari', 'mercedes', 'porsche', 'nissan', 'toyota']
        for make in makes:
            if make in title_lower:
                tags.append(make)
        if 'hot wheels' in title_lower: tags.append('hot wheels')

    # --- Other Categories ---
    if any(kw in title_lower for kw in ['pc', 'gaming', 'electronics', 'gpu', 'motherboard']):
        tags.append('electronics')
        
    if 'mattel brick shop' in title_lower:
        tags.append('mattel brick shop')

    # Fallback for anything uncategorized
    if not tags:
        tags.append('other')

    return list(set(tags))  # Returns unique tags only

def sync_inventory():
    print("Starting sync_unified process with dynamic tagging...")
    
    raw_items = get_active_ebay_inventory()
    print(f"Total items fetched from eBay: {len(raw_items)}")
    
    processed_items = []
    
    for item in raw_items:
        title = item.get('title', '')
        # Inject the new tags array directly into the item data
        item['tags'] = assign_tags(title)
        processed_items.append(item)
            
    # Output is now a single array of smart-tagged items
    unified_data = {
        "inventory": processed_items
    }
    
    output_path = os.path.join('data', 'inventory.json')
    os.makedirs('data', exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(unified_data, f, indent=4)
        
    print(f"Sync complete. Tagged and saved {len(processed_items)} items.")

if __name__ == "__main__":
    sync_inventory()
