import time
import logging
from typing import List
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from backend.services.scrapers.base_scraper import BaseScraper
from backend.models import FlightOffer

logger = logging.getLogger(__name__)

class IbomAirScraper(BaseScraper):
    def __init__(self):
        super().__init__("Ibom Air")
        self.base_url = "https://www.ibomair.com"

    def scrape(self, origin: str, destination: str, date: str) -> List[FlightOffer]:
        """
        Scrapes Ibom Air flights via Homepage Interaction.
        """
        self._setup_driver()
        offers = []

        try:
            # Transform date to dd.MM.yyyy for Ibom's format
            dt = datetime.strptime(date, "%Y-%m-%d")
            formatted_date = dt.strftime("%d.%m.%Y")
            
            logger.info(f"[{self.airline_name}] Navigating to homepage: {self.base_url}")
            self.driver.get(self.base_url)
            
            # 1. Handle Origin (Select2 Interaction)
            logger.info(f"[{self.airline_name}] Selecting Origin: {origin}")
            # Click the Select2 container for depPort
            # The container usually follows the select element. We use the aria-labelledby which matches standard Select2
            dep_container = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "span[aria-labelledby='select2-depPort-container']"))
            )
            dep_container.click()
            
            # Type into the search field (which appears in the dropdown)
            search_field = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "select2-search__field"))
            )
            search_field.send_keys(origin)
            time.sleep(0.5) # Wait for filter
            search_field.send_keys(Keys.ENTER)
            time.sleep(0.5)

            # 2. Handle Destination
            logger.info(f"[{self.airline_name}] Selecting Destination: {destination}")
            arr_container = self.driver.find_element(By.CSS_SELECTOR, "span[aria-labelledby='select2-arrPort-container']")
            arr_container.click()
            
            # Search field should be visible again (it's often the same element reused or a new one in the DOM)
            search_field = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "select2-search__field"))
            )
            search_field.send_keys(destination)
            time.sleep(0.5)
            search_field.send_keys(Keys.ENTER)
            time.sleep(0.5)

            # 3. Handle Date
            # Try human-like interaction first
            date_input = self.driver.find_element(By.ID, "departureDate")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", date_input)
            time.sleep(0.5)
            date_input.click()
            date_input.clear()
            date_input.send_keys(formatted_date)
            # Ensure the value stuck
            logger.info(f"[{self.airline_name}] Date Input Value: {date_input.get_attribute('value')}")

            # 4. Handle Passengers (Direct Injection)
            try:
                self.driver.execute_script("document.getElementsByName('adult')[0].value = '1';")
                logger.info(f"[{self.airline_name}] Injected adult count = 1")
            except Exception as e:
                logger.warning(f"[{self.airline_name}] Failed to inject adult count: {e}")

            # 5. Click Search (Standard interaction, anticipating JS injection fixed validation)
            logger.info(f"[{self.airline_name}] Clicking search button...")
            search_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "search"))
            )
            # Scroll to view
            self.driver.execute_script("arguments[0].scrollIntoView(true);", search_btn)
            time.sleep(1) # Visual pause
            search_btn.click()

            # 6. Wait for Results
            logger.info(f"[{self.airline_name}] Waiting for results...")
            time.sleep(15) # Initial wait for redirection
            logger.info(f"[{self.airline_name}] Current URL after wait: {self.driver.current_url}")
            
            # Save results again for analysis
            with open("ibom_results_interaction.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            logger.info(f"[{self.airline_name}] Saved result page to ibom_results_interaction.html")

            # TODO: Parsing Logic (to be added after inspecting ibom_results_interaction.html)
            
        except Exception as e:
            logger.error(f"[{self.airline_name}] Scraping failed: {e}")
            # Save screenshot on failure
            if self.driver:
                self.driver.save_screenshot("ibom_error.png")
        finally:
            self.quit()
        
        return offers
