import requests
from bs4 import BeautifulSoup
import urllib.parse
import json

# Replace with your actual Scrape.do API token
SCRAPE_DO_TOKEN = "YOUR_API_TOKEN" 

# Target Walmart item (e.g., Hot Wheels '94 Toyota Supra MKIV)
WALMART_URL = "https://www.walmart.com/ip/18239062303" 

def check_walmart_inventory(url):
    # Scrape.do requires the target URL to be URL-encoded
    encoded_url = urllib.parse.quote(url)
    
    # Construct the API request. 
    # Using render=true tells Scrape.do to execute the page's JavaScript
    api_url = f"https://api.scrape.do/?token={SCRAPE_DO_TOKEN}&url={encoded_url}&render=true"
    
    print(f"Checking inventory for: {url}")
    
    try:
        # Increase timeout slightly as rendering JS can take a few extra seconds
        response = requests.get(api_url, timeout=45)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Walmart often stores structured product data inside a Next.js JSON script tag
        next_data_script = soup.find("script", {"id": "__NEXT_DATA__"})
        
        if next_data_script:
            # If the JSON exists, we load it to check inventory flags
            page_data = json.loads(next_data_script.string)
            data_string = json.dumps(page_data).lower()
            
            # A basic string check against the JSON payload for availability
            if "out of stock" in data_string:
                print("Result: Item is currently Out of Stock.")
                return False
            else:
                print("Result: Item might be IN STOCK! Trigger alerts.")
                return True
        else:
            # Fallback method: checking the rendered visible text for the cart button
            page_text = soup.get_text().lower()
            if "add to cart" in page_text and "out of stock" not in page_text:
                print("Result: IN STOCK (Fallback verification).")
                return True
            else:
                print("Result: Out of Stock (or page structure changed).")
                return False

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return False

if __name__ == "__main__":
    check_walmart_inventory(WALMART_URL)
