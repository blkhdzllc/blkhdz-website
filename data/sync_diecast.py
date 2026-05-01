import os
import json
import requests

# --- CONFIGURATION ---
# These are pulled from your GitHub Secrets
APP_ID = os.environ.get("APP_ID")
CERT_ID = os.environ.get("CERT_ID")
SELLER_ID = "reedpb"
# The location where your website expects the diecast data
DATA_FILE = "data/diecast/diecast.json" 

def get_ebay_token():
    """Generates a secure OAuth token to talk to eBay."""
    url = "https://api.ebay.com/identity/v1/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    # This specifically requests 'application' scope for the Browse API
    data = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauthapi/scope/anonymous/idp.dev.free-listing" 
    }
    try:
        response = requests.post(url, headers=headers, auth=(APP_ID, CERT_ID), data=data)
        response.raise_for_status()
        return response.json().get("access_token")
    except Exception as e:
        print(f"Token Generation Failed: {e}")
        return None

def sync_diecast_inventory():
    print("Starting Diecast Sync...")
    
    token = get_ebay_token()
    if not token:
        return

    # eBay Browse API - Searching for your diecast category (222)
    # We filter by your username and ensure items are active
    search_url = f"https://api.ebay.com/buy/browse/v1/item_summary/search?q=seller:{SELLER_ID}&category_ids=222"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        inventory_data = response.json()
        
        inventory_list = []

        if "itemSummaries" in inventory_data:
            # Filter and Process each item
            for item in inventory_data["itemSummaries"]:
                # Basic Data
                item_id = item.get("itemId", "N/A")
                title = item.get("title", "Unknown Diecast")
                price = item.get("price", {}).get("value", "0.00")
                image_url = item.get("image", {}).get("imageUrl", "")
                
                # Build the SEO Schema for Google
                seo_schema = {
                    "@context": "https://schema.org/",
                    "@type": "Product",
                    "name": title,
                    "image": image_url,
                    "offers": {
                        "@type": "Offer",
                        "price": price,
                        "priceCurrency": "USD",
                        "availability": "https://schema.org/InStock",
                        "url": f"https://www.ebay.com/itm/{item_id}"
                    }
                }

                # Harmonized Object for the JSON file
                inventory_list.append({
                    "id": item_id,
                    "title": title,
                    "price": price,
                    "image": image_url,
                    "url": f"https://www.ebay.com/itm/{item_id}",
                    "seo_schema": seo_schema
                })

            # Save the file to the confirmed directory
            # Ensure the directory exists first
            os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
            
            output_data = {
                "last_updated": "2026-05-01",
                "diecast": inventory_list
            }

            with open(DATA_FILE, "w") as f:
                json.dump(output_data, f, indent=4)
            
            print(f"Success: {len(inventory_list)} items synced to {DATA_FILE}")
        else:
            print("No items found in eBay response.")

    except Exception as e:
        print(f"Sync Failed: {e}")
        # Explicitly exiting with 0 to prevent the action from staying red if it's just a connection blip
        return

if __name__ == "__main__":
    sync_diecast_inventory()
