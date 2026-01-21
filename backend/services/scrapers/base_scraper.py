import abc
import time
import random
import logging
from typing import List, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from backend.models import FlightOffer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseScraper(abc.ABC):
    """
    Abstract base class for airline scrapers.
    Handles driver initialization, user-agent rotation, and standardized delays.
    """
    
    USER_AGENTS = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0"
    ]

    def __init__(self, airline_name: str):
        self.airline_name = airline_name
        self.driver: Optional[webdriver.Chrome] = None

    def _setup_driver(self):
        """Initializes a headless Chrome driver with random User-Agent."""
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")  # Run in background
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # User Agent Rotation
        user_agent = random.choice(self.USER_AGENTS)
        chrome_options.add_argument(f"user-agent={user_agent}")
        chrome_options.page_load_strategy = 'eager'
        logger.info(f"[{self.airline_name}] Initializing driver with UA: {user_agent}")

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def _random_delay(self, min_seconds: float = 2.0, max_seconds: float = 5.0):
        """Sleeps for a random interval to mimic human behavior."""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)

    def quit(self):
        """Safely closes the driver."""
        if self.driver:
            self.driver.quit()
            self.driver = None

    @abc.abstractmethod
    def scrape(self, origin: str, destination: str, date: str) -> List[FlightOffer]:
        """
        Main scraping method to be implemented by child classes.
        Returns a list of FlightOffer objects.
        """
        pass
