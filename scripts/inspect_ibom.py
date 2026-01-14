import sys
import os
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.scrapers.base_scraper import BaseScraper

class Inspector(BaseScraper):
    def scrape(self, origin, destination, date):
        pass # Not used
        
    def inspect(self):
        try:
            self._setup_driver()
            url = "https://www.ibomair.com"
            print(f"Navigating to {url}...")
            self.driver.get(url)
            
            # Wait for page to load
            time.sleep(5) 
            
            print(f"Page Title: {self.driver.title}")
            
            # Save HTML for analysis
            with open("ibom_source.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            print("Saved page source to ibom_source.html")
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.quit()

if __name__ == "__main__":
    inspector = Inspector("Ibom Inspector")
    inspector.inspect()
