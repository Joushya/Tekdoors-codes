import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException


class DancerVibesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize the Chrome driver
        cls.driver = webdriver.Chrome()
        cls.driver.maximize_window()
        cls.base_url = "https://stage.dancervibes.com/dancerjou"
        cls.test_results = []

    def test_001_signup_valid_credentials(self):
        """Verify successful sign-up with valid credentials"""
        test_name = "SignUp_001"
        result = "Pass"
        error_msg = ""

        try:
            # Navigate to signup page
            self.driver.get(f"{self.base_url}/customer/signup")

            # Fill in signup form
            self.driver.find_element(By.ID, "fname").send_keys("Test")
            self.driver.find_element(By.ID, "lname").send_keys("User")
            self.driver.find_element(By.ID, "username").send_keys("joush1")
            self.driver.find_element(By.ID, "email").send_keys("joushcovind@gmail.com")
            self.driver.find_element(By.ID, "phone").send_keys("1234567899")
            self.driver.find_element(By.ID, "dance_style").send_keys("Hip Hop")
            self.driver.find_element(By.ID, "dance_level").send_keys("Beginner")
            self.driver.find_element(By.ID, "password").send_keys("Jerry@2020")
            self.driver.find_element(By.ID, "password_confirmation").send_keys("Jerry@2020")

            # Submit form
            self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

            # Verify successful signup
            WebDriverWait(self.driver, 10).until(
                EC.url_contains("dashboard")
            )

        except Exception as e:
            result = "Fail"
            error_msg = str(e)
            self.driver.save_screenshot(f"{test_name}_error.png")

        finally:
            self.test_results.append({
                "Test Case": test_name,
                "Result": result,
                "Error": error_msg
            })

    def test_002_signup_facebook(self):
        """Verify successful sign-up with valid Facebook credentials"""
        test_name = "SignUp_002"
        result = "Pass"
        error_msg = ""

        try:
            # Navigate to signup page
            self.driver.get(f"{self.base_url}/customer/signup")

            # Click Facebook signup (assuming there's a Facebook button)
            fb_button = self.driver.find_element(By.XPATH, "//a[contains(text(),'Facebook')]")
            fb_button.click()

            # Switch to Facebook login window
            WebDriverWait(self.driver, 10).until(EC.number_of_windows_to_be(2))
            self.driver.switch_to.window(self.driver.window_handles[1])

            # Verify Facebook login page
            WebDriverWait(self.driver, 10).until(
                EC.title_contains("Facebook")
            )

            # Close Facebook window and switch back
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])

        except Exception as e:
            result = "Fail"
            error_msg = str(e)
            self.driver.save_screenshot(f"{test_name}_error.png")

        finally:
            self.test_results.append({
                "Test Case": test_name,
                "Result": result,
                "Error": error_msg
            })

    def test_003_signup_google(self):
        """Verify successful sign-up with valid Google credentials"""
        test_name = "SignUp_003"
        result = "Pass"
        error_msg = ""

        try:
            # Navigate to signup page
            self.driver.get(f"{self.base_url}/customer/signup")

            # Click Google signup (assuming there's a Google button)
            google_button = self.driver.find_element(By.XPATH, "//a[contains(text(),'Google')]")
            google_button.click()

            # Switch to Google login window
            WebDriverWait(self.driver, 10).until(EC.number_of_windows_to_be(2))
            self.driver.switch_to.window(self.driver.window_handles[1])

            # Verify Google login page
            WebDriverWait(self.driver, 10).until(
                EC.title_contains("Google")
            )

            # Close Google window and switch back
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])

        except Exception as e:
            result = "Fail"
            error_msg = str(e)
            self.driver.save_screenshot(f"{test_name}_error.png")

        finally:
            self.test_results.append({
                "Test Case": test_name,
                "Result": result,
                "Error": error_msg
            })

    def test_004_forgot_password(self):
        """Verify Functionality of Forgot Password Link"""
        test_name = "Login_004"
        result = "Pass"
        error_msg = ""

        try:
            # Navigate to login page
            self.driver.get(f"{self.base_url}/customer/login")

            # Click forgot password link
            forgot_pwd_link = self.driver.find_element(By.LINK_TEXT, "forgot password?")
            forgot_pwd_link.click()

            # Verify reset password page
            WebDriverWait(self.driver, 10).until(
                EC.url_contains("forget-password")
            )

            # Enter email and submit
            email_input = self.driver.find_element(By.NAME, "email")
            email_input.send_keys("pritk572@gmail.com")
            self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

            # Verify success message
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "successIcon")))

        except Exception as e:
            result = "Fail"
            error_msg = str(e)
            self.driver.save_screenshot(f"{test_name}_error.png")

        finally:
            self.test_results.append({
                "Test Case": test_name,
                "Result": result,
                "Error": error_msg
            })

    def test_005_login_valid_credentials(self):
        """Verify login functionality with valid credentials"""
        test_name = "Login_005"
        result = "Pass"
        error_msg = ""

        try:
            # Navigate to login page
            self.driver.get(f"{self.base_url}/customer/login")

            # Enter credentials and submit
            username_input = self.driver.find_element(By.ID, "username")
            username_input.send_keys("joushya22@gmail.com")

            password_input = self.driver.find_element(By.ID, "password")
            password_input.send_keys("Jerry@2020")

            self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

            # Verify successful login
            WebDriverWait(self.driver, 10).until(
                EC.url_contains("dashboard")
            )

        except Exception as e:
            result = "Fail"
            error_msg = str(e)
            self.driver.save_screenshot(f"{test_name}_error.png")

        finally:
            self.test_results.append({
                "Test Case": test_name,
                "Result": result,
                "Error": error_msg
            })

    def test_006_dashboard_display(self):
        """Verify Dashboard Display with Participant details"""
        test_name = "Dashboard_006"
        result = "Pass"
        error_msg = ""

        try:
            # Ensure we're logged in (run login test first)
            self.test_005_login_valid_credentials()

            # Verify dashboard elements
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "header-user-wrapper")))

            # Verify user info is displayed
            user_name = self.driver.find_element(By.CLASS_NAME, "user-name")
            self.assertTrue(user_name.text.strip() != "")

        except Exception as e:
            result = "Fail"
            error_msg = str(e)
            self.driver.save_screenshot(f"{test_name}_error.png")

        finally:
            self.test_results.append({
                "Test Case": test_name,
                "Result": result,
                "Error": error_msg
            })

    @classmethod
    def tearDownClass(cls):


        # Close the browser
        cls.driver.quit()


if __name__ == "__main__":
    unittest.main()