"""
Test script for ValueJet scraper.
"""
import logging
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)

# Add project root to path
sys.path.insert(0, '/Users/slime./Desktop/Projects/live-flight-checker')

from backend.services.scrapers.valuejet import ValueJetScraper

def main():
    scraper = ValueJetScraper()
    
    # Test search: Lagos (LOS) to Abuja (ABV)
    origin = "LOS"
    destination = "ABV"
    date = "2026-01-21"  # A few days in the future
    
    print(f"Searching ValueJet: {origin} -> {destination} on {date}")
    
    flights = scraper.scrape(origin, destination, date)
    
    print(f"\nFound {len(flights)} flights:")
    for f in flights:
        print(f"  - {f}")

if __name__ == "__main__":
    main()
