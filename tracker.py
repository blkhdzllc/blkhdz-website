import requests
from bs4 import BeautifulSoup
import re
import statistics

def get_ebay_sold_average(set_id):
    # This mimics the "Last 10 Sold" query I run for you
    search_url = f"https://www.ebay.com/sch/i.html?_nkw=LEGO+{set_id}&LH_Sold=1&LH_Complete=1&_sop=13"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Target the price spans in eBay's search results
    price_tags = soup.find_all('span', class_='s-item__price')
    prices = []

    for tag in price_tags[1:11]: # Skip the first one (often a range or ad)
        price_text = tag.get_text().replace('$', '').replace(',', '')
        # Handle price ranges like "100.00 to 120.00" by taking the first number
        val = re.findall(r"[-+]?\d*\.\d+|\d+", price_text)
        if val:
            prices.append(float(val[0]))

    if prices:
        return round(statistics.mean(prices), 2)
    return "N/A"

# Then, in your main loop, update your data.json with this value:
# data['ebay_avg'] = get_ebay_sold_average(set_id)
