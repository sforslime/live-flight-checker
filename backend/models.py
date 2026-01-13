from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class FlightOffer(BaseModel):
    source: str  # 'Amadeus', 'Air Peace', etc.
    airline: str
    flight_number: str
    origin: str
    destination: str
    departure_time: datetime
    arrival_time: datetime
    price: float
    currency: str
    booking_link: Optional[str] = None
