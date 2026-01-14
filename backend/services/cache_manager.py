import time
from typing import Optional, Any, Dict

class CacheManager:
    """
    Simple in-memory cache with TTL (Time To Live).
    """
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        """Retrieve a value if it exists and hasn't expired."""
        if key in self._cache:
            entry = self._cache[key]
            if entry['expiry'] > time.time():
                return entry['value']
            else:
                del self._cache[key] # Expired
        return None

    def set(self, key: str, value: Any, ttl_minutes: int = 30):
        """Store a value with a TTL in minutes."""
        expiry_time = time.time() + (ttl_minutes * 60)
        self._cache[key] = {
            'value': value,
            'expiry': expiry_time
        }
        
    def clear(self):
        self._cache = {}

# Global instance
flight_cache = CacheManager()
