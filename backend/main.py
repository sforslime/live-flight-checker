from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List
import os

from .services.amadeus_client import AmadeusClient
from .models import FlightOffer

app = FastAPI(title="Live Flight Checker")

# Mount static files (ensure directory exists)
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(frontend_path, "index.html"))

@app.get("/api/search", response_model=List[FlightOffer])
async def search_flights(
    origin: str = Query(..., min_length=3, max_length=3),
    destination: str = Query(..., min_length=3, max_length=3),
    date: str = Query(...)
):
    """
    Search endpoint that queries Amadeus and Airline Scrapers concurrently.
    """
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    from .services.scrapers.valuejet import ValueJetScraper
    from .services.scrapers.xejet import XEJetScraper

    # Helper wrapper to run synchronous scrapers safely
    def run_scraper(scraper_cls, *args):
        import time
        start = time.time()
        print(f"--- Starting {scraper_cls.__name__} ---")
        try:
            scraper = scraper_cls()
            results = scraper.scrape(*args)
            duration = time.time() - start
            print(f"--- Finished {scraper_cls.__name__} in {duration:.2f}s. Found {len(results)} flights. ---")
            return results
        except Exception as e:
            duration = time.time() - start
            print(f"!!! Scraper Error ({scraper_cls.__name__}) after {duration:.2f}s: {e}")
            import traceback
            traceback.print_exc()
            return []

    # 1. Fetch from Amadeus (Async/Fast)
    amadeus = AmadeusClient()
    
    loop = asyncio.get_running_loop()
    
    # Create tasks
    # Task 1: Amadeus (API) - Run this in background while we scrape
    task_amadeus = loop.run_in_executor(None, amadeus.search_flights, origin, destination, date)
    
    # Run Scrapers Sequentially to prevent driver crashes locally
    results_list = []
    
    # ValueJet
    results_list.append(await loop.run_in_executor(None, lambda: run_scraper(ValueJetScraper, origin, destination, date)))
    
    # XEJet 
    results_list.append(await loop.run_in_executor(None, lambda: run_scraper(XEJetScraper, origin, destination, date)))
    
    # Wait for Amadeus (should be done by now)
    amadeus_results = await task_amadeus
    results_list.append(amadeus_results)
    
    # Flatten results
    final_results = []
    for res in results_list:
        if isinstance(res, list):
            final_results.extend(res)
        else:
            # It was an exception or error
            print(f"Search task failed: {res}")

    return final_results

