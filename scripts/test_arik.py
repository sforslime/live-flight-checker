
import logging
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.scrapers.arik_air import ArikAirScraper

# Setup logging
logging.basicConfig(level=logging.INFO)

def main():
    print("Initializing Arik Air Scraper...")
    scraper = ArikAirScraper()
    
    # Use a date slightly deep in future to ensure flights
    results = scraper.scrape("LOS", "ABV", "2026-01-20")
    
    print(f"\nFound {len(results)} flights.")
    print("Check arik_results.html for the page structure.")

if __name__ == "__main__":
    main()
