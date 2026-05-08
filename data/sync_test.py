import os
import json
import requests
import base64

# --- SETTINGS ---
# ... rest of your code ...# --- SETTINGS ---
EPN_CAMPAIGN_ID = "5339141674" 
SELLER_ID = "reedpb"

# NPW Fix: This logic detects if the script is in 'data' or the root
# and ensures it ALWAYS saves to the correct 'data/test' location.
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SANDBOX_DIR = os.path.join(base_dir, "data", "test")

os.makedirs(SANDBOX_DIR, exist_ok=True)
