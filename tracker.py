import requests
from bs4 import BeautifulSoup
import json
import os
import time

# SETS TO TRACK
WATCHLIST = ["75192-1", "10333-1", "75313-1"]

def get_ebay_price(set_num):
    # Extract just the number (e.g., 75192)
    clean_id = set_num.split('-')[0]
    search_url = f"https://www.ebay.com/sch/i.html?_nkw=LEGO+{clean_id}+new+sealed&LH_Sold=1&LH_Complete=1"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(search_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        prices = soup.find_all('span', class_='s-item__price')
        
        valid_prices = []
        for p in prices:
            text = p.get_text().replace('$', '').replace(',', '')
            if 'to' not in text: # Skip price ranges
                try:
                    valid_prices.append(float(text))
                except: continue
        
        if valid_prices:
            # Get average of last few sales
            avg = sum(valid_prices[:10]) / len(valid_prices[:10])
            return round(avg, 2)
    except Exception as e:
        print(f"Ebay Error for {set_num}: {e}")
    return "Market Volatile"

def update_tracker():
    api_key = os.getenv("REBRICKABLE_KEY")
    # Crucial: Rebrickable needs the word 'key' before the actual string
    headers = {"Authorization": f"key {api_key}"}
    
    new_data = []
    
    for set_num in WATCHLIST:
        print(f"Syncing {set_num}...")
        rb_url = f"https://rebrickable.com/api/v3/lego/sets/{set_num}/"
        
        try:
            rb_res = requests.get(rb_url, headers=headers)
            rb_data = rb_res.json()
            
            market_price = get_ebay_price(set_num)
            
            new_data.append({
                "set_num": set_num,
                "name": rb_data.get("name", "Unknown Set"),
                "image_url": rb_data.get("set_img_url", ""),
                "year": rb_data.get("year"),
                "ebay_avg_price": market_price,
                "status": "Trending" if isinstance(market_price, float) else "Researching"
            })
            time.sleep(2) # Prevent IP bans
        except Exception as e:
            print(f"Failed to sync {set_num}: {e}")

    with open('data.json', 'w') as f:
        json.dump(new_data, f, indent=4)

if __name__ == "__main__":
    update_tracker()
