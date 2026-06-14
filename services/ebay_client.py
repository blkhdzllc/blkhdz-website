import os
import requests
import base64

def get_ebay_access_token():
    """Generates an OAuth token using App ID and Cert ID from GitHub secrets."""
    app_id = os.environ.get('APP_ID')
    cert_id = os.environ.get('CERT_ID')
    
    if not app_id or not cert_id:
        print("Error: APP_ID or CERT_ID not set in environment.")
        return None

    credentials = f"{app_id}:{cert_id}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    url = "https://api.ebay.com/identity/v1/oauth2/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {encoded_credentials}"
    }
    data = {
        "grant_type": "client_credentials", 
        "scope": "https://api.ebay.com/oauth/api_scope"
    }
    
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        print(f"Token Error {response.status_code}: {response.text}")
        return None

def get_active_ebay_inventory():
    """Fetches all active listings for your specific eBay store (reedpb)."""
    token = get_ebay_access_token()
    if not token:
        return []

    url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_US"
    }
    
    # Filter by your store username AND include all buying options (Fixed Price + Auction)
    params = {
        "filter": "sellers:{reedpb},buyingOptions:{FIXED_PRICE|AUCTION}",
        "limit": "100"
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get('itemSummaries', [])
    else:
        print(f"API Error {response.status_code}: {response.text}")
        return []
