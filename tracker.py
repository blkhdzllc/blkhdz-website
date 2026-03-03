import os, requests, json, time, re

# GET YOUR TOKEN at Scrape.do
SCRAPE_API_TOKEN = "YOUR_TOKEN_HERE"

LEGO_DATA_LIST = [
    {"id": "75354-1", "name": "Coruscant Guard Gunship"},
    {"id": "75337-1", "name": "AT-TE Walker"},
    {"id": "75389-1", "name": "The Dark Falcon"},
    {"id": "42224-1", "name": "Rexy the Porsche (42224)"}
]

def get_market_price(set_num):
    clean_id = set_num.split('-')[0]
    target_url = f"https://www.ebay.com/sch/i.html?_nkw=LEGO+{clean_id}+new+sealed&LH_Sold=1&LH_Complete=1"
    api_url = f"https://api.scrape.do?token={SCRAPE_API_TOKEN}&url={target_url}"

    try:
        r = requests.get(api_url, timeout=30)
        # MARCH 2026 MULTI-TARGET SEARCH: Finds prices even if eBay moves them
        # Target 1: The 'POSITIVE' span (Standard Sold)
        # Target 2: The 's-item__price' (Listing view)
        # Target 3: The 'BOLD' price tag (New 2026 variant)
        patterns = [
            r'POSITIVE">\$([\d,]+\.\d+)', 
            r'item__price.*?\$([\d,]+\.\d+)',
            r's-item__price">\$([\d,]+\.\d+)'
        ]
        
        found_prices = []
        for pattern in patterns:
            matches = re.findall(pattern, r.text, re.DOTALL)
            if matches:
                found_prices.extend([float(p.replace(',', '')) for p in matches[:10]])
                break # Stop once we find a working pattern

        if found_prices:
            avg = round(sum(found_prices) / len(found_prices), 2)
            print(f"Verified {set_num}: ${avg}")
            return avg
            
    except Exception as e:
        print(f"Connection error for {set_num}: {e}")
    
    return "Market TBD"

def run():
    final = []
    for item in LEGO_DATA_LIST:
        price = get_market_price(item['id'])
        clean_id = item['id'].split('-')[0]
        final.append({
            "set_num": item['id'],
            "name": item['name'],
            "image_url": f"https://images.brickset.com/sets/images/{clean_id}-1.jpg",
            "ebay_avg_price": price,
            "ebay_link": f"https://www.ebay.com/sch/i.html?_nkw=LEGO+{clean_id}+new+sealed"
        })
    with open('data.json', 'w') as f:
        json.dump(final, f, indent=4)

if __name__ == "__main__":
    run()
