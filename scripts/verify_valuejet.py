import logging
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.scrapers.valuejet import ValueJetScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)

def test_valuejet():
    scraper = ValueJetScraper()
    # Use a realistic route and future date
    origin = "LOS" # Lagos
    destination = "ABV" # Abuja
    date = "2026-02-01" # Future date relative to assumed current time (Mocked time is 2026-01-23)
    
    print(f"Testing ValueJet Scraper: {origin} -> {destination} on {date}")
    try:
        results = scraper.scrape(origin, destination, date)
        
        print(f"\nResults found: {len(results)}")
        for flight in results:
            print(f"- {flight.airline} {flight.flight_number}: {flight.departure_time} -> {flight.arrival_time} | {flight.currency} {flight.price}")
            
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
    test_valuejet()
