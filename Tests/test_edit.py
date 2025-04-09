import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from datetime import datetime, timedelta

# Helper function from your existing tests
def click_element_safely(driver, element):
    try:
        # Scroll element into view
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.5)  # Give time for any animations
        
        # Click the element
        element.click()
    except Exception as e:
        print(f"Error clicking element: {str(e)}")
        # Try JavaScript click as fallback
        try:
            driver.execute_script("arguments[0].click();", element)
        except Exception as js_error:
            print(f"JavaScript click also failed: {str(js_error)}")
            raise

# Setup driver function
def setup_driver():
    chrome_options = Options()
    # Uncomment the following line for headless testing
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    return driver




def test_delivery_workflow():
    driver = setup_driver()
    try:
        # Step 1: Login as delivery person
        time.sleep(2)
        driver.get("http://127.0.0.1:8000/Login/")
        
        # Fill in login credentials for delivery person
        email_field = driver.find_element(By.NAME, "your_email")
        email_field.send_keys("augustinesebastian007@gmail.com") 
        
        password_field = driver.find_element(By.NAME, "your_password")
        password_field.send_keys("Sebastian@123")  # Replace with valid delivery account password
        
        # Click login button
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        click_element_safely(driver, login_button)
        
        # Wait for login to complete
        WebDriverWait(driver, 10).until(EC.url_changes("http://127.0.0.1:8000/Login/"))
        print(f"Logged in as delivery person. Current URL: {driver.current_url}")
        
        # Add a delay to ensure page is fully loaded
        time.sleep(3)
        
        # Step 2: Find and click "Start Delivery" on the first pending order
        start_delivery_buttons = driver.find_elements(By.XPATH, "//a[contains(text(), 'Start Delivery')]")
        
        if start_delivery_buttons:
            # Scroll to the start delivery button
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", start_delivery_buttons[0])
            time.sleep(1)  # Wait for scroll to complete
            
            # Click the first Start Delivery button
            click_element_safely(driver, start_delivery_buttons[0])
            print("Clicked 'Start Delivery' button")
            
            # Wait for page to refresh or redirect
            time.sleep(3)
            print(f"Current URL after starting delivery: {driver.current_url}")
            
            # Step 3: Now find and click "Complete Delivery" for the active order
            # Scroll down to the active orders section
            active_orders_heading = driver.find_element(By.XPATH, "//h3[contains(text(), 'Active Orders')]")
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", active_orders_heading)
            time.sleep(1)  # Wait for scroll to complete
            
            # Find Complete Delivery button
            complete_delivery_buttons = driver.find_elements(By.XPATH, "//a[contains(text(), 'Complete Delivery')]")
            
            if complete_delivery_buttons:
                # Scroll to the complete delivery button
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", complete_delivery_buttons[0])
                time.sleep(1)  # Wait for scroll to complete
                
                # Click the first Complete Delivery button
                click_element_safely(driver, complete_delivery_buttons[0])
                print("Clicked 'Complete Delivery' button")
                
                # Wait for page to refresh or redirect
                time.sleep(3)
                print(f"Current URL after completing delivery: {driver.current_url}")
                
                # Verify that delivery was completed (check for success message or status change)
                try:
                    success_message = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
                    )
                    print(f"Success message found: {success_message.text}")
                except:
                    print("No success message found, but delivery workflow completed")
            else:
                print("No 'Complete Delivery' buttons found")
                driver.save_screenshot("active_orders_page.png")
                print("Screenshot saved as active_orders_page.png")
        else:
            print("No 'Start Delivery' buttons found")
            driver.save_screenshot("pending_orders_page.png")
            print("Screenshot saved as pending_orders_page.png")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        driver.save_screenshot("delivery_error.png")
        print("Screenshot saved as delivery_error.png")
    finally:
        driver.quit()

# Update main function to call the new test function
def main():
    test_delivery_workflow()

if __name__ == "__main__":
    main()