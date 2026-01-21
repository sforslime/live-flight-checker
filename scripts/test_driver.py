from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time

def test_driver():
    print("Setting up driver...")
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Force fresh install
    path = ChromeDriverManager().install()
    print(f"Driver installed at: {path}")
    
    service = Service(path)
    driver = webdriver.Chrome(service=service, options=options)
    
    print("Driver started. Navigating...")
    driver.get("https://example.com")
    print(f"Title: {driver.title}")
    
    driver.quit()
    print("Driver closed successfully.")

if __name__ == "__main__":
    try:
        test_driver()
    except Exception as e:
        print(f"FAILED: {e}")
