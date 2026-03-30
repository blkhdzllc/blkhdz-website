import requests
from bs4 import BeautifulSoup
import json
import datetime
import os

# Target Sets for Triangulation
TEST_SETS = ["75274", "31167", "71738"]

def get_brickeconomy_data(set_id):
    url = f"https://www.brickeconomy.com/set/{set_id}-1/"
    # Professional Headers to mimic a real browser and avoid "Bot Blocks"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return {"id": set_id, "error": f"Access Denied: {response.status_code}"}
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        data = {
            "id": set_id,
            "market_value": "N/A",
            "retail_price": "N/A",
            "status": "Unknown",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # STRATEGY 1: Search the specific 'Price Analysis' table
        summary_table = soup.find('table', class_='table-sm')
        if summary_table:
            for row in summary_table.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) >= 2:
                    label = cells[0].get_text(strip=True)
                    val = cells[1].get_text(strip=True)
                    if "Market Value" in label: data["market_value"] = val
                    if "Retail Price" in label: data["retail_price"] = val
                    if "Status" in label: data["status"] = val

        # STRATEGY 2: If Table fails, look for specific 'ctl00_ContentPlaceHolder1_SetSummary_... labels
        if data["market_value"] == "N/A":
            mv_tag = soup.select_one("div.mb-2:-soup-contains('Market Value')")
            if mv_tag:
                data["market_value"] = mv_tag.get_text().replace("Market Value", "").strip()

        return data
    except Exception as e:
        return {"id": set_id, "error": str(e)}

if __name__ == "__main__":
    print("--- BRICKECONOMY TEST START ---")
    results = [get_brickeconomy_data(s) for s in TEST_SETS]
    
    # Save results to the 'test' directory (Production remains untouched)
    os.makedirs('test/results', exist_ok=True)
    with open('test/results/brickeconomy_test.json', 'w') as f:
        json.dump(results, f, indent=4)
    
    print("--- TEST COMPLETE. RESULTS SAVED TO test/results/brickeconomy_test.json ---")
