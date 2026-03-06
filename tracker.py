import os, requests, json, time, re, urllib.parse, datetime

SCRAPE_API_TOKEN = os.getenv("SCRAPE_TOKEN")

LEGO_DATA_LIST = [
    {"id": "75354-1", "name": "Coruscant Guard Gunship", "msrp": 139.99},
    {"id": "71036-1", "name": "Minifigures Series 23 (6-Pack)", "msrp": 29.99},
    {"id": "75356-1", "name": "Executor Super Star Destroyer", "msrp": 69.99},
    {"id": "75274-1", "name": "TIE Fighter Pilot Helmet", "msrp": 425.00}, # Adjusted MSRP to 2026 Market Floor
    {"id": "31167-1", "name": "Creator Haunted Mansion", "msrp": 88.99},
    {"id": "75345-1", "name": "501st Clone Troopers Battle Pack", "msrp": 19.99},
    {"id": "77247-1", "name": "KICK Sauber F1 Team C44", "msrp": 26.99},
    {"id": "76286-1", "name": "Guardians Milano", "msrp": 179.99},
    {"id": "75389-1", "name": "The Dark Falcon", "msrp": 179.99},
    {"id": "76332-1", "name": "The Batman Batmobile (2026)"},
    {"id": "75435-1", "name": "Battle of Felucia Separatist MTT"},
    {"id": "42224-1", "name": "Rexy the Porsche (42224)"},
    {"id": "71858-1", "name": "Ninjago 15th Anniv. Blacksmith"},
    {"id": "71847-1", "name": "Ninjago The Guardian Dragon"},
    {"id": "30726-1", "name": "Bruce Wayne & Batsuit Polybag"},
    {"id": "75349-1", "name": "Captain Rex Helmet", "msrp": 69.99},
    {"id": "75337-1", "name": "AT-TE Walker", "msrp": 139.99}
]

def get_market_price(set_id, name):
    clean_id = set_id.split('-')[0]
    # More aggressive search query to force "New & Sealed"
    query = f"LEGO {clean_id} new sealed -used -parts -damaged"
    
    # Strictly filtering for Sold, Completed, New (1000), and Buy It Now to see real market value
    target_ebay_url = f"https://www.ebay.com/sch/i.html?_nkw={urllib.parse.quote(query)}&LH_Sold=1&LH_Complete=1&LH_ItemCondition=1000&LH_BIN=1"
    api_url = f"https://api.scrape.do/?token={SCRAPE_API_TOKEN}&url={urllib.parse.quote(target_ebay_url)}"
    
    try:
        r = requests.get(api_url, timeout=30)
        prices = re.findall(r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2}))', r.text)
        
        if prices:
            float_prices = sorted([float(p.replace(',', '')) for p in prices], reverse=True)
            
            # ELITE LOGIC: 
            # We take the TOP 4 highest recent sales. 
            # This ignores the "Sticker only" or "Box only" listings that plague the bottom of the search results.
            valid_sales = float_prices[:4] 
            avg_price = sum(valid_sales) / len(valid_sales)
            
            # Final sanity check: Market price for retired sets shouldn't be lower than original MSRP
            return round(avg_price, 2)
            
    except Exception as e:
        print(f"Error scraping {clean_id}: {e}")
    return None

def run():
    print(f"Update Start: {datetime.datetime.now()}")
    lego_final = []
    
    for item in LEGO_DATA_LIST:
        print(f"Syncing: {item['name']}...")
        market_val = get_market_price(item['id'], item['name'])
        
        # Determine final price: Use scraped value, but don't let it fall below MSRP for retired items
        final_price = market_val if market_val and market_val > item.get('msrp', 0) else item.get('msrp', "TBD")

        img = f"https://images.brickset.com/sets/images/{item['id'].split('-')[0]}-1.jpg"
        if "71036" in item['id']:
            img = "https://images.brickset.com/sets/AdditionalImages/71036-1/71036_Lifestyle_1.jpg"

        lego_final.append({
            "set_num": item['id'], 
            "name": item['name'], 
            "image_url": img,
            "ebay_avg_price": final_price,
            "ebay_link": f"https://www.ebay.com/sch/i.html?_nkw=LEGO%20{item['id'].split('-')[0]}%20new%20sealed&LH_ItemCondition=1000"
        })
        time.sleep(2) # Extra delay for better scraping results

    output = {"last_updated": datetime.datetime.now().strftime("%B %d, %Y"), "sets": lego_final}
    with open('data.json', 'w') as f:
        json.dump(output, f, indent=4)
    print("Market Sync Complete.")

if __name__ == "__main__":
    run()
