import os
import json

# Since the script is already IN the data folder, 
# it just needs to look for the 'test' folder next to it.
data_path = "test/inventory.json"
log_path = "test/test/sync_log.txt"

# This ensures the 'test' folder exists
os.makedirs("test", exist_ok=True)

def sync():
    try:
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
        # If it fails, it will print the error to the GitHub console
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    sync()
