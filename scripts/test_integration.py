
import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.amadeus_client import AmadeusClient
from backend.services.scrapers.valuejet import ValueJetScraper

async def test_search():
    origin = "LOS"
    destination = "ABV"
    date = "2026-01-20"
    
    print(f"Testing search for {origin} -> {destination} on {date}")
    
    def run_scraper(scraper_cls, *args):
        try:
            scraper = scraper_cls()
            print(f"Starting {scraper_cls.__name__}...")
            res = scraper.scrape(*args)
            print(f"Finished {scraper_cls.__name__} with {len(res)} results")
            return res
        except Exception as e:
            print(f"Scraper Error ({scraper_cls.__name__}): {e}")
            return []

    amadeus = AmadeusClient()
    loop = asyncio.get_running_loop()
    
    print("Launching tasks...")
    task_amadeus = loop.run_in_executor(None, amadeus.search_flights, origin, destination, date)
    task_valuejet = loop.run_in_executor(None, lambda: run_scraper(ValueJetScraper, origin, destination, date))
    
    results_list = await asyncio.gather(task_amadeus, task_valuejet, return_exceptions=True)
    
    final_results = []
    for res in results_list:
        if isinstance(res, list):
            final_results.extend(res)
        else:
            print(f"Task failed: {res}")
            
    print("\n--- Final Results ---")
    print(f"Total flights found: {len(final_results)}")
    for flight in final_results:
        print(f"- {flight.airline} ({flight.source}): {flight.price} {flight.currency}")

if __name__ == "__main__":
    asyncio.run(test_search())
