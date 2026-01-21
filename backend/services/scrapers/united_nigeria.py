import logging
import time
from typing import List
from datetime import datetime
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from backend.models import FlightOffer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UnitedNigeriaScraper:
    def __init__(self):
        self.airline_name = "United Nigeria Airlines"
        self.driver = None

    def _setup_driver(self):
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.options import Options

        options = Options()
        options.add_argument("--headless=new") 
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.set_page_load_timeout(60)

    def scrape(self, origin: str, destination: str, date: str) -> List[FlightOffer]:
        """
        Scrape United Nigeria Airlines flights.
        date format expected: YYYY-MM-DD
        """
        self._setup_driver()
        flights = []
        
        try:
            # 1. Format date to dd-MMM-yyyy (e.g., 16-Jan-2026)
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            date_formatted = date_obj.strftime("%d-%b-%Y")
            
            # 2. Navigate to Booking Widget (Direct)
            url = "https://booking.flyunitednigeria.com/VARS/Public/CustomerPanels/requirementsBS.aspx"
            logger.info(f"[{self.airline_name}] Navigating to {url}")
            self.driver.get(url)
            time.sleep(5) # Let initial JS settle
            
            # 3. Select One Way
            try:
                # ID ReturnTrip2 is for One Way
                one_way_radio = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "ReturnTrip2"))
                )
                one_way_radio.click()
            except Exception as e:
                logger.warning(f"Could not select One Way: {e}")

            # 4. Select Origin and Destination (Human Typing)
            try:
                from selenium.webdriver.common.keys import Keys
                
                # Origin
                logger.info(f"Typing Origin: {origin}")
                origin_el = self.driver.find_element(By.ID, "Origin")
                origin_el.click()
                origin_el.send_keys(origin)
                time.sleep(0.5)
                origin_el.send_keys(Keys.ENTER)
                
                # Force trigger change just in case
                self.driver.execute_script("$('#Origin').trigger('change');")
                
                time.sleep(3) 

                # Destination
                logger.info(f"Typing Destination: {destination}")
                dest_el = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "Destination"))
                )
                dest_el.click()
                dest_el.send_keys(destination)
                time.sleep(0.5)
                dest_el.send_keys(Keys.ENTER)
                self.driver.execute_script("$('#Destination').trigger('change');")
                
            except Exception as e:
                logger.error(f"Could not interact with airports: {e}")
                return []

            # 5. Set Date
            logger.info(f"Setting date to {date_formatted}")
            self.driver.execute_script(f"$('#departuredate').datepicker('setDate', '{date_formatted}');")
            self.driver.execute_script(f"$('#departuredate').trigger('change');") 
            
            # 6. Click Continue
            logger.info("Clicking Search...")
            submit_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "submitButton"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
            time.sleep(1)
            
            # Try plain click first
            try:
                submit_btn.click()
            except:
                logger.warning("Regular click failed, trying ActionChains")
                from selenium.webdriver.common.action_chains import ActionChains
                ActionChains(self.driver).move_to_element(submit_btn).click().perform()
            
            # 7. Wait for Results
            logger.info("Waiting for results...")
            try:
                # Wait for URL change OR a specific element in the new page
                WebDriverWait(self.driver, 30).until(
                    lambda d: "requirementsBS.aspx" not in d.current_url 
                )
                # Give the new page a moment to render content
                WebDriverWait(self.driver, 30).until(
                     EC.presence_of_element_located((By.ID, "divBasket2")) # Basket usually appears on results
                )
            except Exception as e:
                logger.warning(f"Wait for results timed out or failed: {e}")
                
            # 8. Parse Results
            flights = self._parse_results(origin, destination, date_obj)
            return flights
            
        except Exception as e:
            logger.error(f"[{self.airline_name}] Scraping failed: {e}")
            if self.driver:
                self.driver.save_screenshot(f"{self.airline_name.lower().replace(' ', '_')}_error.png")
                with open(f"{self.airline_name.lower().replace(' ', '_')}_error.html", "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
        finally:
            if self.driver:
                self.driver.quit()
        
        return []

    def _parse_results(self, origin, destination, date_obj) -> List[FlightOffer]:
        flights = []
        try:
            # Locate the flight table (Videcom usually uses tables inside divAvailabilityPanel)
            # We look for rows with flight info.
            # This is speculative based on common Videcom layouts.
            # Row class usually "AvailabilityRow"
            
            rows = self.driver.find_elements(By.CLASS_NAME, "AvailabilityRow")
            logger.info(f"Found {len(rows)} flight rows.")
            
            for row in rows:
                try:
                    # Extract Data
                    # Videcom rows usually have cells with times and flight number.
                    # This needs adjustment once we see the actual HTML.
                    # For now, we will log the text content to verify.
                    
                    flight_text = row.text
                    logger.info(f"Processing row: {flight_text}")
                    
                    # Placeholder Parser
                    # We need to find specific elements.
                    # Flight Num: .flightNo
                    # Dep Time: .depTime
                    # Arr Time: .arrTime
                    # Price: .price (or inside the radio button label)
                    
                    # If I assume generic structure:
                    # Time is usually in first few columns.
                    # Price is in the fare class columns.
                    
                    # Let's try to extract minimum info to return a valid object
                    # We will likely fail on specific selectors without seeing the HTML.
                    # So I will return valid dummy data if we found rows, to prove connectivity.
                    # AND save the HTML for refinement.
                    pass
                    
                except Exception as row_e:
                    logger.error(f"Error parsing row: {row_e}")
            
            if len(rows) > 0:
                # Save the HTML to refine the parser
                with open("united_success_results.html", "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                    
        except Exception as e:
            logger.error(f"Parsing error: {e}")
            
        return flights

