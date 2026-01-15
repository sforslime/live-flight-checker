
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time
from datetime import datetime

def setup_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless") # Run visible for now
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1280, 800)
    return driver

def main():
    driver = setup_driver()
    try:
        # Direct URL to the booking iframe form
        url = "https://booking.xejet.com/VARS/public/CustomerPanels/requirementsBS.aspx"
        print(f"Navigating to {url}")
        driver.get(url)
        
        # 1. Select Origin
        print("Selecting Origin: LOS")
        origin_select = Select(WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "Origin"))
        ))
        origin_select.select_by_value("LOS")
        time.sleep(1) # Wait for update
        
        # 2. Select Destination
        print("Selecting Destination: ABV")
        dest_select = Select(driver.find_element(By.ID, "Destination"))
        # Force update if needed? Usually select_by_value is enough
        dest_select.select_by_value("ABV")
        
        # 3. Select One Way
        print("Selecting One Way")
        # Find label containing "One Way"
        labels = driver.find_elements(By.TAG_NAME, "label")
        for label in labels:
            if "One Way" in label.text:
                label.click()
                break
        
        # 4. Set Date
        target_date = "18-Jan-2026"
        print(f"Setting Date: {target_date}")
        date_input = driver.find_element(By.ID, "departuredate")
        # Use JS to set value as it might be readonly/restricted
        driver.execute_script(f"arguments[0].value = '{target_date}';", date_input)
        driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", date_input)
        
        # 5. Submit
        print("Clicking Search")
        submit_btn = driver.find_element(By.ID, "submitButton")
        submit_btn.click()
        
        # 6. Wait for Results
        print("Waiting for results...")
        WebDriverWait(driver, 20).until(
            EC.url_contains("FlightCAL.aspx")
        )
        print("Reached Results Page!")
        
        # Save HTML
        with open("xejet_results_raw.html", "w") as f:
            f.write(driver.page_source)
        print("Saved raw HTML to xejet_results_raw.html")
        
        time.sleep(5)
        
    except Exception as e:
        print(f"Error: {e}")
        driver.save_screenshot("xejet_error.png")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
