import sys
import os
from datetime import datetime, timedelta

# Add the project root to the python path so we can import backend packages
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.amadeus_client import AmadeusClient

def test_api():
    client = AmadeusClient()
    
    if not client.client_id:
        print("Error: Credentials not found.")
        return

    print("--- Manual Flight Search Tool ---")
    origin = input("Enter Origin Code (e.g., LOS): ").upper().strip() or "LOS"
    destination = input("Enter Destination Code (e.g., ABV): ").upper().strip() or "ABV"
    
    # Default to tomorrow if no date provided
    default_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    date_input = input(f"Enter Date (YYYY-MM-DD) [default: {default_date}]: ").strip()
    departure_date = date_input if date_input else default_date

    print(f"\nSearching for flights from {origin} to {destination} on {departure_date}...")

    offers = client.search_flights(
        origin=origin,
        destination=destination,
        departure_date=departure_date
    )

    if not offers:
        print("No flights found or API error occurred.")
        return

    print(f"\nFound {len(offers)} flight offers:")
    print("-" * 60)
    for offer in offers:
        print(f"Airline: {offer.airline} | Flight: {offer.flight_number}")
        print(f"Time: {offer.departure_time.strftime('%H:%M')} - {offer.arrival_time.strftime('%H:%M')}")
        print(f"Price: {offer.currency} {offer.price:,.2f}")
        print("-" * 60)


if __name__ == "__main__":
    test_api()
