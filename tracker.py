import os
import requests
import json
from bs4 import BeautifulSoup
import re
import statistics
import time

# --- CONFIGURATION ---
# Replace the API key if you aren't using GitHub Secrets
REBRICKABLE_API_KEY = os.environ.get('REBRICKABLE_KEY')

# YOUR 9 SETS
SET_NUMBERS = [
    "75192-1",  # Millennium Falcon
    "10333-1",  # Barad-dûr
    "75313-1",  # AT-AT
    "75290-1",  # Mos Eisley Cantina
    "10316-1",  # Rivendell
    "75308-1",  # R2-D2
    "10307-1",  # Eiffel Tower
    "75341-1",  # Luke's Landspeeder
    "10302-1"   # Optimus Prime
]

def get_ebay_sold_average(set_id):
    """Scrapes the last 10 sold prices from eBay for the specific LEGO set."""
    clean_id = set_id.split('-')[0]
    # Search for "LEGO [Set Number]" in Sold/Completed listings
    search_url = f"https://www.ebay.com/sch/i.html?_nkw=LEGO+{clean_id}&LH_Sold=1&LH_Complete=1&_sop=13"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        response = requests.get(search_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        price_tags = soup.find_all('span', class_='s-item__price')
        
        prices = []
        # We take up to 10 results, skipping the first one which is often a placeholder
        for tag in price_tags[1:11]: 
            price_text = tag.get_text().replace('$', '').replace(',', '')
            # Handle ranges (e.g., "100.00 to 120.00") by taking the first number
            val = re.findall(r"[-+]?\d*\.\d+|\d+", price_text)
            if val:
                prices.append(float(val[0]))
        
        if prices:
            return round(statistics.mean(prices), 2)
        return 0.0
    except Exception as e:
        print(f"Error fetching eBay data for {set_id}: {e}")
        return 0.0

def fetch_lego_data():
    all_data = []
    
    for set_num in SET_NUMBERS:
        print(f"Processing Set: {set_num}...")
        
        # 1. Fetch Basic Info from Rebrickable
        rb_url = f"https://rebrickable.com/api/v3/lego/sets/{set_num}/"
        headers = {'Authorization': f'key {REBRICKABLE_API_KEY}'}
        
        try:
            rb_res = requests.get(rb_url, headers=headers).json()
            
            # 2. Fetch Market Average from eBay
            ebay_avg = get_ebay_sold_average(set_num)
            
            # 3. Assemble the dataset
            set_info = {
                "set_num": set_num,
                "name": rb_res.get('name', 'Unknown LEGO Set'),
                "image_url": rb_res.get('set_img_url', ''),
                "year": rb_res.get('year', 'N/A'),
                "ebay_avg_price": ebay_avg if ebay_avg > 0 else "TBD",
                # If we found eBay sales, it's 'Market Active'
                "status": "Market Active" if ebay_avg > 0 else "Researching"
            }
            all_data.append(set_info)
            
            # Small sleep to avoid hitting rate limits
            time.sleep(1)
            
        except Exception as e:
            print(f"Failed to process {set_num}: {e}")

    # 4. Save to data.json for the index.html to read
    with open('data.json', 'w') as f:
        json.dump(all_data, f, indent=4)
    print("Successfully updated data.json with 9 sets.")

if __name__ == "__main__":
    fetch_lego_data()
