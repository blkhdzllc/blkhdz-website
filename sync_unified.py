import json
import os
import sys

# Ensure the root directory is in the path to allow imports from /services
sys.path.append(os.getcwd())

from services.ebay_client import get_active_ebay_inventory

def sync_inventory():
    """
    Main function to sync eBay items using Finding API structure.
    """
    print("Starting sync_unified process...")
    
    raw_items = get_active_ebay_inventory()
    print(f"Total items fetched from eBay: {len(raw_items)}")
    
    lego_items = []
    diecast_items = []
    
    for item in raw_items:
        # Finding API stores data in lists, e.g., item['title'][0]
        # We safely extract the first element of the list
        title_list = item.get('title', ['Unknown Item'])
        title = title_list[0] if isinstance(title_list, list) else str(title_list)
        
        # Mapping Finding API fields to your website's expected format
        formatted_item = {
            "title": title,
            "itemWebUrl": item.get('viewItemURL', [''])[0],
            "price": {
                "value": item.get('sellingStatus', [{}])[0].get('currentPrice', [{}])[0].get('__value__', '0.00')
            },
            "image": {
                "imageUrl": item.get('galleryURL', [''])[0]
            }
        }
        
        # Categorize based on the title
        if 'lego' in title.lower():
            lego_items.append(formatted_item)
        else:
            diecast_items.append(formatted_item)
            
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
