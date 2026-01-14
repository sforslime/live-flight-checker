import sys
import os
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.scrapers.ibom_air import IbomAirScraper

def test_scraper():
    scraper = IbomAirScraper()
    
    # Search for tomorrow
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    print(f"Testing Ibom Air Scraper for LOS -> ABV on {tomorrow}")
    scraper.scrape("LOS", "ABV", tomorrow)
    print("Test complete. Check ibom_results.html")

if __name__ == "__main__":
    test_scraper()
