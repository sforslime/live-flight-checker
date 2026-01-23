from amadeus import Client, ResponseError
from datetime import datetime
import os
from dotenv import load_dotenv
from ..models import FlightOffer
from ..utils import get_airline_name

load_dotenv()

class AmadeusClient:
    def __init__(self):
        self.client_id = os.getenv("AMADEUS_CLIENT_ID")
        self.client_secret = os.getenv("AMADEUS_CLIENT_SECRET")
        
        if not self.client_id or not self.client_secret:
            print("Warning: Amadeus credentials not found in environment variables.")
            self.amadeus = None
        else:
            self.amadeus = Client(
                client_id=self.client_id,
                client_secret=self.client_secret
            )

    def search_flights(self, origin: str, destination: str, departure_date: str, included_airlines: list = None):
        """
        Search for flights using Amadeus Flight Offers Search API.
        departure_date format: YYYY-MM-DD
        included_airlines: List of IATA codes to filter by.
        """
        if not self.amadeus:
            return []

        try:
            kwargs = {
                'originLocationCode': origin,
                'destinationLocationCode': destination,
                'departureDate': departure_date,
                'adults': 1,
                'currencyCode': 'NGN'
            }
            
            if included_airlines:
                kwargs['includedAirlineCodes'] = ",".join(included_airlines)

            response = self.amadeus.shopping.flight_offers_search.get(**kwargs)
            
            flight_offers = []
            for offer in response.data:
                # Basic parsing logic - can be expanded
                itineraries = offer['itineraries'][0]['segments']
                first_segment = itineraries[0]
                last_segment = itineraries[-1]
                
                # Carrier code (e.g. 'P4' for Air Peace if available, or others)
                carrier_code = first_segment['carrierCode']
                airline_name = get_airline_name(carrier_code)
                
                price_amount = float(offer['price']['total'])
                currency = offer['price']['currency']
                
                dt_format = "%Y-%m-%dT%H:%M:%S"
                dept_time = datetime.strptime(first_segment['departure']['at'], dt_format)
                arr_time = datetime.strptime(last_segment['arrival']['at'], dt_format)

                flight_offers.append(FlightOffer(
                    source='Amadeus',
                    airline=airline_name, 
                    flight_number=f"{carrier_code}{first_segment['number']}",
                    origin=origin,
                    destination=destination,
                    departure_time=dept_time,
                    arrival_time=arr_time,
                    price=price_amount,
                    currency=currency,
                    booking_link=None # API generally doesn't give direct deep links easily without more work
                ))
            
            return flight_offers

        except ResponseError as error:
            print(f"Amadeus API Error: {error}")
            return []
