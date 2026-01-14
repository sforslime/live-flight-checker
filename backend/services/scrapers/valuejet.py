"""
ValueJet Scraper - Web scraper for https://www.flyvaluejet.com
"""
import logging
import time
from typing import List
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from backend.services.scrapers.base_scraper import BaseScraper
from backend.models import FlightOffer

logger = logging.getLogger(__name__)


class ValueJetScraper(BaseScraper):
    """Scraper for ValueJet flights."""
    
    def __init__(self):
        super().__init__("ValueJet")
        self.base_url = "https://www.flyvaluejet.com"
    
    def scrape(self, origin: str, destination: str, date: str) -> List[FlightOffer]:
        """
        Scrape ValueJet for flights.
        
        Args:
            origin: Origin airport code (e.g., 'LOS' for Lagos)
            destination: Destination airport code (e.g., 'ABV' for Abuja)
            date: Travel date in YYYY-MM-DD format
            
        Returns:
            List of FlightOffer objects
        """
        flights = []
        
        try:
            self.search_params = {
                'origin': origin,
                'destination': destination,
                'date': date
            }
            self._setup_driver()
            logger.info(f"[{self.airline_name}] Navigating to homepage: {self.base_url}")
            self.driver.get(self.base_url)
            
            # Wait for page to fully hydrate (Next.js React app)
            logger.info(f"[{self.airline_name}] Waiting for page hydration...")
            time.sleep(5)
            
            # 1. Wait for dropdown options to load
            logger.info(f"[{self.airline_name}] Waiting for airport options to load...")
            self._wait_for_options()
            
            # 2. Select Departure Airport
            logger.info(f"[{self.airline_name}] Selecting departure airport: {origin}")
            self._select_departure_airport(origin)
            self._random_delay(1, 2)
            
            # 3. Select Arrival Airport
            logger.info(f"[{self.airline_name}] Selecting arrival airport: {destination}")
            self._select_arrival_airport(destination)
            self._random_delay(1, 2)
            
            # 4. Select Departure Date
            logger.info(f"[{self.airline_name}] Setting departure date: {date}")
            self._set_date(date)
            self._random_delay(1, 2)
            
            # 5. Click Search Button
            logger.info(f"[{self.airline_name}] Clicking search button...")
            search_btn = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='search-flights']"))
            )
            # Scroll to center of viewport to avoid header/footer overlap
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center', inline: 'center'});", 
                search_btn
            )
            time.sleep(1)
            
            # Try regular click first, fall back to JS click
            try:
                search_btn.click()
            except Exception as click_error:
                logger.warning(f"[{self.airline_name}] Standard click failed, using JS click: {click_error}")
                self.driver.execute_script("arguments[0].click();", search_btn)
            
            # 6. Wait for Results
            logger.info(f"[{self.airline_name}] Waiting for results...")
            
            # Wait for URL to change to flight-result
            WebDriverWait(self.driver, 20).until(
                EC.url_contains("flight-result")
            )
            
            # Handling the Baggage Modal if it appears
            try:
                logger.info(f"[{self.airline_name}] Checking for Baggage Modal...")
                modal = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Baggage Allowance Notice')]"))
                )
                logger.info(f"[{self.airline_name}] Baggage Modal found. Attempting to dismiss/accept.")
                
                # Click checkbox
                checkbox = self.driver.find_element(By.CSS_SELECTOR, ".p-checkbox-box")
                checkbox.click()
                time.sleep(0.5)
                
                # Check for a Continue/Search button in the modal
                # Note: valid button might appear after check
                buttons = self.driver.find_elements(By.CSS_SELECTOR, ".p-dialog-footer button")
                for btn in buttons:
                    if "continue" in btn.text.lower() or "search" in btn.text.lower() or "proceed" in btn.text.lower():
                        btn.click()
                        break
                else:
                    # If no obvious continue button, maybe the 'Back' is actually 'Close'? 
                    # Or maybe just clicking the checkbox is enough? 
                    # Let's try to find any close icon
                    try:
                        close_icon = self.driver.find_element(By.CSS_SELECTOR, ".p-dialog-header-icons button")
                        close_icon.click()
                    except:
                        logger.warning(f"[{self.airline_name}] Could not find close button for modal")
                        
            except Exception:
                logger.info(f"[{self.airline_name}] No blocking baggage modal found (or timed out checking)")

            # Wait for Skeletons to disappear
            logger.info(f"[{self.airline_name}] Waiting for loading skeletons to disappear...")
            try:
                # Wait for any element that is NOT a skeleton in the results area
                # or just wait a fixed time for now to guarantee capture
                time.sleep(15) 
            except Exception:
                pass
            
            # Save results for analysis
            current_url = self.driver.current_url
            logger.info(f"[{self.airline_name}] Current URL after search: {current_url}")
            
            with open("valuejet_results.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            logger.info(f"[{self.airline_name}] Saved results to valuejet_results.html")
            
            # Screenshot for debugging
            self.driver.save_screenshot("valuejet_results.png")
            logger.info(f"[{self.airline_name}] Saved screenshot to valuejet_results.png")
            
            # 7. Parse Results
            flights = self._parse_results()
            logger.info(f"[{self.airline_name}] Found {len(flights)} flights")
            
        except Exception as e:
            logger.error(f"[{self.airline_name}] Scraping failed: {e}")
            if self.driver:
                self.driver.save_screenshot("valuejet_error.png")
                with open("valuejet_error.html", "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
        finally:
            self.quit()
        
        return flights
    
    def _wait_for_options(self):
        """Wait for the dropdown options to be populated by the React app."""
        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                dep_dropdown = self.driver.find_element(
                    By.CSS_SELECTOR, "[data-testid='departure-airport-dropdown']"
                )
                options = dep_dropdown.find_elements(By.TAG_NAME, "option")
                # We expect more than just the placeholder option
                if len(options) > 1:
                    logger.info(f"[{self.airline_name}] Found {len(options)} airport options")
                    # Log available airports for debugging
                    for opt in options[:5]:
                        logger.info(f"[{self.airline_name}]   Option: {opt.get_attribute('value')} - {opt.text}")
                    return
            except Exception as e:
                pass
            
            time.sleep(1)
            logger.info(f"[{self.airline_name}] Waiting for options... attempt {attempt + 1}/{max_attempts}")
        
        raise Exception("Airport dropdown options did not load within timeout")
    
    def _select_departure_airport(self, airport_code: str):
        """Select the departure airport."""
        dep_dropdown = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='departure-airport-dropdown']"))
        )
        self._select_from_dropdown(dep_dropdown, airport_code)
    
    def _select_arrival_airport(self, airport_code: str):
        """Select the arrival airport."""
        arr_dropdown = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='arrival-airport-dropdown']"))
        )
        self._select_from_dropdown(arr_dropdown, airport_code)
    
    def _select_from_dropdown(self, dropdown_elem, airport_code: str):
        """
        Select an airport from a dropdown. 
        Tries to match by value first, then by visible text containing the code.
        """
        select = Select(dropdown_elem)
        
        # First try: exact value match
        try:
            select.select_by_value(airport_code)
            logger.info(f"[{self.airline_name}] Selected by value: {airport_code}")
            return
        except:
            pass
        
        # Second try: find option containing the airport code
        for option in select.options:
            value = option.get_attribute('value') or ''
            text = option.text or ''
            if airport_code.upper() in value.upper() or airport_code.upper() in text.upper():
                select.select_by_visible_text(option.text)
                logger.info(f"[{self.airline_name}] Selected by text match: {option.text}")
                return
        
        # Log all available options for debugging
        logger.error(f"[{self.airline_name}] Could not find airport {airport_code}. Available options:")
        for option in select.options:
            logger.error(f"[{self.airline_name}]   {option.get_attribute('value')}: {option.text}")
        
        raise ValueError(f"Airport code {airport_code} not found in dropdown")
    
    def _set_date(self, date: str):
        """
        Set the departure date using the date picker.
        ValueJet uses a PrimeReact Calendar component.
        """
        try:
            # Click on the date input to open the calendar
            date_container = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='departure-date-input']"))
            )
            date_container.click()
            time.sleep(1)
            
            # Parse the target date
            target_date = datetime.strptime(date, "%Y-%m-%d")
            day = target_date.day
            
            # Wait for calendar to appear
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".p-datepicker"))
            )
            
            # Try to navigate to the correct month if needed
            # For now, assume current month is shown and try to click the day
            
            # Click the day (PrimeReact uses spans with specific structure)
            # Try multiple selector patterns
            day_selectors = [
                f"//td[not(contains(@class,'disabled'))]/span[text()='{day}']",
                f"//span[@class='p-datepicker-day' and text()='{day}']",
                f"//*[@class='p-datepicker']//span[text()='{day}']"
            ]
            
            for selector in day_selectors:
                try:
                    day_elem = WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    day_elem.click()
                    logger.info(f"[{self.airline_name}] Selected day {day} using selector")
                    return
                except:
                    continue
            
            # Fallback: try clicking any element with the day number
            all_spans = self.driver.find_elements(By.CSS_SELECTOR, ".p-datepicker span")
            for span in all_spans:
                if span.text == str(day):
                    span.click()
                    logger.info(f"[{self.airline_name}] Selected day {day} via span search")
                    return
            
            logger.warning(f"[{self.airline_name}] Could not click date, trying input injection...")
            # Last resort: inject the date into the input
            date_input = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='departure-date-input'] input")
            formatted_date = target_date.strftime("%d/%m/%Y")
            self.driver.execute_script(
                f"arguments[0].value = '{formatted_date}'; arguments[0].dispatchEvent(new Event('change'));",
                date_input
            )
            
        except Exception as e:
            logger.warning(f"[{self.airline_name}] Date selection failed: {e}")
    
    def _parse_results(self) -> List[FlightOffer]:
        """
        Parse flight results from the search results page.
        """
        flights = []
        
        try:
            # Flight containers: Identify by the border styling and structure seen in HTML
            # <div class="flex flex-col w-full border border-gray-200 rounded-lg lg:pb-4 mb-4">
            flight_elements = self.driver.find_elements(
                By.XPATH, 
                "//div[contains(@class, 'border-gray-200')][descendant::p[contains(text(), 'VK')]]"
            )
            logger.info(f"[{self.airline_name}] Found {len(flight_elements)} flight elements")
            
            for idx, elem in enumerate(flight_elements):
                try:
                    flight = self._parse_flight_element(elem, idx)
                    if flight:
                        flights.append(flight)
                except Exception as e:
                    logger.warning(f"[{self.airline_name}] Failed to parse flight {idx}: {e}")
        
        except Exception as e:
            logger.error(f"[{self.airline_name}] Failed to parse results: {e}")
        
        return flights
    
    def _parse_flight_element(self, elem, idx: int) -> FlightOffer:
        """
        Parse a single flight element into a FlightOffer.
        """
        try:
            # Extract Flight Number (e.g., VK200)
            # It's in a <p> tag, uppercase
            flight_num_elem = elem.find_element(By.XPATH, ".//p[starts-with(text(), 'VK')]")
            flight_number = flight_num_elem.text.strip()
            
            # Extract Departure Time & Arrival Time
            # Found in: <span class="text-primary text-2xl font-semibold">06:45</span>
            time_elements = elem.find_elements(By.CSS_SELECTOR, ".text-2xl.font-semibold")
            
            if len(time_elements) < 2:
                # Fallback: try different selector if the class varies
                time_elements = elem.find_elements(By.XPATH, ".//span[contains(@class, 'text-2xl')]")
            
            if len(time_elements) < 2:
                logger.warning(f"[{self.airline_name}] Could not find time elements for flight {idx}")
                return None
            
            dep_time_str = time_elements[0].text.strip()
            arr_time_str = time_elements[1].text.strip()
            
            # Construct full datetime strings (YYYY-MM-DDTHH:MM:SS)
            # Standardize time (remove AM/PM if present, or convert)
            # The HTML shows "06:45" and separate "AM" span, but usually text-2xl has the numbers
            
            dep_datetime = f"{self.search_params['date']}T{dep_time_str}:00"
            arr_datetime = f"{self.search_params['date']}T{arr_time_str}:00"
            
            # Extract Price
            # <button ...><span>₦</span>145,714...</button>
            # Look for button text containing the currency symbol
            price_amount = 0.0
            
            # Try finding the price button
            price_elem = elem.find_element(By.XPATH, ".//button[.//span[contains(text(), '₦')]]")
            
            # Get text, strip currency and commas
            price_text = price_elem.text.replace('₦', '').replace(',', '').strip()
            
            # Extract first valid float
            import re
            match = re.search(r'(\d+)', price_text)
            if match:
                price_amount = float(match.group(1))
            
            # Create FlightOffer object
            return FlightOffer(
                source=self.airline_name,
                airline=self.airline_name,
                flight_number=flight_number,
                origin=self.search_params['origin'],
                destination=self.search_params['destination'],
                departure_time=dep_datetime,
                arrival_time=arr_datetime,
                price=price_amount,
                currency="NGN",
                # cabin_class="ECONOMY" # Removed as it's not in the model
            )
            
        except Exception as e:
            logger.warning(f"[{self.airline_name}] Parse error for flight {idx}: {e}")
            return None
