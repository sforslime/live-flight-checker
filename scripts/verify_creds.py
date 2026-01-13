import sys
import os
from datetime import datetime, timedelta

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.amadeus_client import AmadeusClient

def verify():
    print("Initializing Client...")
    # Force reload of environment variables might be needed if this was a long running process, 
    # but for a fresh script run, it will load from .env on disk.
    client = AmadeusClient()
    
    if not client.client_id or not client.client_secret:
        print("FAIL: Credentials are missing from .env")
        return

    print(f"Client ID present: {client.client_id[:4]}...")
    
    # Search for flights tomorrow
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    print(f"Testing search: LOS -> ABV on {tomorrow}")

    try:
        offers = client.search_flights('LOS', 'ABV', tomorrow)
        if offers:
            print(f"SUCCESS: Found {len(offers)} offers.")
            print(f"Sample price: {offers[0].currency} {offers[0].price}")
        else:
            print("WARNING: API call succeeded but returned 0 results.")
    except Exception as e:
        print(f"ERROR: API call failed. Details: {e}")

if __name__ == "__main__":
    verify()
