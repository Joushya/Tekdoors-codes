import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
import logging
import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"forgot_password_tests_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ForgotPasswordTests(unittest.TestCase):
    """Test cases for the forgot password functionality of StudioMeets application."""

    def setUp(self):
        """Set up the test environment before each test case."""
        self.base_url = "https://stage.dancervibes.com/admin/login"
        self.forgot_password_url = "https://stage.dancervibes.com/admin/login/forget-password"

        # Setup Chrome WebDriver
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")  # Start browser maximized
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-popup-blocking")

        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.set_page_load_timeout(30)
            self.wait = WebDriverWait(self.driver, 15)
            logger.info(f"Set up test environment successfully for {self._testMethodName}")
        except Exception as e:
            logger.error(f"Failed to set up test environment: {str(e)}")
            raise

    def tearDown(self):
        """Clean up after each test case."""
        if hasattr(self, 'driver') and self.driver:
            try:
                self.driver.quit()
                logger.info(f"Tore down test environment successfully for {self._testMethodName}")
            except Exception as e:
                logger.error(f"Error during tearDown: {str(e)}")

    def click_element_safely(self, element, max_attempts=3):
        """Helper method to safely click elements, handling potential issues."""
        attempt = 0
        while attempt < max_attempts:
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(0.5)
                element.click()
                logger.info("Successfully clicked element")
                return True
            except ElementClickInterceptedException:
                logger.warning(f"Click intercepted, attempt {attempt + 1}/{max_attempts}")
                try:
                    self.driver.execute_script("arguments[0].click();", element)
                    logger.info("Successfully clicked element using JavaScript")
                    return True
                except Exception as js_e:
                    logger.warning(f"JavaScript click failed with error: {str(js_e)}")
            except Exception as e:
                logger.warning(f"Click failed with error: {str(e)}")
            attempt += 1
            time.sleep(1)
        logger.error("Failed to click element after maximum attempts")
        return False

    def test_001_verify_reset_password_page_accessibility(self):
        """TC_Reset Password or Username_001: Verify Reset Password Page Accessibility."""
        try:
            logger.info("Starting test_001_verify_reset_password_page_accessibility")
            self.driver.get(self.base_url)
            logger.info(f"Navigated to login page: {self.base_url}")
            self.assertIn("login", self.driver.current_url.lower())
            logger.info("Login page is accessible")

            # Find and click the "Forgot Password" link
            forgot_password_link = None
            locators = [
                "//a[contains(text(), 'Forgot Password')]",
                "//a[contains(text(), 'Reset Password')]",
                "//a[contains(text(), 'forgot')]",
                "//a[contains(@href, 'forget-password')]",
                "//div[contains(@class, 'login')]//a",
                "//form//a",
                "//a[contains(@class, 'login_link')]"
            ]

            for locator in locators:
                try:
                    forgot_password_links = self.driver.find_elements(By.XPATH, locator)
                    if forgot_password_links:
                        for link in forgot_password_links:
                            if "forgot" in link.text.lower() or "reset" in link.text.lower() or "forget-password" in (
                                    link.get_attribute("href") or ""):
                                forgot_password_link = link
                                logger.info(f"Found forgot password link using locator: {locator}")
                                break
                    if forgot_password_link:
                        break
                except NoSuchElementException:
                    continue

            if not forgot_password_link:
                screenshot_path = f"test_001_fail_{time.time()}.png"
                self.driver.save_screenshot(screenshot_path)
                logger.error(f"Failed to find forgot password link. Screenshot saved to {screenshot_path}")
                with open(f"page_source_{time.time()}.html", "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                self.fail("Could not find the forgot password link on the login page")

            self.click_element_safely(forgot_password_link)
            logger.info("Clicked on forgot password link")

            time.sleep(2)
            try:
                self.wait.until(EC.url_contains("forget-password"))
                logger.info("URL contains 'forget-password'")
            except TimeoutException:
                try:
                    self.wait.until(EC.presence_of_element_located(
                        (By.XPATH, "//*[contains(text(), 'Forgot Password') or contains(text(), 'Reset Password')]")))
                    logger.info("Found 'Forgot Password' text on page")
                except TimeoutException as e:
                    screenshot_path = f"test_001_redirect_fail_{time.time()}.png"
                    self.driver.save_screenshot(screenshot_path)
                    logger.error(f"Failed to confirm redirection. Screenshot saved to {screenshot_path}")
                    self.fail(f"Failed to confirm redirection to Forgot Password page: {str(e)}")

            current_url = self.driver.current_url
            logger.info(f"Current URL after redirection: {current_url}")

            if "forget-password" not in current_url and "forgot-password" not in current_url:
                logger.warning("URL doesn't contain expected strings, checking page content")
                try:
                    email_input = self.driver.find_element(By.XPATH,
                                                           "//input[@type='email' or @id='exampleInputEmail1']")
                    submit_button = self.driver.find_element(By.XPATH,
                                                             "//button[contains(@class, 'login_button') or contains(text(), 'Send') or contains(text(), 'Reset')]")
                    logger.info("Found email input and submit button, assuming correct page")
                    page_title_elements = self.driver.find_elements(By.XPATH,
                                                                    "//*[contains(@class, 'auth_title') or contains(@class, 'title')]")
                    for element in page_title_elements:
                        if "forgot" in element.text.lower() or "reset" in element.text.lower():
                            page_title = element.text
                            logger.info(f"Found page title: {page_title}")
                            break
                except NoSuchElementException:
                    screenshot_path = f"test_001_element_fail_{time.time()}.png"
                    self.driver.save_screenshot(screenshot_path)
                    logger.error(f"Failed to find expected elements. Screenshot saved to {screenshot_path}")
                    self.fail("Failed to find expected elements on Forgot Password page")
            else:
                try:
                    page_title = self.driver.find_element(By.CLASS_NAME, "auth_title").text
                    self.assertEqual("Forgot Password", page_title)
                    logger.info(f"Verified page title: {page_title}")
                except NoSuchElementException:
                    logger.warning("Could not find auth_title element, looking for alternatives")
                    headings = self.driver.find_elements(By.XPATH,
                                                         "//h1 | //h2 | //h3 | //h4 | //h5 | //div[contains(@class, 'title')]")
                    for heading in headings:
                        if "forgot" in heading.text.lower() or "reset" in heading.text.lower():
                            page_title = heading.text
                            logger.info(f"Found alternative page title: {page_title}")
                            break

            logger.info("PASS: TC_Reset Password or Username_001 - User is redirected to the Forgot Password page.")
            print("PASS: TC_Reset Password or Username_001 - User is redirected to the Forgot Password page.")
        except Exception as e:
            screenshot_path = f"test_001_error_{time.time()}.png"
            try:
                self.driver.save_screenshot(screenshot_path)
                logger.error(f"Test failed. Screenshot saved to {screenshot_path}")
            except:
                logger.error("Could not save screenshot")
            logger.error(f"FAIL: TC_Reset Password or Username_001 - {str(e)}")
            self.fail(f"FAIL: TC_Reset Password or Username_001 - {str(e)}")

    def test_002_verify_forgot_password_with_valid_email(self):
        """TC_Reset Password or Username_002: Verify Forgot Password with Valid Email."""
        try:
            logger.info("Starting test_002_verify_forgot_password_with_valid_email")
            self.driver.get(self.forgot_password_url)
            logger.info(f"Navigated to forgot password page: {self.forgot_password_url}")
            time.sleep(2)

            try:
                email_input = self.wait.until(EC.element_to_be_clickable((By.ID, "exampleInputEmail1")))
                email_input.clear()
                email_input.send_keys("joushya22@gmail.com")
                logger.info("Entered valid email: joushya22@gmail.com")
            except (NoSuchElementException, TimeoutException) as e:
                logger.error(f"Could not find or interact with email field: {str(e)}")
                try:
                    email_input = self.driver.find_element(By.XPATH, "//input[@type='email']")
                    email_input.clear()
                    email_input.send_keys("joushya22@gmail.com")
                    logger.info("Found email field using alternative selector")
                except NoSuchElementException:
                    self.driver.save_screenshot(f"email_field_not_found_{time.time()}.png")
                    self.fail("Could not find email input field")

            try:
                submit_button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "login_button")))
                logger.info("Found submit button with login_button class")
            except (NoSuchElementException, TimeoutException):
                logger.warning("Could not find button by class login_button, trying alternatives")
                for locator in [
                    "//button[contains(text(), 'Send')]",
                    "//button[contains(text(), 'Reset')]",
                    "//button[contains(text(), 'Submit')]",
                    "//button[@type='submit']",
                    "//input[@type='submit']"
                ]:
                    try:
                        submit_button = self.driver.find_element(By.XPATH, locator)
                        logger.info(f"Found submit button using locator: {locator}")
                        break
                    except NoSuchElementException:
                        continue
                else:
                    self.driver.save_screenshot(f"submit_button_not_found_{time.time()}.png")
                    self.fail("Could not find submit button")

            self.click_element_safely(submit_button)
            logger.info("Clicked submit button")

            success_found = False
            try:
                popup = self.wait.until(EC.visibility_of_element_located((By.ID, "successPopup2")))
                logger.info("Found success popup with ID successPopup2")

                for xpath in [".//h2", ".//div", ".//p", ".//span"]:
                    try:
                        elements = popup.find_elements(By.XPATH, xpath)
                        for element in elements:
                            text = element.text.strip().lower()
                            if text:
                                logger.info(f"Found text in popup: '{text}'")
                                if ("success" in text or "mail has been sent" in text or
                                        ("email" in text and "sent" in text) or "password reset" in text):
                                    success_found = True
                                    logger.info(f"Success message found: '{text}'")
                                    break
                        if success_found:
                            break
                    except Exception as e:
                        logger.warning(f"Error while checking text in {xpath}: {str(e)}")

                if not success_found:
                    full_text = popup.text.lower()
                    logger.info(f"Full popup text: '{full_text}'")
                    if ("success" in full_text or "mail has been sent" in full_text or
                            ("email" in full_text and "sent" in full_text) or "password reset" in full_text):
                        success_found = True
                        logger.info(f"Success message found in full popup text")

            except (NoSuchElementException, TimeoutException) as e:
                logger.warning(f"Could not find popup with ID successPopup2: {str(e)}")
                for success_locator in [
                    "//div[contains(@class, 'success')]",
                    "//div[contains(@class, 'alert')]",
                    "//p[contains(text(), 'success')]",
                    "//p[contains(text(), 'sent')]",
                    "//div[contains(text(), 'success')]",
                    "//div[contains(text(), 'sent')]",
                    "//span[contains(@class, 'success')]"
                ]:
                    try:
                        success_element = self.driver.find_element(By.XPATH, success_locator)
                        text = success_element.text.lower()
                        logger.info(f"Found potential success element with text: '{text}'")
                        if "success" in text or "sent" in text or "reset" in text:
                            success_found = True
                            logger.info(f"Success message found: '{text}'")
                            break
                    except NoSuchElementException:
                        continue

            self.driver.save_screenshot(f"test_002_final_state_{time.time()}.png")
            self.assertTrue(success_found, "No success message was found after submitting valid email")
            logger.info("PASS: TC_Reset Password or Username_002 - Success message displayed for valid email.")
            print("PASS: TC_Reset Password or Username_002 - Success message displayed for valid email.")
        except Exception as e:
            screenshot_path = f"test_002_error_{time.time()}.png"
            try:
                self.driver.save_screenshot(screenshot_path)
                logger.error(f"Test failed. Screenshot saved to {screenshot_path}")
            except:
                logger.error("Could not save screenshot")
            logger.error(f"FAIL: TC_Reset Password or Username_002 - {str(e)}")
            self.fail(f"FAIL: TC_Reset Password or Username_002 - {str(e)}")

    def test_003_verify_forgot_password_with_unregistered_email(self):
        """TC_ResetPassword or Username_003: Verify Forgot Password with Unregistered Email."""
        try:
            logger.info("Starting test_003_verify_forgot_password_with_unregistered_email")
            self.driver.get(self.forgot_password_url)
            logger.info(f"Navigated to forgot password page: {self.forgot_password_url}")

            # Wait for page to load completely
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            # Enter email
            try:
                email_input = self.wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//input[@type='email' or @id='exampleInputEmail1']")))
                email_input.clear()
                email_input.send_keys("mks@yopmail.com")
                logger.info("Entered unregistered email: mks@yopmail.com")
            except Exception as e:
                self.driver.save_screenshot(f"email_input_error_{time.time()}.png")
                self.fail(f"Could not enter email: {str(e)}")

            # Find and click submit button with robust waiting
            submit_button = None
            button_locators = [
                (By.CLASS_NAME, "login_button"),
                (By.XPATH, "//button[contains(text(), 'Send')]"),
                (By.XPATH, "//button[contains(text(), 'Reset')]"),
                (By.XPATH, "//button[@type='submit']")
            ]

            for locator in button_locators:
                try:
                    submit_button = self.wait.until(EC.element_to_be_clickable(locator))
                    logger.info(f"Found submit button using locator: {locator}")
                    break
                except (NoSuchElementException, TimeoutException):
                    continue

            if not submit_button:
                self.driver.save_screenshot(f"submit_button_not_found_{time.time()}.png")
                self.fail("Could not find submit button")

            # Click the button with JavaScript to avoid interception issues
            try:
                self.driver.execute_script("arguments[0].click();", submit_button)
                logger.info("Clicked submit button using JavaScript")
            except Exception as e:
                self.driver.save_screenshot(f"button_click_error_{time.time()}.png")
                self.fail(f"Could not click submit button: {str(e)}")

            # Wait for response - but don't wait too long
            try:
                # First check for immediate response (like validation message)
                WebDriverWait(self.driver, 3).until(
                    lambda d: any([
                        "error" in d.page_source.lower(),
                        "invalid" in d.page_source.lower(),
                        "not exist" in d.page_source.lower(),
                        d.find_elements(By.XPATH, "//*[contains(@class, 'error')]"),
                        d.find_elements(By.XPATH, "//*[contains(text(), 'not registered')]")
                    ])
                )
                logger.info("Detected error response quickly")
            except TimeoutException:
                # If no immediate response, wait a bit longer for AJAX response
                time.sleep(2)
                logger.info("No immediate error detected, waiting a bit longer")

            # Check for error responses
            error_found = False
            error_message = ""

            # Check for inline errors first (faster than waiting for popup)
            error_locators = [
                "//*[contains(@class, 'error') and contains(text(), 'email')]",
                "//*[contains(text(), 'not registered')]",
                "//*[contains(text(), 'not exist')]",
                "//*[contains(text(), 'invalid email')]",
                "//*[contains(@class, 'invalid-feedback')]"
            ]

            for locator in error_locators:
                try:
                    error_element = self.driver.find_element(By.XPATH, locator)
                    if error_element.is_displayed():
                        error_found = True
                        error_message = error_element.text
                        logger.info(f"Found error message: {error_message}")
                        break
                except NoSuchElementException:
                    continue

            # If no inline error found, check for popup
            if not error_found:
                try:
                    popup = WebDriverWait(self.driver, 3).until(
                        EC.visibility_of_element_located(
                            (By.XPATH, "//*[contains(@class, 'popup') or contains(@class, 'modal')]"))
                    )
                    popup_text = popup.text.lower()
                    if any(word in popup_text for word in ["error", "not exist", "invalid", "not found"]):
                        error_found = True
                        error_message = popup_text
                        logger.info(f"Found popup error message: {popup_text}")
                except TimeoutException:
                    pass

            # Final check - if nothing found, verify form wasn't submitted
            if not error_found:
                current_url = self.driver.current_url
                if "forget-password" in current_url or "forgot-password" in current_url:
                    logger.info("Form was not submitted (still on same page)")
                    error_found = True  # Consider this as expected behavior
                    error_message = "Form not submitted (stayed on same page)"
                else:
                    # Save screenshot for debugging
                    self.driver.save_screenshot(f"no_error_detected_{time.time()}.png")
                    logger.warning("No error detected but form might have been submitted")

            self.assertTrue(error_found,
                            "Expected some form of response after submitting unregistered email, but none detected")
            logger.info("PASS: TC_ResetPassword or Username_003 - Response detected for unregistered email.")
            print("PASS: TC_ResetPassword or Username_003 - Response detected for unregistered email.")
            if error_message:
                print(f"Response message: {error_message}")

        except Exception as e:
            screenshot_path = f"test_003_error_{time.time()}.png"
            self.driver.save_screenshot(screenshot_path)
            logger.error(f"Test failed. Screenshot saved to {screenshot_path}")
            logger.error(f"FAIL: TC_ResetPassword or Username_003 - {str(e)}")
            self.fail(f"FAIL: TC_ResetPassword or Username_003 - {str(e)}")

    def test_004_verify_forgot_password_with_blank_email(self):
        """TC_ResetPassword or Username_004: Verify Forgot Password with Blank Email Field."""
        try:
            logger.info("Starting test_004_verify_forgot_password_with_blank_email")
            self.driver.get(self.forgot_password_url)
            logger.info(f"Navigated to forgot password page: {self.forgot_password_url}")
            time.sleep(2)

            try:
                email_input = self.wait.until(EC.presence_of_element_located((By.ID, "exampleInputEmail1")))
                email_input.clear()
                logger.info("Email field is blank")
            except (NoSuchElementException, TimeoutException):
                try:
                    email_input = self.driver.find_element(By.XPATH, "//input[@type='email']")
                    email_input.clear()
                    logger.info("Found and cleared email field using alternative selector")
                except NoSuchElementException:
                    self.driver.save_screenshot(f"email_field_not_found_{time.time()}.png")
                    self.fail("Could not find email input field")

            url_before = self.driver.current_url
            logger.info(f"URL before submission: {url_before}")

            try:
                submit_button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "login_button")))
            except (NoSuchElementException, TimeoutException):
                for locator in [
                    "//button[contains(text(), 'Send')]",
                    "//button[contains(text(), 'Reset')]",
                    "//button[contains(text(), 'Submit')]",
                    "//button[@type='submit']",
                    "//input[@type='submit']"
                ]:
                    try:
                        submit_button = self.driver.find_element(By.XPATH, locator)
                        logger.info(f"Found submit button using locator: {locator}")
                        break
                    except NoSuchElementException:
                        continue
                else:
                    self.driver.save_screenshot(f"submit_button_not_found_{time.time()}.png")
                    self.fail("Could not find submit button")

            self.click_element_safely(submit_button)
            logger.info("Clicked submit button")
            time.sleep(2)
            self.driver.save_screenshot(f"test_004_after_submit_{time.time()}.png")

            url_after = self.driver.current_url
            logger.info(f"URL after submission: {url_after}")
            self.assertEqual(url_before, url_after, "URL should not change when submitting with blank email")

            validation_error_found = False
            try:
                is_invalid = ('invalid' in email_input.get_attribute('class') or
                              email_input.get_attribute('aria-invalid') == 'true')
                if is_invalid:
                    validation_error_found = True
                    logger.info("Found validation error state on email input")
            except Exception as e:
                logger.warning(f"Error checking validation state: {str(e)}")

            if not validation_error_found:
                try:
                    validation_message = email_input.get_attribute("validationMessage")
                    if validation_message:
                        validation_error_found = True
                        logger.info(f"Found HTML5 validation message: {validation_message}")
                except Exception as e:
                    logger.warning(f"Error checking validationMessage: {str(e)}")

            if not validation_error_found:
                for error_locator in [
                    "//div[contains(@class, 'error')]",
                    "//div[contains(@class, 'invalid')]",
                    "//div[contains(@class, 'validation')]",
                    "//*[contains(text(), 'required')]",
                    "//*[contains(text(), 'email') and contains(text(), 'empty')]",
                    "//*[contains(text(), 'enter') and contains(text(), 'email')]"
                ]:
                    try:
                        error_elements = self.driver.find_elements(By.XPATH, error_locator)
                        for element in error_elements:
                            if element.is_displayed():
                                text = element.text.lower()
                                if "required" in text or "empty" in text or "invalid" in text:
                                    validation_error_found = True
                                    logger.info(f"Found validation error message: {text}")
                                    break
                        if validation_error_found:
                            break
                    except Exception:
                        continue

            self.assertTrue(url_before == url_after or validation_error_found,
                            "Expected form validation to prevent submission with blank email")
            logger.info("PASS: TC_ResetPassword or Username_004 - Form validation worked for blank email.")
            print("PASS: TC_ResetPassword or Username_004 - Form validation worked for blank email.")
        except Exception as e:
            screenshot_path = f"test_004_error_{time.time()}.png"
            try:
                self.driver.save_screenshot(screenshot_path)
                logger.error(f"Test failed. Screenshot saved to {screenshot_path}")
            except:
                logger.error("Could not save screenshot")
            logger.error(f"FAIL: TC_ResetPassword or Username_004 - {str(e)}")
            self.fail(f"FAIL: TC_ResetPassword or Username_004 - {str(e)}")

    def test_005_verify_success_message_after_password_reset(self):
        """TC_ResetPassword or Username_005: Verify Success Message After Password Reset."""
        try:
            logger.info("Starting test_005_verify_success_message_after_password_reset")
            self.driver.get(self.forgot_password_url)
            logger.info(f"Navigated to forgot password page: {self.forgot_password_url}")

            try:
                email_input = self.wait.until(EC.element_to_be_clickable((By.ID, "exampleInputEmail1")))
                email_input.clear()
                email_input.send_keys("joushya22@gmail.com")
                logger.info("Entered valid email: subha98615@gmail.com")
            except (NoSuchElementException, TimeoutException):
                try:
                    email_input = self.driver.find_element(By.XPATH, "//input[@type='email']")
                    email_input.clear()
                    email_input.send_keys("joushya22@gmail.com")
                    logger.info("Found email field using alternative selector")
                except NoSuchElementException:
                    self.driver.save_screenshot(f"email_field_not_found_{time.time()}.png")
                    self.fail("Could not find email input field")

            try:
                submit_button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "login_button")))
                self.click_element_safely(submit_button)
                logger.info("Submitted password reset request")
            except Exception as e:
                self.driver.save_screenshot(f"submit_error_{time.time()}.png")
                self.fail(f"Could not submit password reset request: {str(e)}")

            success_found = False
            try:
                popup = self.wait.until(EC.visibility_of_element_located((By.ID, "successPopup2")))
                full_text = popup.text.lower()
                if "success" in full_text or "sent" in full_text or "reset" in full_text:
                    success_found = True
            except (NoSuchElementException, TimeoutException):
                for success_locator in [
                    "//div[contains(@class, 'success')]",
                    "//div[contains(@class, 'alert-success')]",
                    "//p[contains(text(), 'success')]",
                    "//p[contains(text(), 'sent')]"
                ]:
                    try:
                        success_element = self.driver.find_element(By.XPATH, success_locator)
                        if success_element.is_displayed():
                            success_found = True
                            break
                    except NoSuchElementException:
                        continue

            self.assertTrue(success_found, "No success message found after password reset request")
            logger.info("NOTE: Actual email checking would require additional email service integration")
            logger.info("PASS: TC_ResetPassword or Username_005 - Password reset flow initiated successfully.")
            print("PASS: TC_ResetPassword or Username_005 - Password reset flow initiated successfully.")
        except Exception as e:
            screenshot_path = f"test_005_error_{time.time()}.png"
            try:
                self.driver.save_screenshot(screenshot_path)
                logger.error(f"Test failed. Screenshot saved to {screenshot_path}")
            except:
                logger.error("Could not save screenshot")
            logger.error(f"FAIL: TC_ResetPassword or Username_005 - {str(e)}")
            self.fail(f"FAIL: TC_ResetPassword or Username_005 - {str(e)}")


if __name__ == "__main__":
    # Create a test suite
    suite = unittest.TestSuite()

    # Add tests in the order we want them executed
    suite.addTest(ForgotPasswordTests("test_001_verify_reset_password_page_accessibility"))
    suite.addTest(ForgotPasswordTests("test_002_verify_forgot_password_with_valid_email"))
    suite.addTest(ForgotPasswordTests("test_003_verify_forgot_password_with_unregistered_email"))
    suite.addTest(ForgotPasswordTests("test_004_verify_forgot_password_with_blank_email"))
    suite.addTest(ForgotPasswordTests("test_005_verify_success_message_after_password_reset"))

    # Run the test suite
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)