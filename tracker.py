import os, requests, json, time, re

# REPLACE THIS with your actual token from Scrape.do
SCRAPE_API_TOKEN = "YOUR_TOKEN_HERE"

LEGO_DATA_LIST = [
    {"id": "75354-1", "name": "Coruscant Guard Gunship"},
    {"id": "71036-1", "name": "Minifigures Series 23 (Set of 6)"},
    {"id": "75356-1", "name": "Executor Super Star Destroyer"},
    {"id": "75274-1", "name": "TIE Fighter Pilot Helmet"},
    {"id": "31167-1", "name": "Creator Haunted Mansion"},
    {"id": "75345-1", "name": "501st Clone Troopers Battle Pack"},
    {"id": "77247-1", "name": "KICK Sauber F1 Team C44"},
    {"id": "76015-1", "name": "Doc Ock Truck Heist"},
    {"id": "76286-1", "name": "Guardians Milano"},
    # --- 2026 Watchlist ---
    {"id": "42224-1", "name": "Rexy the Porsche (42224)"}, 
    {"id": "75349-1", "name": "Captain Rex Helmet"},       
    {"id": "75337-1", "name": "AT-TE Walker"},                             
    {"id": "75389-1", "name": "The Dark Falcon"}
]

def get_market_price(set_num):
    clean_id = set_num.split('-')[0]
    # We query eBay for New/Sealed/Sold listings
    target_url = f"https://www.ebay.com/sch/i.html?_nkw=LEGO+{clean_id}+new+sealed&LH_Sold=1&LH_Complete=1"
    
    # This routes the request through a residential proxy to bypass 2026 blocks
    api_url = f"https://api.scrape.do?token={SCRAPE_API_TOKEN}&url={target_url}"

    try:
        response = requests.get(api_url, timeout=30)
        if response.status_status == 200:
            # Regex for the 2026 eBay price layout
            prices = re.findall(r'POSITIVE">\$([\d,]+\.\d+)', response.text)
            if not prices:
                prices = re.findall(r'item__price.*?\$([\d,]+\.\d+)', response.text, re.DOTALL)
            
            if prices:
                clean_prices = [float(p.replace(',', '')) for p in prices[:10]]
                return round(sum(clean_prices) / len(clean_prices), 2)
    except Exception as e:
        print(f"Scrape failed for {set_num}: {e}")
    
    return "Market TBD"

def run_update():
    final_data = []
    for item in LEGO_DATA_LIST:
        price = get_market_price(item['id'])
        clean_id = item['id'].split('-')[0]
        
        final_data.append({
            "set_num": item['id'],
            "name": item['name'],
            "image_url": f"https://images.brickset.com/sets/images/{clean_id}-1.jpg",
            "ebay_avg_price": price,
            "ebay_link": f"https://www.ebay.com/sch/i.html?_nkw=LEGO+{clean_id}+new+sealed"
        })
        time.sleep(1) # Small gap to be polite

    with open('data.json', 'w') as f:
        json.dump(final_data, f, indent=4)
    print("Market Update Complete.")

if __name__ == "__main__":
    run_update()
