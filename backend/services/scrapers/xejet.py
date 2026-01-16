
import time
import logging
from typing import List
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from backend.services.scrapers.base_scraper import BaseScraper
from backend.models import FlightOffer

logger = logging.getLogger(__name__)

class XEJetScraper(BaseScraper):
    """
    Scraper for XEJet (AeroCRS based)
    """
    def __init__(self):
        super().__init__("XEJet")
        # Direct link to the booking iframe form to avoid complex navigation
        self.base_url = "https://booking.xejet.com/VARS/public/CustomerPanels/requirementsBS.aspx"
        
    def scrape(self, origin: str, destination: str, date: str) -> List[FlightOffer]:
        self._setup_driver()
        self.search_params = {
            'origin': origin,
            'destination': destination,
            'date': date
        }
        flights = []
        
        try:
            logger.info(f"[{self.airline_name}] Navigating to search form: {self.base_url}")
            self.driver.get(self.base_url)
            
            # 1. Select Origin
            logger.info(f"[{self.airline_name}] Selecting Origin: {origin}")
            origin_select = Select(WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "Origin"))
            ))
            origin_select.select_by_value(origin)
            time.sleep(2) # Allow destination dropdown to update
            
            # 2. Select Destination
            logger.info(f"[{self.airline_name}] Selecting Destination: {destination}")
            dest_select = Select(self.driver.find_element(By.ID, "Destination"))
            dest_select.select_by_value(destination)
            
            # 3. Select One Way
            # AeroCRS usually has a label for "One Way"
            labels = self.driver.find_elements(By.TAG_NAME, "label")
            for label in labels:
                if "One Way" in label.text:
                    label.click()
                    break
            
            # 4. Set Date (Natural Interaction via jQuery UI Datepicker)
            target_date_obj = datetime.strptime(date, "%Y-%m-%d")
            target_day = str(target_date_obj.day)
            target_month = target_date_obj.strftime("%B") # e.g., "January"
            target_year = str(target_date_obj.year)

            logger.info(f"[{self.airline_name}] Opening date picker...")
            date_input = self.driver.find_element(By.ID, "departuredate")
            date_input.click()
            
            # Wait for calendar
            calendar = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.ID, "ui-datepicker-div"))
            )
            
            # Navigate to correct month/year
            max_months = 12
            for _ in range(max_months):
                curr_month = self.driver.find_element(By.CSS_SELECTOR, ".ui-datepicker-month").text
                curr_year = self.driver.find_element(By.CSS_SELECTOR, ".ui-datepicker-year").text
                
                if curr_month == target_month and curr_year == target_year:
                    break
                
                # Click Next
                try:
                    next_btn = self.driver.find_element(By.CSS_SELECTOR, ".ui-datepicker-next")
                    next_btn.click()
                    time.sleep(0.5)
                except Exception:
                    logger.warning(f"[{self.airline_name}] Could not find next month button")
                    break
            
            # Click Day
            logger.info(f"[{self.airline_name}] Selecting day: {target_day}")
            # The 'a' tag has class 'ui-state-default' and text is the day number
            # We look for 'td' not having 'ui-datepicker-other-month' to ensure we pick current month's day
            day_xpath = f"//td[not(contains(@class, 'ui-datepicker-other-month'))]//a[text()='{target_day}']"
            day_link = self.driver.find_element(By.XPATH, day_xpath)
            day_link.click()
            
            time.sleep(1) # Wait for UI to settle
            
            # 5. Click Search
            logger.info(f"[{self.airline_name}] Clicking Search...")
            search_btn = self.driver.find_element(By.ID, "submitButton")
            search_btn.click()
            
            # 6. Wait for Results
            logger.info(f"[{self.airline_name}] Waiting for results page...")
            WebDriverWait(self.driver, 30).until(
                EC.url_contains("Flight") # FlightCAL.aspx or similar
            )
            
            # 7. Dump HTML for parsing analysis
            with open("xejet_results.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            logger.info(f"[{self.airline_name}] Saved results HTML to xejet_results.html")
            
            # 8. Attempt Parsing
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

    def _parse_results(self) -> List[FlightOffer]:
        flights = []
        try:
            # Locate all flight rows
            # Based on HTML: div class="row no-gutter flt-row" or id starting with flt_row
            flight_rows = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'flt-row') and not(contains(@class, 'flt-facts')) and not(contains(@class, 'flt-classes'))]")
            
            logger.info(f"[{self.airline_name}] Found {len(flight_rows)} flight rows")
            
            for idx, elem in enumerate(flight_rows):
                try:
                    flight = self._parse_flight_element(elem, idx)
                    if flight:
                        flights.append(flight)
                except Exception as e:
                    logger.warning(f"[{self.airline_name}] Failed to parse flight {idx}: {e}")
                
        except Exception as e:
            logger.warning(f"[{self.airline_name}] Parsing error: {e}")
            
        return flights

    def _parse_flight_element(self, elem, idx: int) -> FlightOffer:
        try:
            # Extract basics
            flight_num = elem.find_element(By.CLASS_NAME, "flightnumber").text.strip()
            
            # Times
            dep_time_str = elem.find_element(By.CSS_SELECTOR, ".cal-Depart-time .time").text.strip()
            arr_time_str = elem.find_element(By.CSS_SELECTOR, ".cal-Arrive-time .time").text.strip()
            
            # Construct Datetimes
            # The dates are also in .flightDate (e.g. "20 Jan"), but we know the search date.
            # We assume single day search for now.
            date_str = self.search_params['date'] # YYYY-MM-DD
            dep_datetime = f"{date_str}T{dep_time_str}:00"
            arr_datetime = f"{date_str}T{arr_time_str}:00"
            
            # Price
            # <div class="... fare-price-small ..." data-original-amount="260501" ...>
            price_elem = elem.find_element(By.CSS_SELECTOR, ".fare-price-small")
            price_amount = float(price_elem.get_attribute("data-original-amount"))
            currency = price_elem.get_attribute("data-original-currency") or "NGN"
            
            return FlightOffer(
                source=self.airline_name,
                airline=self.airline_name,
                flight_number=flight_num,
                origin=self.search_params['origin'],
                destination=self.search_params['destination'],
                departure_time=dep_datetime,
                arrival_time=arr_datetime,
                price=price_amount,
                currency=currency.upper(),
                booking_link=self.base_url 
            )
            
        except Exception as e:
            # It's possible some rows are headers or hidden
            # logger.debug(f"[{self.airline_name}] Skipping row {idx}: {e}")
            return None
