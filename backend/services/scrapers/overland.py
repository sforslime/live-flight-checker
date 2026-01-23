
import time
import logging
from typing import List
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

from backend.services.scrapers.base_scraper import BaseScraper
from backend.models import FlightOffer

logger = logging.getLogger(__name__)

class OverlandScraper(BaseScraper):
    """
    Scraper for Overland Airways.
    Interacts with the specific dropdowns and date picker as described by the user.
    """
    def __init__(self):
        super().__init__("Overland Airways")
        self.base_url = "https://www.overlandairways.com/"
        
    def scrape(self, origin: str, destination: str, date: str) -> List[FlightOffer]:
        self._setup_driver()
        self.search_params = {
            'origin': origin,
            'destination': destination,
            'date': date
        }
        flights = []
        
        try:
            logger.info(f"[{self.airline_name}] Navigating to: {self.base_url}")
            self.driver.get(self.base_url)
            
            # Wait for page load and any initial overlay
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "main")) 
            )
            self._wait_for_spinner()

            # 1. Select Origin
            logger.info(f"[{self.airline_name}] Selecting Origin: {origin}")
            self._select_dropdown_by_typing("flightFrom", origin)
            
            # 2. Select Destination
            logger.info(f"[{self.airline_name}] Selecting Destination: {destination}")
            self._select_dropdown_by_typing("flightTo", destination)
            
            # 3. Select One Way
            logger.info(f"[{self.airline_name}] Selecting 'One Way'")
            try:
                # Based on HTML: <select><option value="OW">One-way</option>...</select>
                trip_type_select = Select(self.driver.find_element(By.XPATH, "//select[./option[@value='OW']]"))
                trip_type_select.select_by_value("OW")
            except Exception as e:
                logger.warning(f"[{self.airline_name}] Could not select 'One Way': {e}")

            self._wait_for_spinner()
            
            # 4. Select Date
            self._select_date(date)
            
            # 5. Click Search
            logger.info(f"[{self.airline_name}] Snapshotting before search...")
            try:
                self.driver.save_screenshot("overland_filled_form.png")
                with open("overland_filled_form.html", "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
            except:
                pass

            logger.info(f"[{self.airline_name}] Clicking Search")
            # id="avl" contains the submit input
            search_btn = self.driver.find_element(By.CSS_SELECTOR, "#avl input[type='submit']")
            # Use JS click to avoid intersection issues
            self.driver.execute_script("arguments[0].click();", search_btn)
            
            # 6. Wait for Results
            logger.info(f"[{self.airline_name}] Waiting for results...")
            WebDriverWait(self.driver, 45).until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, ".flight-result-row, .flight-row, #flightResults, .avail-table")) > 0 or "No flight found" in d.page_source
            )
            
            logger.info(f"[{self.airline_name}] Snapshotting results page...")
            try:
                self.driver.save_screenshot("overland_results.png")
                with open("overland_results.html", "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
            except:
                pass
            
            # 7. Parse Results
            flights = self._parse_results()
            
        except Exception as e:
            logger.error(f"[{self.airline_name}] Scraping failed: {e}")
            if self.driver:
                self.driver.save_screenshot(f"{self.airline_name.lower()}_error.png")
                with open(f"{self.airline_name.lower()}_error.html", "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
        finally:
            self.quit()
            
        return flights

    def _wait_for_spinner(self):
        """Waits for any loading spinner to disappear."""
        try:
            # HTML has <div id="overlay1" class="loader">
            WebDriverWait(self.driver, 2).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "#overlay1, .loader"))
            )
            WebDriverWait(self.driver, 20).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, "#overlay1, .loader"))
            )
        except Exception:
            pass
        finally:
            time.sleep(1)

    def _select_dropdown_by_typing(self, element_id: str, text: str):
        # User Interaction: Click -> Type -> Click Option
        
        inp = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, element_id))
        )
        
        logger.info(f"[{self.airline_name}] Clicking input {element_id}")
        inp.click()
        time.sleep(0.5)
        
        logger.info(f"[{self.airline_name}] Sending keys {text}")
        inp.send_keys(text)
        
        # Trigger explicit click again in case 'onclick' is required to show dropdown
        inp.click()
        
        time.sleep(3.0) # Increased wait for dropdown
        
        # Click the first visible option in the specific container
        container_id = f"eac-container-{element_id}"
        
        try:
            # Wait for container visibility
            logger.info(f"[{self.airline_name}] Waiting for container {container_id}")
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.ID, container_id))
            )
            
            # Find options - verify we are clicking the clickable element
            # Structure: li > div.eac-item
            options = self.driver.find_elements(By.XPATH, f"//div[@id='{container_id}']//li//div[contains(@class, 'eac-item')]")
            logger.info(f"[{self.airline_name}] Found {len(options)} options for {text}")
            
            target_option = None
            for opt in options:
                if text.lower() in opt.text.lower():
                    target_option = opt
                    break
            
            if target_option:
                logger.info(f"[{self.airline_name}] Clicking option: {target_option.text}")
                # Try regular click first
                try:
                    target_option.click()
                except:
                     self.driver.execute_script("arguments[0].click();", target_option)
            else:
                logger.warning(f"[{self.airline_name}] No matching option found for {text}")
                # Fallback to Enter
                inp.send_keys(Keys.ENTER)

        except Exception as e:
            logger.warning(f"[{self.airline_name}] Error selecting option for {text}: {e}")
            inp.send_keys(Keys.ENTER)
            
        self._wait_for_spinner()

    def _select_date(self, date_str: str):
        logger.info(f"[{self.airline_name}] Selecting Date: {date_str}")
        try:
            # Convert YYYY-MM-DD to DD/MM/YYYY (DMY format as per HTML data-dateformat)
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%d/%m/%Y")
            
            # Method 4: jQuery Datepicker setDate (Silver Bullet for jQuery UI)
            # This triggers all internal events and validations
            try:
                date_str_formatted = date_obj.strftime("%d/%m/%Y")
                logger.info(f"[{self.airline_name}] Setting date via jQuery: {date_str_formatted}")
                # Set both main and mobile inputs
                self.driver.execute_script(f"$('#flightDepart').datepicker('setDate', '{date_str_formatted}');")
                self.driver.execute_script(f"$('#flightDepart_mobile').val('{date_str_formatted}');")
                
                # Trigger events
                self.driver.execute_script("document.getElementById('flightDepart').dispatchEvent(new Event('change', { bubbles: true }));")
                self.driver.execute_script("document.getElementById('flightDepart').dispatchEvent(new Event('blur', { bubbles: true }));")
            except Exception as e:
                logger.warning(f"[{self.airline_name}] jQuery setDate failed: {e}")
                # Fallback to UI click
                self.driver.find_element(By.ID, "flightDepart").click()
                day = date_obj.day
                day_xpath = f"//a[contains(@class, 'ui-state-default') and text()='{day}']"
                WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, day_xpath))).click()
            
        except Exception as e:
            logger.error(f"[{self.airline_name}] Failed to select date: {e}")
            
        self._wait_for_spinner()

    def _parse_results(self) -> List[FlightOffer]:
        flights = []
        try:
            # Check for "No Flight Found" or "Sold Out" popup
            if "No flight found" in self.driver.page_source or "SOLD OUT" in self.driver.page_source:
                logger.info(f"[{self.airline_name}] No flights found or sold out.")
                return []
                
            rows = self.driver.find_elements(By.CSS_SELECTOR, ".flight-result-row, .flight-row, #flightResults, .avail-table")
            for row in rows:
                # Extract details (Placeholder)
                pass
        except Exception:
            pass
            
        if not flights:
             with open("overland_debug.html", "w", encoding="utf-8") as f:
                 f.write(self.driver.page_source)
                 
        return flights
