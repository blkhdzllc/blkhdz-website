import os, requests, json, time, re, random
from bs4 import BeautifulSoup

API_KEY = os.environ.get('REBRICKABLE_KEY')
SET_NUMBERS = ["75192-1", "10333-1", "75313-1", "75290-1", "10316-1", "75308-1", "10307-1", "75341-1", "10302-1"]

def get_ebay_avg(set_id):
    clean_id = set_id.split('-')[0]
    # Search for sold/completed listings specifically
    url = f"https://www.ebay.com/sch/i.html?_nkw=LEGO+{clean_id}+new+sealed&LH_Sold=1&LH_Complete=1"
    
    # This header makes you look like a real Chrome browser user
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    try:
        time.sleep(random.uniform(2, 5)) # Random wait so eBay doesn't block you
        res = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        prices = []
        
        # Find the price spans on the page
        for tag in soup.find_all('span', class_='s-item__price'):
            price_text = tag.get_text().replace('$', '').replace(',', '')
            # Handle price ranges like "100.00 to 150.00" by taking the first number
            val = re.findall(r"\d+\.\d+", price_text)
            if val:
                price_float = float(val[0])
                if price_float > 10: # Filter out small accessory/part sales
                    prices.append(price_float)
        
        if len(prices) > 2:
            # Average the last 5-10 sales
            subset = prices[:10]
            return round(sum(subset) / len(subset), 2)
    except Exception as e:
        print(f"Error fetching eBay for {set_id}: {e}")
    return "TBD"

def run():
    results = []
    # Force the "key " prefix if it's missing
    prefix = "key " if API_KEY and not API_KEY.startswith("key ") else ""
    auth_header = f"{prefix}{API_KEY}"
    
    for sn in SET_NUMBERS:
        print(f"Tracking Set: {sn}...")
        try:
            r = requests.get(f"https://rebrickable.com/api/v3/lego/sets/{sn}/", headers={'Authorization': auth_header})
            data = r.json()
            avg = get_ebay_avg(sn)
            
            results.append({
                "set_num": sn,
                "name": data.get('name', 'Unknown LEGO Set'),
                "image_url": data.get('set_img_url', ''),
                "ebay_avg_price": avg,
                "status": "Trending" if avg != "TBD" else "Researching"
            })
        except Exception as e:
            print(f"Rebrickable Error: {e}")
        
    with open('data.json', 'w') as f:
        json.dump(results, f, indent=4)
    print("Market Data Saved to data.json")

if __name__ == "__main__":
    run()
