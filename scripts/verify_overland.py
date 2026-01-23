
import logging
from backend.services.scrapers.overland import OverlandScraper

# Setup logging
logging.basicConfig(level=logging.INFO)

def test_overland():
    scraper = OverlandScraper()
    # Use a realistic route and future date
    origin = "Abuja"
    destination = "Lagos" 
    date = "2026-01-25" # Future date relative to assumed current time (Mocked time is 2026)
    
    print(f"Testing Overland Scraper: {origin} -> {destination} on {date}")
    results = scraper.scrape(origin, destination, date)
    
    print("Results found:", len(results))
    for flight in results:
        print(flight)

if __name__ == "__main__":
    test_overland()
