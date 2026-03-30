import requests
from bs4 import BeautifulSoup
import json
import datetime
import os

# Target Sets for Triangulation
TEST_SETS = ["75274", "31167", "71738"]

def get_brickeconomy_data(set_id):
    url = f"https://www.brickeconomy.com/set/{set_id}-1/"
    # Mimic a modern browser to avoid being blocked as a bot
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

        # Targeted logic: Search the specific summary table cells
        rows = soup.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 2:
                label = cells[0].get_text(strip=True)
                val = cells[1].get_text(strip=True)
                if "Market Value" in label:
                    data["market_value"] = val
                elif "Retail Price" in label:
                    data["retail_price"] = val

        # Targeted logic: Find the availability status badge
        status_tag = soup.find('span', class_='badge')
        if status_tag:
            # Filters out numeric codes and looks for actual status words
            text = status_tag.get_text(strip=True)
            if any(word in text for word in ['Retired', 'Available', 'Soon']):
                data["status"] = text

        return data
    except Exception as e:
        return {"id": set_id, "error": str(e)}

if __name__ == "__main__":
    print("--- BRICKECONOMY TEST START ---")
    new_results = [get_brickeconomy_data(s) for s in TEST_SETS]
    
    # NPW: Logic to APPEND to a history file instead of overwriting
    os.makedirs('test/results', exist_ok=True)
    history_file = 'test/results/brickeconomy_history.json'
    
    history = []
    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            try:
                history = json.load(f)
            except:
                history = []
    
    history.append({
        "run_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data": new_results
    })
    
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=4)
    
    print(f"--- TEST COMPLETE. DATA APPENDED TO {history_file} ---")
