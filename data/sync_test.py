import os
import json
import requests
import glob  # NPW: Added for recursive folder searching

# ... (keep your existing tokens and settings at the top)

def sync_enriched_data(category_name, query):
    # ... (keep your existing eBay token logic)

    if "itemSummaries" in data:
        for item in data["itemSummaries"]:
            raw_id = item.get('legacyItemId')
            if not raw_id: continue

            # --- NEW RECURSIVE IMAGE LOGIC ---
            # This looks in images/ AND images/diecast/ AND images/lego/
            # It searches for any file that starts with the SKU/Set Number
            search_pattern = os.path.join(base_dir, "images", "**", "*.*")
            all_files = glob.glob(search_pattern, recursive=True)
            
            # Find files that match this specific item
            # We look for the SKU (like PR64226 or 75337) in the filename
            sku_match = None
            title_upper = item.get('title', '').upper()
            
            # We filter for only the images that belong to THIS item
            local_gallery = []
            for f in all_files:
                filename = os.path.basename(f)
                # Check if the SKU is in the filename (e.g., PR64226.png)
                # We use a simple check: if the filename starts with a known ID from the title
                # For Diecast, we'll look for that PR/PN number
                if any(sku in filename for sku in ["PR", "PN", "753", "752"]): # Common prefixes
                    # (Advanced logic: we can extract the SKU from the filename and compare)
                    pass 

            # SIMPLIFIED NPW APPROACH: 
            # Get all images in the subfolders and filter them
            valid_images = [f for f in all_files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            
            item_images = []
            for img_path in valid_images:
                img_name = os.path.basename(img_path).split('_')[0].split('.')[0]
                # If the image name (like PR64226) is found in the eBay Title
                if img_name.upper() in item.get('title', '').upper().replace("-", ""):
                    # Convert to a relative URL the website can use
                    rel_path = os.path.relpath(img_path, base_dir).replace("\\", "/")
                    item_images.append(f"./{rel_path}")

            # Sort so .png (Hero shots) come first, then the numbered shots (_1, _2)
            item_images.sort(key=lambda x: (not x.lower().endswith('.png'), x))
            
            # Combine with eBay's default image as a backup
            main_img = item.get('image', {}).get('imageUrl')
            ebay_images = [main_img] if main_img else []
            item['customGallery'] = item_images + ebay_images
            # ----------------------------------

            # ... (keep the rest of your description and saving logic)
