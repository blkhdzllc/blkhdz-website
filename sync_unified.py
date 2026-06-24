import json
import os
import sys
sys.path.append(os.getcwd())
from services.ebay_client import get_active_ebay_inventory

def assign_tags(title):
    t = title.lower()
    tags = ['all']
    
    # 1. LEGO Sub-categories
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

    # 2. DIECAST Sub-categories
    if any(kw in t for kw in ['diecast', 'pop race', 'hot wheels', 'mini gt', 'tarmac', 'spark', 'looksmart', '1/64', '1/43']): 
        tags.append('diecast')
        if 'hot wheels' in t: tags.append('hot wheels')
        if 'mini gt' in t: tags.append('mini gt')
        if 'pop race' in t: tags.append('pop race')
        if 'tarmac' in t: tags.append('tarmac works')
        if '1/64' in t: tags.append('1/64 scale')
        if '1/43' in t: tags.append('1/43 scale')

    # 3. ELECTRONICS Sub-categories
    if any(kw in t for kw in ['pc', 'gaming', 'electronics', 'gpu', 'motherboard', 'nintendo', 'sega', 'playstation', 'xbox']):
        tags.append('electronics')
        if 'nintendo' in t: tags.append('nintendo')
        if 'sega' in t: tags.append('sega')
        if 'xbox' in t: tags.append('xbox')
        if 'playstation' in t or 'ps4' in t or 'ps5' in t: tags.append('playstation')
        if 'pc' in t or 'gpu' in t or 'motherboard' in t: tags.append('pc hardware')
        
    return list(set(tags))

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
