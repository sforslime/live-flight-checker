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
    date: str = Query(...),
    airlines: List[str] = Query(None)
):
    """
    Search endpoint that queries Amadeus and Airline Scrapers concurrently.
    Supports filtering by specific airlines.
    """
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    from .services.scrapers.valuejet import ValueJetScraper
    from .services.scrapers.xejet import XEJetScraper
    from .utils import get_airline_code

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

    # Filter Logic
    print(f"DEBUG: Received airlines filter: {airlines}")
    
    run_all = False
    if not airlines or "ALL" in airlines:
        run_all = True
    
    should_run_valuejet = run_all or "ValueJet" in airlines
    should_run_xejet = run_all or "XEJet" in airlines
    
    # Amadeus Codes
    amadeus_codes = []
    if not run_all:
        for airline in airlines:
            code = get_airline_code(airline)
            if code and airline not in ["ValueJet", "XEJet"]: # Exclude pure scrapers if they happen to have codes
                amadeus_codes.append(code)
    
    # If filtered but no valid codes found for Amadeus, and not running all, skip Amadeus?
    # No, user might have selected "Air Peace" (P4). 
    should_run_amadeus = run_all or len(amadeus_codes) > 0
    
    print(f"DEBUG: Execution Plan -> RunAll={run_all}, ValueJet={should_run_valuejet}, XEJet={should_run_xejet}, Amadeus={should_run_amadeus} (Codes: {amadeus_codes})")

    # 1. Fetch from Amadeus (Async/Fast)
    amadeus = AmadeusClient()
    
    loop = asyncio.get_running_loop()
    
    # Create tasks
    tasks = []
    
    # Task 1: Amadeus (API)
    if should_run_amadeus:
        # If run_all, pass None to search_flights to search everything. 
        # If filtered, pass the codes.
        codes_arg = amadeus_codes if not run_all else None
        tasks.append(loop.run_in_executor(None, amadeus.search_flights, origin, destination, date, codes_arg))
    
    # Run Scrapers Sequentially in background pool to prevent driver crashes
    # We will wrap them in a single async function or just list them
    
    scraper_results = []
    
    if should_run_valuejet:
        scraper_results.append(await loop.run_in_executor(None, lambda: run_scraper(ValueJetScraper, origin, destination, date)))
    
    if should_run_xejet:
        scraper_results.append(await loop.run_in_executor(None, lambda: run_scraper(XEJetScraper, origin, destination, date)))
        
    # Wait for Amadeus
    amadeus_results = []
    if tasks:
        # We only have one Amadeus task potentially
        res = await asyncio.gather(*tasks)
        amadeus_results = res[0]
    
    results_list = scraper_results + [amadeus_results]
    
    # Flatten results
    final_results = []
    for res in results_list:
        if isinstance(res, list):
            final_results.extend(res)
        else:
            # It was an exception or error
            print(f"Search task failed: {res}")

    return final_results

