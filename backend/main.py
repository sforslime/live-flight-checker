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
    Search endpoint that currently queries Amadeus.
    Will be updated to include scrapers.
    """
    # Initialize Clients
    amadeus = AmadeusClient()
    
    # 1. Fetch from Amadeus
    results = amadeus.search_flights(origin, destination, date)
    
    # 2. Future: Fetch from scrapers (Air Peace, Ibom, etc.) and extend 'results'
    
    return results

