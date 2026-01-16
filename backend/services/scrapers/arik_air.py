
import time
import logging
from typing import List
from datetime import datetime
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from backend.services.scrapers.base_scraper import BaseScraper
from backend.models import FlightOffer

logger = logging.getLogger(__name__)

class ArikAirScraper(BaseScraper):
    """
    Scraper for Arik Air using undetected-chromedriver to bypass Cloudflare
    """
    def __init__(self):
        super().__init__("ArikAir")
        self.base_url = "https://www.arikair.com/"
        
    def _setup_driver(self):
        """Override base driver setup to use undetected-chromedriver"""
        options = uc.ChromeOptions()
        options.add_argument("--headless=new") # Comment this out to run headful (helps with Cloudflare bypass)
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        
        # UC manages the driver binary automatically
        self.driver = uc.Chrome(options=options, use_subprocess=True)
        self.driver.set_page_load_timeout(60)
        
    def scrape(self, origin: str, destination: str, date: str) -> List[FlightOffer]:
        self._setup_driver()
        self.search_params = {
            "origin": origin,
            "destination": destination,
            "date": date
        }
        
        try:
            # Construct URL for direct access
            # Format date: YYYY-MM-DD -> DD.MM.YYYY
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            date_formatted = date_obj.strftime("%d.%m.%Y")
            
            # Base URL for the booking engine (found from investigation)
            base_ibe_url = "https://arikair.crane.aero/ibe/availability"
            
            params = [
                "tripType=ONE_WAY",
                f"depPort={origin}",
                f"arrPort={destination}",
                f"departureDate={date_formatted}",
                "adult=1",
                "child=0",
                "infant=0",
                "currency=NGN",
                "cabinClass=ECONOMY",
                "lang=EN"
            ]
            full_url = f"{base_ibe_url}?{'&'.join(params)}"
            
            logger.info(f"[{self.airline_name}] Navigating directly to: {full_url}")
            self.driver.get(full_url)
            
            # 7. Wait for Results
            logger.info(f"[{self.airline_name}] Waiting for results...")
            
            try:
                # Wait for flight list or at least the body to load
                 WebDriverWait(self.driver, 60).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                 # Give it time to render JS
                 time.sleep(10)
                 
            except Exception as e:
                # Check for Cloudflare title
                if "Cloudflare" in self.driver.title or "Access denied" in self.driver.title:
                    logger.error(f"[{self.airline_name}] BLOCKED BY CLOUDFLARE.")
                raise e
            
            # 8. Parse Results
            flights = self._parse_results()
            return flights
            
        except Exception as e:
            logger.error(f"[{self.airline_name}] Scraping failed: {e}")
            if self.driver:
                self.driver.save_screenshot(f"{self.airline_name.lower()}_error.png")
                with open(f"{self.airline_name.lower()}_error.html", "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
            return []
        finally:
            if self.driver:
                self.driver.quit()
    def _set_date(self, date_str: str):
        # Implementation for clicking datepicker
        # Similar to XEJet/ValueJet: Click input -> Find Day
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d")
            day = target_date.day
            
            date_input = self.driver.find_element(By.ID, "departureDate")
            date_input.click()
            
            # Wait for calendar (jQuery UI or Bootstrap Datepicker)
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".datepicker, .ui-datepicker"))
            )
            
            # Simple day selection (assuming current month for now to test)
            # We locate the day cell. Usually <td> or <a> with the text of the day
            day_elems = self.driver.find_elements(By.XPATH, f"//td[not(contains(@class, 'disabled')) and text()='{day}']")
            if not day_elems:
                 day_elems = self.driver.find_elements(By.XPATH, f"//a[contains(@class, 'ui-state-default') and text()='{day}']")
            
            if day_elems:
                day_elems[0].click()
                logger.info(f"[{self.airline_name}] Selected day: {day}")
            else:
                logger.warning(f"[{self.airline_name}] Could not find day element for {day}")
                
        except Exception as e:
            logger.warning(f"[{self.airline_name}] Date setting failed: {e}")

    def _parse_results(self) -> List[FlightOffer]:
        flights = []
        # Save HTML for inspection since we don't know the structure yet
        with open("arik_results.html", "w", encoding="utf-8") as f:
            f.write(self.driver.page_source)
        return flights
