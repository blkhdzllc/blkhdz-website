import os, requests, json, time, re, statistics
from bs4 import BeautifulSoup

API_KEY = os.environ.get('REBRICKABLE_KEY')
SET_NUMBERS = ["75192-1", "10333-1", "75313-1", "75290-1", "10316-1", "75308-1", "10307-1", "75341-1", "10302-1"]

def get_ebay_avg(set_id):
    clean_id = set_id.split('-')[0]
    url = f"https://www.ebay.com/sch/i.html?_nkw=LEGO+{clean_id}+new+sealed&LH_Sold=1&LH_Complete=1"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        prices = []
        for tag in soup.find_all('span', class_='s-item__price')[1:11]:
            val = re.findall(r"\d+\.\d+", tag.get_text().replace(',', ''))
            if val: prices.append(float(val[0]))
        return round(statistics.mean(prices), 2) if prices else "TBD"
    except: return "TBD"

def run():
    results = []
    auth_header = f"key {API_KEY}" if API_KEY and not API_KEY.startswith('key ') else API_KEY
    for sn in SET_NUMBERS:
        try:
            r = requests.get(f"https://rebrickable.com/api/v3/lego/sets/{sn}/", headers={'Authorization': auth_header})
            data = r.json()
            avg = get_ebay_avg(sn)
            results.append({
                "set_num": sn,
                "name": data.get('name', 'Unknown LEGO Set'),
                "image_url": data.get('set_img_url', ''),
                "ebay_avg_price": avg,
                "status": "Market Active" if avg != "TBD" else "Researching"
            })
        except: pass
        time.sleep(1)
    with open('data.json', 'w') as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    run()
