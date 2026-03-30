import requests
from bs4 import BeautifulSoup
import json
import datetime
import os

# Sets to test
TEST_SETS = ["75274", "31167", "71738"]

def get_brickeconomy_data(set_id):
    # BrickEconomy URL structure
    url = f"https://www.brickeconomy.com/set/{set_id}-1/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return {"id": set_id, "error": f"Status {response.status_code}"}
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        data = {
            "id": set_id,
            "market_value": "N/A",
            "retail_price": "N/A",
            "status": "Unknown",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Targeted scraping logic for BrickEconomy's data points
        for row in soup.find_all('div', class_='row mb-2'):
            text = row.get_text()
            if "Market Value" in text:
                data["market_value"] = text.replace("Market Value", "").strip()
            if "Retail Price" in text:
                data["retail_price"] = text.replace("Retail Price", "").strip()

        status_box = soup.find('span', class_='badge')
        if status_box:
            data["status"] = status_box.get_text().strip()

        return data
    except Exception as e:
        return {"id": set_id, "error": str(e)}

if __name__ == "__main__":
    print(f"--- BRICKECONOMY TEST START ---")
    results = []
    
    for s in TEST_SETS:
        print(f"Fetching: Set {s}")
        results.append(get_brickeconomy_data(s))
    
    # NPW: Save results ONLY to the tests/results folder
    os.makedirs('tests/results', exist_ok=True)
    with open('tests/results/brickeconomy_test.json', 'w') as f:
        json.dump(results, f, indent=4)
    
    print(f"--- TEST COMPLETE. RESULTS IN tests/results/brickeconomy_test.json ---")
