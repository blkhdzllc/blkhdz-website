import os
import json
import urllib.parse
import requests
from bs4 import BeautifulSoup

# Securely fetch the API token from GitHub Actions environment variables
SCRAPE_DO_TOKEN = os.environ.get("SCRAPE_DO_TOKEN")

# Target Walmart items
TARGET_URLS = [
    "https://www.walmart.com/ip/18239062303", # Hot Wheels '94 Toyota Supra MKIV
    "https://www.walmart.com/ip/HW-Speed-Chevy/18257406985"  # Mattel Brick Shop Hot Wheels '83 Chevy Silverado (Black Edition)
]

def check_walmart_inventory(url):
    if not SCRAPE_DO_TOKEN:
        print("Error: SCRAPE_DO_TOKEN environment variable is not set.")
        return False

    encoded_url = urllib.parse.quote(url)
    api_url = f"https://api.scrape.do/?token={SCRAPE_DO_TOKEN}&url={encoded_url}&render=true"
    
    print(f"Checking inventory for: {url}")
    
    try:
        response = requests.get(api_url, timeout=45)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        next_data_script = soup.find("script", {"id": "__NEXT_DATA__"})
        
        if next_data_script:
            page_data = json.loads(next_data_script.string)
            
            # Target the specific product's status instead of the whole page
            product_data = page_data.get("props", {}).get("pageProps", {}).get("initialData", {}).get("data", {}).get("product", {})
            inventory_status = product_data.get("inventoryStatus", "").upper()
            
            if inventory_status == "IN_STOCK":
                print("Result: Item might be IN STOCK! Trigger alerts.\n")
                return True
            else:
                print("Result: Item is currently Out of Stock.\n")
                return False
        else:
            page_text = soup.get_text().lower()
            if "add to cart" in page_text and "out of stock" not in page_text:
                print("Result: IN STOCK (Fallback verification).\n")
                return True
            else:
                print("Result: Out of Stock (or page structure changed).\n")
                return False

    except requests.exceptions.RequestException as e:
        print(f"Request failed for {url}: {e}\n")
        return False

if __name__ == "__main__":
    for item_url in TARGET_URLS:
        check_walmart_inventory(item_url)
