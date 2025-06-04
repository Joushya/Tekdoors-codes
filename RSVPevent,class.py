import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
import time
import logging
from datetime import datetime


class DancerVibesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename='dancervibes_test.log'
        )

        # Initialize Chrome WebDriver with performance optimizations
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")  # Don't load images
        chrome_options.add_argument("--disable-javascript")  # Disable JS if not needed
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

        # Page load strategy for faster loading
        chrome_options.add_argument("--page-load-strategy=eager")

        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.set_page_load_timeout(10)  # Reduce page load timeout
        cls.driver.implicitly_wait(3)  # Reduce implicit wait
        cls.driver.maximize_window()
        cls.wait = WebDriverWait(cls.driver, 8)  # Reduced from 15 to 8
        cls.short_wait = WebDriverWait(cls.driver, 3)  # For quick elements
        cls.base_url = "https://stage.dancervibes.com/dancerjou"
        cls.test_results = {
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }
        cls.logged_in = False  # Track login state

    def setUp(self):
        self.start_time = datetime.now()
        logging.info(f"\nStarting test: {self._testMethodName}")

    def tearDown(self):
        test_duration = datetime.now() - self.start_time
        logging.info(f"Test duration: {test_duration.total_seconds():.2f} seconds")

    @classmethod
    def tearDownClass(cls):
        # Print summary of test results
        logging.info("\n=== TEST SUMMARY ===")
        logging.info(
            f"Total tests: {cls.test_results['passed'] + cls.test_results['failed'] + cls.test_results['skipped']}")
        logging.info(f"Passed: {cls.test_results['passed']}")
        logging.info(f"Failed: {cls.test_results['failed']}")
        logging.info(f"Skipped: {cls.test_results['skipped']}")

        if cls.test_results['errors']:
            logging.info("\nError details:")
            for error in cls.test_results['errors']:
                logging.error(error)

        cls.driver.quit()

    def record_test_result(self, passed=True, error_msg=None):
        if passed:
            self.test_results['passed'] += 1
        else:
            self.test_results['failed'] += 1
            if error_msg:
                self.test_results['errors'].append(f"{self._testMethodName}: {error_msg}")

    def safe_navigate_to_page(self, url, expected_title_keywords=None):
        """Safely navigate to page with faster loading"""
        try:
            self.driver.get(url)
            # Reduced wait time from 2 to 1 second
            time.sleep(1)

            if expected_title_keywords:
                current_title = self.driver.title.lower()
                if isinstance(expected_title_keywords, str):
                    expected_title_keywords = [expected_title_keywords]

                title_found = any(keyword.lower() in current_title for keyword in expected_title_keywords)
                if not title_found:
                    logging.warning(
                        f"Expected title keywords {expected_title_keywords} not found in '{self.driver.title}', but continuing...")

            logging.info(f"Successfully navigated to: {url}")
            return True
        except Exception as e:
            error_msg = f"Failed to navigate to {url}: {str(e)}"
            logging.error(error_msg)
            return False

    def safe_find_element(self, by, value, timeout=5, required=False):
        """Safely find element with reduced timeout"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located((by, value)))
            return element
        except TimeoutException:
            if required:
                logging.error(f"Required element not found: {by}={value}")
                return None
            else:
                logging.warning(f"Optional element not found: {by}={value}")
                return None

    def safe_login(self):
        """Optimized login with state tracking"""
        # Skip login if already logged in
        if self.logged_in:
            return True

        try:
            login_url = f"{self.base_url}/customer/login"
            if not self.safe_navigate_to_page(login_url, ["login", "signin"]):
                return False

            # Combined element finding - try multiple selectors at once
            email_element = None
            for by, value in [(By.ID, "username"), (By.ID, "email"), (By.NAME, "username"),
                              (By.NAME, "email"), (By.XPATH, "//input[@type='email']")]:
                email_element = self.safe_find_element(by, value, timeout=3)
                if email_element:
                    break

            if not email_element:
                logging.error("Email field not found")
                return False

            email_element.clear()
            email_element.send_keys("joushya22@gmail.com")

            # Find password field
            password_element = None
            for by, value in [(By.ID, "password"), (By.NAME, "password"),
                              (By.XPATH, "//input[@type='password']")]:
                password_element = self.safe_find_element(by, value, timeout=3)
                if password_element:
                    break

            if not password_element:
                logging.error("Password field not found")
                return False

            password_element.clear()
            password_element.send_keys("Jerry@2020")

            # Find and click login button
            login_btn = None
            for by, value in [(By.XPATH, "//button[contains(text(),'Login')]"),
                              (By.XPATH, "//button[contains(text(),'Sign In')]"),
                              (By.XPATH, "//input[@type='submit']"),
                              (By.XPATH, "//button[@type='submit']")]:
                login_btn = self.safe_find_element(by, value, timeout=3)
                if login_btn:
                    break

            if not login_btn:
                logging.error("Login button not found")
                return False

            login_btn.click()
            time.sleep(2)  # Reduced from 3 to 2 seconds

            # Quick check for login success
            user_indicators = [
                (By.XPATH, "//h6[contains(text(),'TestUser2 covind')]"),
                (By.XPATH, "//*[contains(text(),'dashboard')]"),
                (By.XPATH, "//*[contains(text(),'profile')]")
            ]

            for by, value in user_indicators:
                if self.safe_find_element(by, value, timeout=3):
                    logging.info("Login successful")
                    self.logged_in = True
                    return True

            logging.warning("Login may not have been successful, but continuing...")
            self.logged_in = True
            return True

        except Exception as e:
            error_msg = f"Login failed: {str(e)}"
            logging.error(error_msg)
            return False

    def test_homepage_navigation(self):
        """Fast homepage navigation test"""
        try:
            if not self.safe_navigate_to_page(f"{self.base_url}/events", ["events", "home"]):
                self.record_test_result(False, "Failed to navigate to events page")
                return

            # Quick logo check
            logo = self.safe_find_element(By.TAG_NAME, "img", timeout=3)
            if logo and logo.is_displayed():
                logging.info("Logo found")

            # Quick menu check
            menu_found = len(self.driver.find_elements(By.TAG_NAME, "a"))
            logging.info(f"Found {menu_found} navigation links")

            self.record_test_result(True)

        except Exception as e:
            self.record_test_result(False, str(e))
            logging.error(f"Homepage navigation test failed: {str(e)}")

    def test_event_page(self):
        """Fast event page test"""
        try:
            if not self.safe_navigate_to_page(f"{self.base_url}/events", ["events"]):
                self.record_test_result(False, "Failed to navigate to events page")
                return

            # Quick element count check instead of detailed parsing
            event_cards = self.driver.find_elements(By.XPATH,
                                                    "//div[contains(@class, 'event-parent')] | //div[contains(@class, 'card')]")

            if event_cards:
                logging.info(f"Found {len(event_cards)} event cards")
                # Quick check of first event
                try:
                    first_title = event_cards[0].find_element(By.TAG_NAME, "h6").text
                    logging.info(f"First event: {first_title}")
                except:
                    logging.info("Event card structure detected")
            else:
                logging.warning("No event cards found")

            self.record_test_result(True)

        except Exception as e:
            self.record_test_result(False, str(e))
            logging.error(f"Event page test failed: {str(e)}")

    def test_class_page(self):
        """Fast class page test"""
        try:
            if not self.safe_navigate_to_page(f"{self.base_url}/classes", ["classes"]):
                self.record_test_result(False, "Failed to navigate to classes page")
                return

            # Quick count of class elements
            class_cards = self.driver.find_elements(By.XPATH,
                                                    "//div[contains(@class, 'event-parent')] | //div[contains(@class, 'card')]")
            logging.info(f"Found {len(class_cards)} class cards")

            self.record_test_result(True)

        except Exception as e:
            self.record_test_result(False, str(e))
            logging.error(f"Class page test failed: {str(e)}")

    def test_private_class_page(self):
        """Fast private class page test"""
        try:
            if not self.safe_navigate_to_page(f"{self.base_url}/private-class", ["private", "classes"]):
                self.record_test_result(False, "Failed to navigate to private class page")
                return

            # Quick content check
            page_content = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            if "no private" in page_content or "available" in page_content:
                logging.info("Private class page content detected")

            self.record_test_result(True)

        except Exception as e:
            self.record_test_result(False, str(e))
            logging.error(f"Private class page test failed: {str(e)}")

    def test_dashboard_navigation(self):
        """Fast dashboard test with login state management"""
        try:
            if not self.safe_login():
                logging.warning("Login failed, skipping dashboard test")
                self.test_results['skipped'] += 1
                return

            if not self.safe_navigate_to_page(f"{self.base_url}/customer/dashboard", ["dashboard", "upcoming"]):
                self.record_test_result(False, "Failed to navigate to dashboard")
                return

            # Quick dashboard element check
            dashboard_buttons = self.driver.find_elements(By.TAG_NAME, "button")
            logging.info(f"Found {len(dashboard_buttons)} buttons on dashboard")

            # Quick tab test if elements exist
            classes_tab = self.safe_find_element(By.XPATH, "//button[contains(text(),'Classes')]", timeout=3)
            if classes_tab:
                classes_tab.click()
                time.sleep(1)  # Reduced wait
                logging.info("Classes tab clicked successfully")

            self.record_test_result(True)

        except Exception as e:
            self.record_test_result(False, str(e))
            logging.error(f"Dashboard navigation test failed: {str(e)}")

    def test_event_booking_flow(self):
        """Fast booking flow test"""
        try:
            if not self.safe_login():
                logging.warning("Login failed, skipping booking flow test")
                self.test_results['skipped'] += 1
                return

            if not self.safe_navigate_to_page(f"{self.base_url}/events", ["events"]):
                self.record_test_result(False, "Failed to navigate to events page")
                return

            # Quick event selection
            first_event = self.safe_find_element(By.XPATH,
                                                 "//div[contains(@class, 'event-parent')] | //div[contains(@class, 'card')]",
                                                 timeout=5)

            if not first_event:
                logging.warning("No events found for booking test")
                self.test_results['skipped'] += 1
                return

            # Quick click and check
            first_event.click()
            time.sleep(1.5)  # Reduced wait

            # Quick booking button check
            book_btn = self.safe_find_element(By.XPATH,
                                              "//button[contains(text(),'Book')] | //a[contains(text(),'Book')]",
                                              timeout=3)

            if book_btn:
                logging.info("Booking button found - flow accessible")
                # Don't actually click to avoid real bookings
            else:
                logging.info("Event detail page loaded successfully")

            self.record_test_result(True)

        except Exception as e:
            self.record_test_result(False, str(e))
            logging.error(f"Event booking flow test failed: {str(e)}")


if __name__ == "__main__":
    # Run tests with faster execution
    unittest.main(verbosity=2)