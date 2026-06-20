import os
import requests

def get_active_ebay_inventory():
    """
    Fetches active inventory specifically for user 'reedpb' 
    using the eBay FindingService API.
    """
    app_id = os.environ.get('APP_ID')
    
    if not app_id:
        print("Error: APP_ID not set in environment.")
        return []
    
    url = "https://svcs.ebay.com/services/search/FindingService/v1"
    
    headers = {
        "X-EBAY-SOA-SECURITY-APPNAME": app_id,
        "X-EBAY-SOA-OPERATION-NAME": "findItemsAdvanced",
        "X-EBAY-SOA-RESPONSE-DATA-FORMAT": "JSON"
    }
    
    # Explicitly filter for your seller account to prevent incorrect data
    params = {
        "itemFilter(0).name": "Seller",
        "itemFilter(0).value": "reedpb",
        "paginationInput.entriesPerPage": "100"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            # Navigate the JSON structure returned by the Finding API
            search_result = data.get('findItemsAdvancedResponse', [{}])[0].get('searchResult', [{}])[0]
            items = search_result.get('item', [])
            return items
        else:
            print(f"API Error {response.status_code}: {response.text}")
            return []
            
    except Exception as e:
        print(f"Request failed: {e}")
        return []
