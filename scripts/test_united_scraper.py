
import logging
from backend.services.scrapers.united_nigeria import UnitedNigeriaScraper

# Configure logging to see scraper output
logging.basicConfig(level=logging.INFO)

def test():
    scraper = UnitedNigeriaScraper()
    # Use a date far enough in advance
    flights = scraper.scrape("LOS", "ABV", "2026-01-20")
    print(f"Scraper returned {len(flights)} flights.")
    for f in flights:
        print(f" - {f}")

if __name__ == "__main__":
    test()
