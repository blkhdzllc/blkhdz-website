import os
import requests
import base64
import urllib.parse

def get_ebay_access_token():
    app_id = os.environ.get('APP_ID')
    cert_id = os.environ.get('CERT_ID')
    if not app_id or not cert_id:
        return None
    credentials = f"{app_id}:{cert_id}"
    encoded = base64.b64encode(credentials.encode()).decode()
    url = "https://api.ebay.com/identity/v1/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded", "Authorization": f"Basic {encoded}"}
    data = {"grant_type": "client_credentials", "scope": "https://api.ebay.com/oauth/api_scope"}
    response = requests.post(url, headers=headers, data=data)
    return response.json().get('access_token') if response.status_code == 200 else None

def get_active_ebay_inventory():
    token = get_ebay_access_token()
    if not token: return []
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_US"
    }
    
    # We use "item" as a generic anchor word. 
    # The filter "sellers:{reedpb}" ensures we ONLY see your stuff.
    params = {
        "q": "item",
        "filter": "sellers:{reedpb},buyingOptions:{FIXED_PRICE|AUCTION}",
        "limit": "100"
    }
    
    print("Requesting inventory directly from store...")
    response = requests.get("https://api.ebay.com/buy/browse/v1/item_summary/search", headers=headers, params=params)
    
    if response.status_code != 200:
        print(f"API Error: {response.status_code} - {response.text}")
        return []
        
    items = response.json().get('itemSummaries', [])
    print(f"Successfully pulled {len(items)} items.")
    
    # Fetch descriptions
    for item in items:
        encoded_id = urllib.parse.quote(item.get('itemId'))
        resp = requests.get(f"https://api.ebay.com/buy/browse/v1/item/{encoded_id}", headers=headers)
        item['fullHtmlDescription'] = resp.json().get('description', '') if resp.status_code == 200 else ''
            
    return items
