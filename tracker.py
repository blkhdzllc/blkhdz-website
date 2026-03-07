import os, requests, json, time, re, urllib.parse, datetime

# Get your Scrape.do token from GitHub Secrets
SCRAPE_API_TOKEN = os.getenv("SCRAPE_TOKEN")

# Your verified inventory for March 2026
LEGO_DATA_LIST = [
    {"id": "75354-1", "name": "Coruscant Guard Gunship", "msrp": 139.99},
    {"id": "75356-1", "name": "Executor Super Star Destroyer", "msrp": 69.99},
    {"id": "76286-1", "name": "Guardians Milano", "msrp": 179.99},
    {"id": "75389-1", "name": "The Dark Falcon", "msrp": 179.99},
    {"id": "75337-1", "name": "AT-TE Walker", "msrp": 139.99},
    {"id": "77244-1", "name": "Mercedes-AMG F1 W15 (2024)", "msrp": 26.99}
]

def get_market_price(set_id):
    clean_id = set_id.split('-')[0]
    query = f"LEGO {clean_id} new sealed"
    # Scrape.do call to eBay Sold Listings
    target_url = f"https://www.ebay.com/sch/i.html?_nkw={urllib.parse.quote(query)}&LH_Sold=1&LH_Complete=1&LH_ItemCondition=1000"
    api_url = f"https://api.scrape.do/?token={SCRAPE_API_TOKEN}&url={urllib.parse.quote(target_url)}"
    
    try:
        r = requests.get(api_url, timeout=20)
        # Find all dollar amounts in the HTML
        prices = re.findall(r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2}))', r.text)
        if prices:
            float_prices = sorted([float(p.replace(',', '')) for p in prices])
            # Trim top/bottom to get a solid mid-range average
            if len(float_prices) > 3:
                float_prices = float_prices[1:-1]
            return round(sum(float_prices) / len(float_prices), 2)
    except Exception as e:
        print(f"Error fetching {set_id}: {e}")
        return None
    return None

def run():
    print(f"Starting BLKHDZ Market Sync...")
    lego_final = []
    
    for item in LEGO_DATA_LIST:
        print(f"Checking {item['name']}...")
        market_val = get_market_price(item['id'])
        
        # If eBay fails, use MSRP so the website isn't blank
        final_price = market_val if market_val else item.get('msrp', 0.00)
        
        # Standard Brickset Image Format
        set_num_only = item['id'].split('-')[0]
        img = f"https://images.brickset.com/sets/images/{set_num_only}-1.jpg"
        
        lego_final.append({
            "set_num": item['id'], 
            "name": item['name'], 
            "image_url": img,
            "ebay_avg_price": final_price
        })
        time.sleep(1) # Safety delay

    output = {
        "last_updated": datetime.datetime.now().strftime("%B %d, %Y"), 
        "sets": lego_final
    }
    
    # Save the file
    with open('data.json', 'w') as f:
        json.dump(output, f, indent=4)
    print("Successfully created data.json")

if __name__ == "__main__":
    run()
