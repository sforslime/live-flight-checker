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
    from .services.scrapers.arik_air import ArikAirScraper

    # Helper wrapper to run synchronous scrapers safely
    def run_scraper(scraper_cls, *args):
        try:
            scraper = scraper_cls()
            return scraper.scrape(*args)
        except Exception as e:
            print(f"Scraper Error ({scraper_cls.__name__}): {e}")
            return []

    # 1. Fetch from Amadeus (Async/Fast)
    amadeus = AmadeusClient()
    
    loop = asyncio.get_running_loop()
    
    # Create tasks
    # Task 1: Amadeus (API)
    task_amadeus = loop.run_in_executor(None, amadeus.search_flights, origin, destination, date)
    
    # Task 2: ValueJet (Scraper)
    task_valuejet = loop.run_in_executor(None, lambda: run_scraper(ValueJetScraper, origin, destination, date))
    
    # Task 3: XEJet (Scraper)
    task_xejet = loop.run_in_executor(None, lambda: run_scraper(XEJetScraper, origin, destination, date))

    # Task 4: Arik Air (Scraper)
    task_arik = loop.run_in_executor(None, lambda: run_scraper(ArikAirScraper, origin, destination, date))
    
    # Await all
    # return_exceptions=True means we get results even if one fails
    results_list = await asyncio.gather(task_amadeus, task_valuejet, task_xejet, task_arik, return_exceptions=True)
    
    final_results = []
    
    for res in results_list:
        if isinstance(res, list):
            final_results.extend(res)
        else:
            # It was an exception or error
            print(f"Search task failed: {res}")

    return final_results

