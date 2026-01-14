"""
Script to inspect ValueJet website structure for scraping.
"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def main():
    chrome_options = Options()
    # Run in headed mode to see what's happening
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.page_load_strategy = 'eager'
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        print("Navigating to ValueJet homepage...")
        driver.get("https://www.flyvaluejet.com")
        
        # Wait for page to load
        time.sleep(5)
        
        print(f"Current URL: {driver.current_url}")
        print(f"Page Title: {driver.title}")
        
        # Save the page source for analysis
        with open("valuejet_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Saved page source to valuejet_source.html")
        
        # Take a screenshot
        driver.save_screenshot("valuejet_screenshot.png")
        print("Saved screenshot to valuejet_screenshot.png")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
