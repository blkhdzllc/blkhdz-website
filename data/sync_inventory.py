import os
import json

# This points to your new folder path
data_path = "data/test/inventory.json"
log_path = "data/test/sync_log.txt"

# Ensure the folder exists before writing
os.makedirs("data/test", exist_ok=True)

def sync():
    try:
        # For now, we create a test entry to see if it works
        test_data = {
            "store": "Blockheadz LLC",
            "status": "Online",
            "items": []
        }
        
        with open(data_path, "w") as f:
            json.dump(test_data, f, indent=4)
            
        with open(log_path, "a") as log:
            log.write("Sync successful: Created test data.\n")
            
    except Exception as e:
        with open(log_path, "a") as log:
            log.write(f"Error: {str(e)}\n")

if __name__ == "__main__":
    sync()
