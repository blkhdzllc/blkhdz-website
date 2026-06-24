import os
import requests
import base64

def get_ebay_access_token():
    app_id = os.environ.get('APP_ID')
    cert_id = os.environ.get('CERT_ID')
    
    if not app_id or not cert_id:
        return None

    credentials = f"{app_id}:{cert_id}"
    encoded = base64.b64encode(credentials.encode()).decode()
    
    url = "https://api.ebay.com/identity/v1/oauth2/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {encoded}"
    }
    data = {
        "grant_type": "client_credentials", 
        "scope": "https://api.ebay.com/oauth/api_scope"
    }
    
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json().get('access_token')
    return None

def get_active_ebay_inventory():
    token = get_ebay_access_token()
    if not token:
        return []

    headers = {
        "Authorization": f"Bearer {token}",
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
        "X-EBAY-C-ENDUSERCTX": "affiliateCampaignId=5339141674"
    }
    
    params = {
        "q": " ", # A blank space acts as a wildcard to stop filtering out items
        "filter": "sellers:{reedpb},buyingOptions:{FIXED_PRICE|AUCTION}",
        "limit": "100"
    }
    
    response = requests.get("https://api.ebay.com/buy/browse/v1/item_summary/search", headers=headers, params=params)
    
    if response.status_code != 200:
        return []
        
    return response.json().get('itemSummaries', [])
