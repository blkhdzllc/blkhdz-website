import json
import os
import sys

# Ensure the root directory is in the path to allow imports from /services
sys.path.append(os.getcwd())

# Import the inventory fetcher from your services folder
from services.ebay_client import get_active_ebay_inventory

# Helper to safely extract Finding API list data
def get_val(item, key):
    # Finding API data is often returned as a list containing one element
    val = item.get(key, [''])
    return val[0] if isinstance(val, list) and len(val) > 0 else ''

def sync_inventory():
    """
    Main function to sync eBay items into a unified JSON structure
    mapped to the format required by the website.
    """
    print("Starting sync_unified process...")
    
    # Fetch active items from eBay via your ebay_client
    raw_items = get_active_ebay_inventory()
    print(f"Total items fetched from eBay: {len(raw_items)}")
    
    lego_items = []
    diecast_items = []
    
    for item in raw_items:
        # Extract title safely
        title = get_val(item, 'title').lower()
        
        # Create a dictionary that matches the expectations of your index.html
        formatted_item = {
            "title": get_val(item, 'title'),
            "itemWebUrl": get_val(item, 'viewItemURL'),
            "price": {
                "value": item.get('sellingStatus', [{}])[0].get('currentPrice', [{}])[0].get('__value__', '0.00')
            },
            "image": {
                "imageUrl": get_val(item, 'galleryURL')
            }
        }
        
        # Categorize items
        if 'lego' in title:
            lego_items.append(formatted_item)
        else:
            diecast_items.append(formatted_item)
            
    # Structure for the website
    unified_data = {
        "lego": lego_items,
        "diecast": diecast_items
    }
    
    # Prepare the output directory
    output_path = os.path.join('data', 'inventory.json')
    os.makedirs('data', exist_ok=True)
    
    # Write to the file
    with open(output_path, 'w') as f:
        json.dump(unified_data, f, indent=4)
        
    # Verify file was written
    if os.path.exists(output_path):
        size = os.path.getsize(output_path)
        print(f"File written successfully. Size: {size} bytes.")
    
    print(f"Sync complete. LEGO: {len(lego_items)}, Diecast: {len(diecast_items)}")

if __name__ == "__main__":
    sync_inventory()
