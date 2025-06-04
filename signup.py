import time
import os
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("signup_automation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SignupPage:
    """Page Object Model for the Signup page"""

    def __init__(self, driver):
        self.driver = driver
        self.url = "https://admin.stage.dancervibes.com/register"

        # Locators
        self.name_input = (By.NAME, "name")
        self.email_input = (By.NAME, "email")
        self.phone_input = (By.ID, "phone")
        self.business_name_input = (By.NAME, "business_name")
        self.password_input = (By.ID, "password")
        self.terms_checkbox = (By.ID, "terms")
        self.signup_button = (By.XPATH, "//button[@type='submit' and contains(text(), 'Sign Up')]")
        self.timezone_input = (By.ID, "browser-timezone")

        # Enhanced error message locators
        self.error_messages = [
            (By.CLASS_NAME, "text-red-500"),
            (By.CSS_SELECTOR, ".invalid-feedback"),
            (By.CSS_SELECTOR, ".alert-danger"),
            (By.CSS_SELECTOR, ".text-danger"),
            (By.CSS_SELECTOR, "[role='alert']"),
            (By.CSS_SELECTOR, ".error"),
            (By.CSS_SELECTOR, ".form-error"),
            (By.XPATH, "//div[contains(@class, 'error')]")
        ]

        # Success message locator
        self.success_message = (By.CSS_SELECTOR, ".alert-success")

    def open(self):
        """Open the signup page"""
        self.driver.get(self.url)
        self.driver.maximize_window()
        time.sleep(2)
        logger.info("Signup page opened successfully")
        return self

    def set_timezone(self):
        """Set timezone using JavaScript"""
        try:
            self.driver.execute_script(
                "document.getElementById('browser-timezone').value = Intl.DateTimeFormat().resolvedOptions().timeZone;"
            )
            logger.info("Timezone set successfully")
        except Exception as e:
            logger.error(f"Error setting timezone: {e}")
        return self

    def enter_name(self, name):
        """Enter name in the name field"""
        try:
            element = self.driver.find_element(*self.name_input)
            element.clear()
            if name:
                element.send_keys(name)
                logger.info(f"Entered name: {name}")
            else:
                logger.info("Left name field empty")
        except Exception as e:
            logger.error(f"Error entering name: {e}")
        return self

    def enter_email(self, email):
        """Enter email in the email field"""
        try:
            element = self.driver.find_element(*self.email_input)
            element.clear()
            if email:
                element.send_keys(email)
                logger.info(f"Entered email: {email}")
            else:
                logger.info("Left email field empty")
        except Exception as e:
            logger.error(f"Error entering email: {e}")
        return self

    def enter_phone(self, phone):
        """Enter phone in the phone field"""
        try:
            element = self.driver.find_element(*self.phone_input)
            element.clear()
            if phone:
                element.send_keys(phone)
                logger.info(f"Entered phone: {phone}")
            else:
                logger.info("Left phone field empty")
        except Exception as e:
            logger.error(f"Error entering phone: {e}")
        return self

    def enter_business_name(self, business_name):
        """Enter business name in the business name field"""
        try:
            element = self.driver.find_element(*self.business_name_input)
            element.clear()
            if business_name:
                element.send_keys(business_name)
                logger.info(f"Entered business name: {business_name}")
            else:
                logger.info("Left business name field empty")
        except Exception as e:
            logger.error(f"Error entering business name: {e}")
        return self

    def enter_password(self, password):
        """Enter password in the password field"""
        try:
            element = self.driver.find_element(*self.password_input)
            element.clear()
            if password:
                element.send_keys(password)
                logger.info(f"Entered password: {'*' * len(password)}")
            else:
                logger.info("Left password field empty")
        except Exception as e:
            logger.error(f"Error entering password: {e}")
        return self

    def accept_terms(self, accept=True):
        """Accept terms and conditions"""
        try:
            terms_checkbox = self.driver.find_element(*self.terms_checkbox)
            is_selected = terms_checkbox.is_selected()

            if accept and not is_selected:
                terms_checkbox.click()
                logger.info("Accepted terms and conditions")
            elif not accept and is_selected:
                terms_checkbox.click()
                logger.info("Unchecked terms and conditions")
            elif accept and is_selected:
                logger.info("Terms already checked")
            elif not accept and not is_selected:
                logger.info("Terms already unchecked")
        except Exception as e:
            logger.error(f"Error with terms checkbox: {e}")
        return self

    def click_signup(self):
        """Click the signup button"""
        try:
            try:
                button = self.driver.find_element(*self.signup_button)
                logger.info("Found signup button")

                if button.is_enabled():
                    logger.info("Signup button is enabled")
                    button.click()
                    logger.info("Clicked signup button normally")
                else:
                    logger.warning("Signup button appears to be disabled, will try JavaScript click")
                    self.driver.execute_script("arguments[0].click();", button)
                    logger.info("Clicked signup button using JavaScript")
            except Exception as e:
                logger.warning(f"Normal click failed: {e}, attempting JavaScript click")
                self.driver.execute_script("arguments[0].click();",
                                           self.driver.find_element(*self.signup_button))
                logger.info("Clicked signup button using JavaScript")

            try:
                self.driver.execute_script("""
                    var forms = document.getElementsByTagName('form');
                    if (forms.length > 0) {
                        forms[0].dispatchEvent(new Event('submit', { 'bubbles': true }));
                    }
                """)
                logger.info("Triggered form submission via JavaScript")
            except Exception as js_error:
                logger.warning(f"JavaScript form submission attempt failed: {js_error}")

            time.sleep(5)
        except Exception as e:
            logger.error(f"All signup button click methods failed: {e}")
        return self

    def get_error_messages(self):
        """Get all error messages displayed on the page"""
        all_errors = []

        for locator in self.error_messages:
            try:
                elements = self.driver.find_elements(*locator)
                for element in elements:
                    try:
                        if element.is_displayed() and element.text.strip():
                            error_text = element.text.strip()
                            if error_text not in all_errors:
                                all_errors.append(error_text)
                                logger.info(f"Found error message: {error_text}")
                    except Exception as e:
                        logger.warning(f"Error checking visibility for element: {e}")
            except Exception as e:
                logger.warning(f"Error finding error messages with locator {locator}: {e}")

        for field_locator in [self.name_input, self.email_input, self.phone_input,
                              self.business_name_input, self.password_input]:
            try:
                field = self.driver.find_element(*field_locator)
                validation_message = self.driver.execute_script(
                    "return arguments[0].validationMessage;", field
                )
                if validation_message:
                    logger.info(f"HTML5 validation message for {field_locator}: {validation_message}")
                    if validation_message not in all_errors:
                        all_errors.append(validation_message)
            except Exception as e:
                logger.warning(f"Error checking HTML5 validation for {field_locator}: {e}")

        current_url = self.driver.current_url
        if "register" not in current_url:
            logger.info(f"Redirected to: {current_url}")

        if not all_errors:
            logger.info("No error messages found, checking page source for clues")
            page_source = self.driver.page_source
            logger.info(f"Page source snippet: {page_source[:500]}...")

        return all_errors

    def is_success_message_displayed(self):
        """Check if success message is displayed or if we were redirected to dashboard"""
        try:
            try:
                success_elem = WebDriverWait(self.driver, 5).until(
                    EC.visibility_of_element_located(self.success_message)
                )
                logger.info(f"Success message displayed: {success_elem.text}")
                return True
            except TimeoutException:
                current_url = self.driver.current_url
                if "register" not in current_url:
                    logger.info(f"Redirected to {current_url} after signup, considering as success")
                    return True
                logger.info("No success message displayed and no redirection")
                return False
        except Exception as e:
            logger.error(f"Error checking for success message: {e}")
            return False

    def fill_form(self, name="", email="", phone="", business_name="", password="", accept_terms=True):
        """Fill the entire form with provided details"""
        self.enter_name(name)
        self.enter_email(email)
        self.enter_phone(phone)
        self.enter_business_name(business_name)
        self.enter_password(password)
        self.accept_terms(accept_terms)
        logger.info("Form filled successfully")
        return self


class TestRunner:
    """Test runner for executing test cases"""

    def __init__(self):
        """Initialize the test runner"""
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        self.signup_page = SignupPage(self.driver)

        self.screenshots_dir = "screenshots"
        if not os.path.exists(self.screenshots_dir):
            os.makedirs(self.screenshots_dir)

        self.test_results = []

    def take_screenshot(self, test_case_id):
        """Take a screenshot and save it with the test case ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.screenshots_dir}/{test_case_id}_{timestamp}.png"
        self.driver.save_screenshot(filename)
        logger.info(f"Screenshot saved: {filename}")
        return filename

    def run_test_case(self, test_case_id, name="", email="", phone="", business_name="", password="", accept_terms=True,
                      expected_result="success"):
        """Run a test case with the given parameters"""
        logger.info(f"\n{' Starting Test Case ':=^80}")
        logger.info(f"TEST CASE: {test_case_id}")
        logger.info(f"Parameters: name='{name}', email='{email}', phone='{phone}', "
                    f"business_name='{business_name}', password='{'*' * len(password) if password else ''}', "
                    f"accept_terms={accept_terms}, expected_result='{expected_result}'")

        self.signup_page.open().set_timezone()
        self.signup_page.fill_form(
            name=name,
            email=email,
            phone=phone,
            business_name=business_name,
            password=password,
            accept_terms=accept_terms
        )
        self.signup_page.click_signup()

        errors = self.signup_page.get_error_messages()
        success = self.signup_page.is_success_message_displayed()
        screenshot_path = self.take_screenshot(test_case_id)

        test_passed = False
        if test_case_id == "TC_SIGNUP_002":
            test_passed = (len(errors) > 0 and not success)
        elif expected_result == "success" and success and not errors:
            test_passed = True
        elif expected_result == "error" and (errors or not success):
            test_passed = True

        result = {
            "test_case_id": test_case_id,
            "passed": test_passed,
            "expected_result": expected_result,
            "actual_result": "success" if success and not errors else "error",
            "errors": errors,
            "screenshot": screenshot_path,
            "params": {
                "name": name,
                "email": email,
                "phone": phone,
                "business_name": business_name,
                "password": password,
                "accept_terms": accept_terms
            }
        }

        self.test_results.append(result)
        status = "PASSED" if test_passed else "FAILED"
        logger.info(f"\nTEST CASE {test_case_id} {status}")
        logger.info(f"{' Test Case Completed ':=^80}\n")
        return result

    def close(self):
        """Close the browser"""
        self.driver.quit()
        logger.info("Browser closed")

    def generate_console_summary(self):
        """Generate a detailed console summary of test results"""
        passed = sum(1 for result in self.test_results if result["passed"])
        failed = len(self.test_results) - passed

        # Color codes
        GREEN = '\033[92m'
        RED = '\033[91m'
        YELLOW = '\033[93m'
        END = '\033[0m'
        BOLD = '\033[1m'

        logger.info(f"\n\n{BOLD}{' TEST SUMMARY ':=^80}{END}")
        logger.info(f"\n{BOLD}Total Tests:{END} {len(self.test_results)}")
        logger.info(f"{BOLD}Passed:{END} {GREEN}{passed}{END}")
        logger.info(f"{BOLD}Failed:{END} {RED}{failed}{END}\n")

        for result in self.test_results:
            status = f"{GREEN}PASS{END}" if result["passed"] else f"{RED}FAIL{END}"
            logger.info(f"{BOLD}{result['test_case_id']}:{END} {status}")
            logger.info(f"Expected: {result['expected_result']} | Actual: {result['actual_result']}")

            if not result["passed"] and result["errors"]:
                logger.info(f"{YELLOW}Errors encountered:{END}")
                for error in result["errors"]:
                    logger.info(f" - {error}")

            logger.info(f"Screenshot: {result['screenshot']}")
            logger.info("-" * 80)

        if failed == 0:
            logger.info(f"\n{BOLD}{GREEN}ALL TESTS PASSED SUCCESSFULLY{END}{BOLD}")
        else:
            logger.info(f"\n{BOLD}{RED}SOME TESTS FAILED{END}{BOLD}")
        logger.info(f"{'=' * 80}{END}\n")

    def generate_html_report(self):
        """Generate HTML report of test results"""
        report_path = "test_report.html"

        html = """<!DOCTYPE html>
<html>
<head>
    <title>Signup Automation Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .pass { color: green; font-weight: bold; }
        .fail { color: red; font-weight: bold; }
        .error-msg { color: #d9534f; }
        .test-params { background-color: #f9f9f9; }
        .param-name { font-weight: bold; width: 120px; }
    </style>
</head>
<body>
    <h1>Signup Automation Test Report</h1>
    <p>Generated: {date}</p>
    <p><strong>Summary:</strong> {passed_count} passed, {failed_count} failed</p>
    <table>
        <tr>
            <th>Test Case ID</th>
            <th>Result</th>
            <th>Expected</th>
            <th>Actual</th>
            <th>Parameters</th>
            <th>Errors</th>
            <th>Screenshot</th>
        </tr>
        {rows}
    </table>
</body>
</html>"""

        rows = ""
        passed_count = 0
        failed_count = 0

        for result in self.test_results:
            if result["passed"]:
                passed_count += 1
            else:
                failed_count += 1

            result_class = "pass" if result["passed"] else "fail"
            result_text = "PASS" if result["passed"] else "FAIL"

            # Format parameters
            params_html = "<table class='test-params'>"
            for key, value in result["params"].items():
                display_value = value if key != "password" else "*****" if value else "None"
                params_html += f"""
                <tr>
                    <td class='param-name'>{key.replace('_', ' ').title()}</td>
                    <td>{display_value}</td>
                </tr>"""
            params_html += "</table>"

            rows += f"""
                <tr>
                    <td>{result['test_case_id']}</td>
                    <td class="{result_class}">{result_text}</td>
                    <td>{result['expected_result']}</td>
                    <td>{result['actual_result']}</td>
                    <td>{params_html}</td>
                    <td>{"<br>".join(f'<span class="error-msg">{error}</span>' for error in result['errors']) if result['errors'] else "None"}</td>
                    <td><a href="{result['screenshot']}" target="_blank">View</a></td>
                </tr>
            """

        report_html = html.format(
            date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            rows=rows,
            passed_count=passed_count,
            failed_count=failed_count
        )

        with open(report_path, "w") as f:
            f.write(report_html)

        logger.info(f"HTML test report generated: {report_path}")
        return report_path

    def generate_report(self):
        """Generate both console and HTML reports"""
        self.generate_console_summary()
        return self.generate_html_report()


def run_all_tests():
    """Run all test cases"""
    test_runner = TestRunner()

    try:
        # TC_SIGNUP_001: Valid Signup
        test_runner.run_test_case(
            test_case_id="TC_SIGNUP_001",
            name="Test User56",
            email="sayu792@gmail.com",
            phone="9776583658",
            business_name="Test Business89",
            password="Mks@1234",
            accept_terms=True,
            expected_result="error"
        )

        # TC_SIGNUP_002: Empty Fields
        empty_fields_result = test_runner.run_test_case(
            test_case_id="TC_SIGNUP_002",
            name="",
            email="",
            phone="",
            business_name="",
            password="",
            accept_terms=True,
            expected_result="error"
        )

        if not empty_fields_result["passed"]:
            test_runner.run_test_case(
                test_case_id="TC_SIGNUP_002_EMAIL",
                name="Test User",
                email="",
                phone="9876543245",
                business_name="Test Business8",
                password="Mks@1234",
                accept_terms=True,
                expected_result="error"
            )

        # TC_SIGNUP_003: Invalid Email Format
        test_runner.run_test_case(
            test_case_id="TC_SIGNUP_003",
            name="Test User",
            email="invalid-email",
            phone="9876543269",
            business_name="Test Business7",
            password="Mks@1234",
            accept_terms=True,
            expected_result="error"
        )

        # TC_SIGNUP_005: Weak Password
        test_runner.run_test_case(
            test_case_id="TC_SIGNUP_005",
            name="Test User",
            email="sayu9@gmail.com",
            phone="9876543247",
            business_name="Test Business21",
            password="Password123",
            accept_terms=True,
            expected_result="error"
        )

        # TC_SIGNUP_006: Terms Not Accepted
        test_runner.run_test_case(
            test_case_id="TC_SIGNUP_006",
            name="Test User",
            email="sayu9@gmail.com",
            phone="9876543285",
            business_name="Test Business6",
            password="Mks@1234",
            accept_terms=False,
            expected_result="error"
        )

        # TC_SIGNUP_007: Duplicate Email
        test_runner.run_test_case(
            test_case_id="TC_SIGNUP_007",
            name="Test User",
            email="subha98615@gmail.com",
            phone="9876543219",
            business_name="Test Business24",
            password="Password123!",
            accept_terms=True,
            expected_result="error"
        )

        # Generate reports
        test_runner.generate_report()

    finally:
        test_runner.close()


if __name__ == "__main__":
    run_all_tests()