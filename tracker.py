import os, requests, json, time, re
import urllib.parse

# ==========================================================
# CONFIGURATION - BLKHDZ ELITE TRACKER
# ==========================================================
SCRAPE_API_TOKEN = "3687f040467644d5a62797baa02ffba5f13b60e27d5"

# ==========================================================
# INVENTORY DATA
# ==========================================================
LEGO_DATA_LIST = [
    {"id": "75354-1", "name": "Coruscant Guard Gunship", "price": 139.99},
    {"id": "71036-1", "name": "Minifigures Series 23 (Set of 6)", "price": 49.95},
    {"id": "75356-1", "name": "Executor Super Star Destroyer", "price": 69.99},
    {"id": "75274-1", "name": "TIE Fighter Pilot Helmet", "price": 325.00},
    {"id": "31167-1", "name": "Creator Haunted Mansion", "price": 88.99},
    {"id": "75345-1", "name": "501st Clone Troopers Battle Pack", "price": 19.99},
    {"id": "77247-1", "name": "KICK Sauber F1 Team C44", "price": 26.99},
    {"id": "76015-1", "name": "Doc Ock Truck Heist", "price": 45.00},
    {"id": "76286-1", "name": "Guardians Milano", "price": 179.99},
    # 2026 WATCHLIST ITEMS - These trigger the deep scraper
    {"id": "42224-1", "name": "Rexy the Porsche (42224)"}, 
    {"id": "75349-1", "name": "Captain Rex Helmet"},       
    {"id": "75337-1", "name": "AT-TE Walker"},                             
    {"id": "75389-1", "name": "The Dark Falcon"},                          
    {"id": "71858-1", "name": "Ninjago 2026 Set A"}, 
    {"id": "71847-1", "name": "Ninjago 2026 Set B"},
    {"id": "30726-1", "name": "2026 Polybag"},
    {"id": "76332-1", "name": "Marvel 2026"},
    {"id": "75435-1", "name": "Star Wars 2026"}
]

DIECAST_LIST = [
    {"id": "TW-911-54", "name": "Tarmac Works Porsche 911 #54", "img": "Porsche 54.jpg", "p": 39.99},
    {"id": "TW-AMG-BIL", "name": "Mercedes-AMG GT3 Team Bilstein", "img": "Mercedez 4.jpg", "p": 31.99},
    {"id": "TW-AMG-BH", "name": "Mercedes-AMG GT3 Bathurst", "img": "Mercedes 2.jpg", "p": 34.95},
    {"id": "SPK-CIV-16", "name": "Spark Honda Civic Type R-GT", "img": "Honda 16.jpg", "p": 134.95},
    {"id": "TW-F488-51", "name": "Ferrari 488 GT3 Macau #51", "img": "Ferrari 51.jpg", "p": 31.99}
]

# ==========================================================
# BRICKHAWK-INSPIRED PRICING ALGORITHM
# ==========================================================
def get_market_price(set_id):
    clean_id = set_id.split('-')[0]
    # Filter for US-Only, New, Sold listings
    query = f"LEGO {clean_id} new sealed"
    ebay_url = f"https://www.ebay.com/sch/i.html?_nkw={urllib.parse.quote(query)}&LH_Sold=1&LH_Complete=1&LH_PrefLoc=1&LH_ItemCondition=1000"
    
    # Step 1: Secure Request via Scrape.do with 'Super' mode to bypass blocks
    api_url = f"https://api.scrape.do/?token={SCRAPE_API_TOKEN}&url={urllib.parse.quote(ebay_url)}&super=true"
    
    try:
        r = requests.get(api_url, timeout=30)
        # Step 2: Extract all prices from the 'POSITIVE' results
        prices = re.findall(r'POSITIVE">\$([\d,]+\.\d+)', r.text)
        
        if not prices:
            # Fallback for newer eBay UI layouts
            prices = re.findall(r's-item__price">.*?\$([\d,]+\.\d+)', r.text)
            
        if prices:
            # Step 3: Outlier Removal (The Algorithm)
            float_prices = sorted([float(p.replace(',', '')) for p in prices])
            
            # Remove the top and bottom 10% to eliminate "fake" or "parts" sales
            if len(float_prices) > 5:
                trim = max(1, len(float_prices) // 10)
                float_prices = float_prices[trim:-trim]
                
            avg_price = sum(float_prices) / len(float_prices)
            return round(avg_price, 2)
            
    except Exception as e:
        print(f"Algorithm Error for {clean_id}: {e}")
    
    return "Market TBD"

def run():
    print("--- BLKHDZ MARKET SYNC STARTING ---")
    
    # Update LEGO/Watchlist
    lego_final = []
    for item in LEGO_DATA_LIST:
        clean_id = item['id'].split('-')[0]
        # Use existing price if it exists, otherwise trigger the deep scraper
        val_price = item.get('price', get_market_price(item['id']))
        img = f"https://images.brickset.com/sets/images/{clean_id}-1.jpg"
        
        if "71036" in item['id']:
            img = "https://images.brickset.com/sets/AdditionalImages/71036-1/71036_Lifestyle_1.jpg"

        lego_final.append({
            "set_num": item['id'], "name": item['name'], "image_url": img,
            "ebay_avg_price": val_price,
            "ebay_link": f"https://www.ebay.com/sch/i.html?_nkw=LEGO%20{clean_id}%20new%20sealed&mkcid=1&mkrid=711-53200-19255-0&campid=5339141674&customid=BLKHDZ_WEB"
        })
        print(f"Synced {item['name']}: ${val_price}")

    # Update Diecast
    diecast_final = []
    for car in DIECAST_LIST:
        diecast_final.append({
            "set_num": car['id'], "name": car['name'], "image_url": car['img'],
            "ebay_avg_price": car['p'],
            "ebay_link": f"https://www.ebay.com/sch/i.html?_nkw={car['name'].replace(' ', '%20')}&mkcid=1&mkrid=711-53200-19255-0&campid=5339141674&customid=BLKHDZ_WEB"
        })

    # Save to disk
    with open('data.json', 'w') as f: json.dump(lego_final, f, indent=4)
    with open('diecast.json', 'w') as f: json.dump(diecast_final, f, indent=4)
    print("--- SYNC COMPLETE. FILES UPDATED. ---")

if __name__ == "__main__":
    run()
