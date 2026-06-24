import json
import os
import sys
import logging

# Configure detailed logging so you can see exactly what happens in GitHub Actions
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ensure the script can find the services folder in your root directory
sys.path.append(os.getcwd())

try:
    from services.ebay_client import get_active_ebay_inventory
except ImportError as e:
    logging.error(f"Failed to import ebay_client: {e}")
    sys.exit(1)

def assign_tags(title):
    """
    Parses the item title and assigns category tags.
    Robust handling with fallbacks.
    """
    if not title:
        return ['all']
        
    t = title.lower()
    tags = ['all']
    
    # Category Classification Logic
    if any(kw in t for kw in ['lego', 'minifig', 'brickheadz', 'polybag', 'star wars', 'ninjago', 'city', 'technic', 'creator', 'icons']):
        tags.append('lego')
    if any(kw in t for kw in ['diecast', 'hot wheels', 'matchbox', 'pop race', 'mini gt', 'tarmac', 'spark', 'tsm', 'looksmart']):
        tags.append('diecast')
    if any(kw in t for kw in ['pc', 'gaming', 'electronics', 'gpu', 'motherboard', 'nintendo', 'sega']):
        tags.append('electronics')
        
    # Return unique list
    return list(set(tags))

def sync_inventory():
    logging.info("Starting comprehensive inventory sync process...")
    
    # 1. Fetch raw items from the batch-optimized client
    try:
        raw_items = get_active_ebay_inventory()
    except Exception as e:
        logging.error(f"Unexpected error during eBay fetch: {e}")
        sys.exit(1)
    
    # 2. Strict validation
    if raw_items is None:
        logging.error("eBay client returned None. Check API connection.")
        sys.exit(1)
        
    if len(raw_items) == 0:
        logging.warning("No items were returned. Preventing overwrite of inventory.json.")
        sys.exit(1)

    logging.info(f"Successfully retrieved {len(raw_items)} items from eBay API.")

    # 3. Process items with full error trapping
    processed_items = []
    for item in raw_items:
        try:
            # Safely get the title
            title = item.get('title', 'Unknown Item')
            
            # Inject tags
            item['tags'] = assign_tags(title)
            processed_items.append(item)
        except Exception as e:
            logging.warning(f"Skipping item due to error: {e}")
            continue
            
    # 4. Save file with atomic write operations
    output_dir = os.path.join(os.getcwd(), 'data')
    output_path = os.path.join(output_dir, 'inventory.json')
    
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        # Prepare the final JSON structure
        final_data = {
            "inventory": processed_items,
            "itemSummaries": processed_items,
            "metadata": {
                "total_items": len(processed_items),
                "status": "success"
            }
        }
        
        # Atomic Write: Write to temp, then replace (prevents file corruption)
        temp_path = output_path + ".tmp"
        with open(temp_path, 'w') as f:
            json.dump(final_data, f, indent=4)
            f.flush()
            os.fsync(f.fileno())
        
        os.replace(temp_path, output_path)
        logging.info(f"Inventory successfully synced. {len(processed_items)} items saved to {output_path}")
        
    except Exception as e:
        logging.error(f"Failed to write inventory file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    sync_inventory()
