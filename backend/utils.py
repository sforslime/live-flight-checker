AIRLINE_CODES = {
    "P4": "Air Peace",
    "W3": "Arik Air",
    "QI": "Ibom Air",
    "OF": "Overland Airways",
    "VJ": "ValueJet",
    "9J": "Dana Air",
    "U5": "United Nigeria"
}

REVERSE_AIRLINE_CODES = {v: k for k, v in AIRLINE_CODES.items()}
# Add manual overrides or aliases if needed
REVERSE_AIRLINE_CODES ["Overland"] = "OF" # Alias

def get_airline_name(code: str) -> str:
    """Returns the airline name for a given IATA code, or the code itself if not found."""
    return AIRLINE_CODES.get(code, code)

def get_airline_code(name: str) -> str:
    """Returns the IATA code for a given airline name."""
    return REVERSE_AIRLINE_CODES.get(name)
