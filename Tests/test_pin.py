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


def test_update_delivery_pincodes():
    driver = setup_driver()
    try:
        # Step 1: Login as delivery person
        time.sleep(2)
        driver.get("http://127.0.0.1:8000/Login/")
        
        # Fill in login credentials for delivery person
        email_field = driver.find_element(By.NAME, "your_email")
        email_field.send_keys("augustinesebastian007@gmail.com")  # Replace with valid delivery account email
        
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
        
        # Step 2: Scroll down to the "Your Delivery Areas" section
        try:
            # Find the "Your Delivery Areas" heading
            delivery_areas_heading = driver.find_element(By.XPATH, "//h5[contains(text(), 'Your Delivery Areas')]")
            
            # Scroll to the delivery areas section
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", delivery_areas_heading)
            time.sleep(1)  # Wait for scroll to complete
            print("Scrolled to 'Your Delivery Areas' section")
            
            # Step 3: Click the "Update Delivery Areas" button
            update_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Update Delivery Areas')]")
            click_element_safely(driver, update_button)
            print("Clicked 'Update Delivery Areas' button")
            
            # Wait for the modal to appear
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "updatePincodesModal"))
            )
            print("Update Pincodes modal opened")
            
            # Step 4: Change the primary pincode
            primary_pincode_select = driver.find_element(By.ID, "primary_pincode")
            primary_pincode_select.click()
            time.sleep(1)
            
            # Get all available options
            primary_options = primary_pincode_select.find_elements(By.TAG_NAME, "option")
            
            # Select a different option than the currently selected one
            current_primary = None
            for option in primary_options:
                if option.is_selected():
                    current_primary = option.get_attribute("value")
                    break
            
            # Choose a different option
            for option in primary_options:
                option_value = option.get_attribute("value")
                if option_value != current_primary:
                    option.click()
                    print(f"Changed primary pincode from {current_primary} to {option_value}")
                    break
            
            # Step 5: Change the secondary pincode
            secondary_pincode_select = driver.find_element(By.ID, "secondary_pincode")
            secondary_pincode_select.click()
            time.sleep(1)
            
            # Get current secondary pincode
            secondary_options = secondary_pincode_select.find_elements(By.TAG_NAME, "option")
            current_secondary = None
            for option in secondary_options:
                if option.is_selected():
                    current_secondary = option.get_attribute("value")
                    break
            
            # Select a different option that's not the primary pincode
            new_primary = primary_pincode_select.find_element(By.XPATH, "./option[@selected]").get_attribute("value")
            for option in secondary_options:
                option_value = option.get_attribute("value")
                if option_value != current_secondary and option_value != new_primary and option_value != "":
                    option.click()
                    print(f"Changed secondary pincode from {current_secondary} to {option_value}")
                    break
            
            # Step 6: Submit the form
            update_button = driver.find_element(By.XPATH, "//div[@id='updatePincodesModal']//button[@type='submit']")
            click_element_safely(driver, update_button)
            print("Submitted pincode update form")
            
            # Wait for the update to complete
            time.sleep(3)
            
            # Verify that the update was successful (check for success message)
            try:
                success_message = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
                )
                print(f"Success message found: {success_message.text}")
            except:
                print("No success message found, but form was submitted")
                
        except Exception as e:
            print(f"Error updating delivery areas: {str(e)}")
            driver.save_screenshot("delivery_areas_error.png")
            print("Screenshot saved as delivery_areas_error.png")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        driver.save_screenshot("update_pincodes_error.png")
        print("Screenshot saved as update_pincodes_error.png")
    finally:
        driver.quit()

# Update main function to call the new test function
def main():
    test_update_delivery_pincodes()

if __name__ == "__main__":
    main()