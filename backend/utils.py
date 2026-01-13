AIRLINE_CODES = {
    "P4": "Air Peace",
    "W3": "Arik Air",
    "QI": "Ibom Air",
    "OF": "Overland Airways",
    "VJ": "ValueJet",
    "U5": "United Nigeria Airlines",
    "Q9": "Green Africa Airways"
}

def get_airline_name(code: str) -> str:
    """Returns the airline name for a given IATA code, or the code itself if not found."""
    return AIRLINE_CODES.get(code, code)
