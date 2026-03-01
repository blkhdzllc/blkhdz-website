import os
import requests
import json
from bs4 import BeautifulSoup
import re
import statistics

# Configuration
REBRICKABLE_API_KEY = os.environ.get('REBRICKABLE_API_KEY')
SET_NUMBERS = ["75192-1", "10333-1", "75313-1"] # Add your sets here

def get_ebay_sold_average(set_id):
    # Clean the set ID for eBay (remove the -1 suffix if it exists)
    clean_id = set_id.split('-')[0]
    search_url = f"https://www.ebay.com/sch/i.html?_nkw=LEGO+{clean_id}&LH_Sold=1&LH_Complete=1&_sop=13"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        price_tags = soup.find_all('span', class_='s-item__price')
        
        prices = []
        # Skip the first result as it is often a template/ad
        for tag in price_tags[1:11]: 
            price_text = tag.get_text().replace('$', '').replace(',', '')
            # Handles range prices by taking the first number
            val = re.findall(r"[-+]?\d*\.\d+|\d+", price_text)
            if val:
                prices.append(float(val[0]))
        
        return round(statistics.mean(prices), 2) if prices else 0
    except Exception as e:
        print(f"Error fetching eBay data for {set_id}: {e}")
        return 0

def fetch_lego_data():
    all_data = []
    
    for set_num in SET_NUMBERS:
        # 1. Get Base Data from Rebrickable
        rb_url = f"https://rebrickable.com/api/v3/lego/sets/{set_num}/"
        headers = {'Authorization': f'key {REBRICKABLE_API_KEY}'}
        rb_res = requests.get(rb_url, headers=headers).json()
        
        # 2. Get Live Market Average from eBay
        ebay_avg = get_ebay_sold_average(set_num)
        
        # 3. Compile Data
        set_info = {
            "set_num": set_num,
            "name": rb_res.get('name', 'Unknown'),
            "image_url": rb_res.get('set_img_url', ''),
            "year": rb_res.get('year'),
            "ebay_avg_price": ebay_avg,
            # Logic: If it's selling on eBay, it's not "Retired" in your world
            "status": "Market Active" if ebay_avg > 0 else "Out of Stock"
        }
        all_data.append(set_info)
    
    # Save to data.json for your website to read
    with open('data.json', 'w') as f:
        json.dump(all_data, f, indent=4)

if __name__ == "__main__":
    fetch_lego_data()
