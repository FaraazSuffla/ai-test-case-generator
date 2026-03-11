"""Demo/mock templates for testing without an API key.

Provides realistic pre-built test outputs so users can see
the tool in action without spending money on API calls.

Default demo target: https://practicetestautomation.com/practice-test-login/
Valid credentials: student / Password123
"""

# ---------------------------------------------------------------------------
# Practice Test Automation — Login (https://practicetestautomation.com)
# ---------------------------------------------------------------------------

DEMO_PLAYWRIGHT_LOGIN = '''import re
import pytest
from playwright.sync_api import Page, expect


BASE_URL = "{url}"


class TestLoginHappyPath:
    """Happy path tests for login functionality."""

    def test_successful_login_with_valid_credentials(self, page: Page):
        """Verify user can log in with valid username and password."""
        page.goto(BASE_URL)
        page.locator("#username").fill("student")
        page.locator("#password").fill("Password123")
        page.locator("#submit").click()
        expect(page).to_have_url(re.compile(".*logged-in-successfully.*"))

    def test_successful_login_shows_congratulations(self, page: Page):
        """Verify logged-in page contains success message."""
        page.goto(BASE_URL)
        page.locator("#username").fill("student")
        page.locator("#password").fill("Password123")
        page.locator("#submit").click()
        expect(page.locator(".post-title")).to_contain_text("Logged In Successfully")

    def test_successful_login_displays_logout_button(self, page: Page):
        """Verify Log out button is visible after successful login."""
        page.goto(BASE_URL)
        page.locator("#username").fill("student")
        page.locator("#password").fill("Password123")
        page.locator("#submit").click()
        expect(page.get_by_role("link", name="Log out")).to_be_visible()

    def test_logout_after_successful_login(self, page: Page):
        """Verify user can log out and return to the main page."""
        page.goto(BASE_URL)
        page.locator("#username").fill("student")
        page.locator("#password").fill("Password123")
        page.locator("#submit").click()
        page.get_by_role("link", name="Log out").click()
        expect(page).to_have_url(BASE_URL)


class TestLoginNegative:
    """Negative tests for login functionality."""

    def test_login_with_invalid_username(self, page: Page):
        """Verify error message when username is incorrect."""
        page.goto(BASE_URL)
        page.locator("#username").fill("incorrectUser")
        page.locator("#password").fill("Password123")
        page.locator("#submit").click()
        expect(page.locator("#error")).to_be_visible()
        expect(page.locator("#error")).to_contain_text("Your username is invalid!")

    def test_login_with_invalid_password(self, page: Page):
        """Verify error message when password is incorrect."""
        page.goto(BASE_URL)
        page.locator("#username").fill("student")
        page.locator("#password").fill("incorrectPassword")
        page.locator("#submit").click()
        expect(page.locator("#error")).to_be_visible()
        expect(page.locator("#error")).to_contain_text("Your password is invalid!")

    def test_login_with_empty_username(self, page: Page):
        """Verify error when username field is left empty."""
        page.goto(BASE_URL)
        page.locator("#password").fill("Password123")
        page.locator("#submit").click()
        expect(page.locator("#error")).to_be_visible()
        expect(page.locator("#error")).to_contain_text("Your username is invalid!")

    def test_login_with_empty_password(self, page: Page):
        """Verify error when password field is left empty."""
        page.goto(BASE_URL)
        page.locator("#username").fill("student")
        page.locator("#submit").click()
        expect(page.locator("#error")).to_be_visible()
        expect(page.locator("#error")).to_contain_text("Your password is invalid!")

    def test_login_with_both_fields_empty(self, page: Page):
        """Verify error when both fields are empty."""
        page.goto(BASE_URL)
        page.locator("#submit").click()
        expect(page.locator("#error")).to_be_visible()


class TestLoginEdgeCases:
    """Edge case tests for login functionality."""

    def test_login_with_sql_injection_in_username(self, page: Page):
        """Verify login is safe from SQL injection in username."""
        page.goto(BASE_URL)
        page.locator("#username").fill("\\' OR 1=1 --")
        page.locator("#password").fill("anything")
        page.locator("#submit").click()
        expect(page.locator("#error")).to_be_visible()
        expect(page).not_to_have_url(re.compile(".*logged-in-successfully.*"))

    def test_login_with_xss_payload_in_username(self, page: Page):
        """Verify login sanitises XSS payloads in username."""
        page.goto(BASE_URL)
        page.locator("#username").fill("<script>alert(\\'xss\\')</script>")
        page.locator("#password").fill("test")
        page.locator("#submit").click()
        expect(page.locator("#error")).to_be_visible()

    def test_login_with_case_sensitive_username(self, page: Page):
        """Verify username is case-sensitive (Student != student)."""
        page.goto(BASE_URL)
        page.locator("#username").fill("Student")
        page.locator("#password").fill("Password123")
        page.locator("#submit").click()
        expect(page.locator("#error")).to_be_visible()

    def test_login_with_case_sensitive_password(self, page: Page):
        """Verify password is case-sensitive (password123 != Password123)."""
        page.goto(BASE_URL)
        page.locator("#username").fill("student")
        page.locator("#password").fill("password123")
        page.locator("#submit").click()
        expect(page.locator("#error")).to_be_visible()

    def test_login_with_whitespace_username(self, page: Page):
        """Verify login rejects username with leading/trailing spaces."""
        page.goto(BASE_URL)
        page.locator("#username").fill("  student  ")
        page.locator("#password").fill("Password123")
        page.locator("#submit").click()
        expect(page.locator("#error")).to_be_visible()


class TestLoginBoundary:
    """Boundary value tests for login functionality."""

    def test_login_with_very_long_username(self, page: Page):
        """Verify system handles extremely long username input."""
        page.goto(BASE_URL)
        page.locator("#username").fill("a" * 500)
        page.locator("#password").fill("Password123")
        page.locator("#submit").click()
        expect(page.locator("#error")).to_be_visible()

    def test_login_with_very_long_password(self, page: Page):
        """Verify system handles extremely long password input."""
        page.goto(BASE_URL)
        page.locator("#username").fill("student")
        page.locator("#password").fill("x" * 500)
        page.locator("#submit").click()
        expect(page.locator("#error")).to_be_visible()

    def test_login_with_single_character_username(self, page: Page):
        """Verify system handles single character username."""
        page.goto(BASE_URL)
        page.locator("#username").fill("a")
        page.locator("#password").fill("Password123")
        page.locator("#submit").click()
        expect(page.locator("#error")).to_be_visible()

    def test_login_with_special_characters_in_username(self, page: Page):
        """Verify system handles special characters in username."""
        page.goto(BASE_URL)
        page.locator("#username").fill("!@#$%^&*()")
        page.locator("#password").fill("Password123")
        page.locator("#submit").click()
        expect(page.locator("#error")).to_be_visible()
'''

DEMO_GHERKIN_LOGIN = '''Feature: User Login
  As a registered user
  I want to log in to my account
  So that I can access the logged-in area

  Background:
    Given I am on the login page at "{url}"

  @happy-path
  Scenario: Successful login with valid credentials
    When I enter "student" in the username field
    And I enter "Password123" in the password field
    And I click the Submit button
    Then the URL should contain "logged-in-successfully"
    And I should see the text "Logged In Successfully"
    And I should see a "Log out" link

  @happy-path
  Scenario: Logout after successful login
    When I log in with username "student" and password "Password123"
    And I click the "Log out" link
    Then I should be redirected to the home page

  @negative
  Scenario: Login with invalid username
    When I enter "incorrectUser" in the username field
    And I enter "Password123" in the password field
    And I click the Submit button
    Then I should see an error message "Your username is invalid!"

  @negative
  Scenario: Login with invalid password
    When I enter "student" in the username field
    And I enter "incorrectPassword" in the password field
    And I click the Submit button
    Then I should see an error message "Your password is invalid!"

  @negative
  Scenario: Login with empty username
    When I leave the username field empty
    And I enter "Password123" in the password field
    And I click the Submit button
    Then I should see an error message "Your username is invalid!"

  @negative
  Scenario: Login with empty password
    When I enter "student" in the username field
    And I leave the password field empty
    And I click the Submit button
    Then I should see an error message "Your password is invalid!"

  @negative
  Scenario: Login with both fields empty
    When I leave all fields empty
    And I click the Submit button
    Then I should see an error message

  @edge-case @security
  Scenario: SQL injection attempt in username field
    When I enter "\\' OR 1=1 --" in the username field
    And I enter "anything" in the password field
    And I click the Submit button
    Then I should see an error message
    And the URL should not contain "logged-in-successfully"

  @edge-case @security
  Scenario: XSS attempt in username field
    When I enter "<script>alert(\\'xss\\')</script>" in the username field
    And I enter "test" in the password field
    And I click the Submit button
    Then the script should not execute
    And I should see an error message

  @edge-case
  Scenario: Case-sensitive username check
    When I enter "Student" in the username field
    And I enter "Password123" in the password field
    And I click the Submit button
    Then I should see an error message "Your username is invalid!"

  @edge-case
  Scenario: Case-sensitive password check
    When I enter "student" in the username field
    And I enter "password123" in the password field
    And I click the Submit button
    Then I should see an error message "Your password is invalid!"

  @edge-case
  Scenario: Username with leading and trailing whitespace
    When I enter "  student  " in the username field
    And I enter "Password123" in the password field
    And I click the Submit button
    Then I should see an error message

  @boundary
  Scenario: Very long username input
    When I enter a 500-character string in the username field
    And I enter "Password123" in the password field
    And I click the Submit button
    Then I should see an error message

  @boundary
  Scenario: Very long password input
    When I enter "student" in the username field
    And I enter a 500-character string in the password field
    And I click the Submit button
    Then I should see an error message

  @boundary
  Scenario: Single character username
    When I enter "a" in the username field
    And I enter "Password123" in the password field
    And I click the Submit button
    Then I should see an error message

  @boundary
  Scenario: Special characters in username
    When I enter "!@#$%^&*()" in the username field
    And I enter "Password123" in the password field
    And I click the Submit button
    Then I should see an error message
'''

# ---------------------------------------------------------------------------
# Generic Registration templates (kept for --describe "registration" usage)
# ---------------------------------------------------------------------------

DEMO_PLAYWRIGHT_REGISTRATION = '''import pytest
from playwright.sync_api import Page, expect


class TestRegistrationHappyPath:
    """Happy path tests for user registration."""

    def test_register_with_valid_details(self, page: Page):
        """Verify user can register with valid email and password."""
        page.goto("{url}")
        page.get_by_label("Full Name").fill("Test User")
        page.get_by_label("Email").fill("newuser@test.com")
        page.get_by_label("Password").fill("SecurePass123!")
        page.get_by_label("Confirm Password").fill("SecurePass123!")
        page.get_by_role("button", name="Register").click()
        expect(page.get_by_text("Registration successful")).to_be_visible()

    def test_register_and_receive_confirmation(self, page: Page):
        """Verify confirmation message appears after registration."""
        page.goto("{url}")
        page.get_by_label("Full Name").fill("Test User")
        page.get_by_label("Email").fill("newuser2@test.com")
        page.get_by_label("Password").fill("SecurePass123!")
        page.get_by_label("Confirm Password").fill("SecurePass123!")
        page.get_by_role("button", name="Register").click()
        expect(page.get_by_text("Check your email")).to_be_visible()


class TestRegistrationNegative:
    """Negative tests for user registration."""

    def test_register_with_existing_email(self, page: Page):
        """Verify error when registering with an already-used email."""
        page.goto("{url}")
        page.get_by_label("Full Name").fill("Test User")
        page.get_by_label("Email").fill("existing@test.com")
        page.get_by_label("Password").fill("SecurePass123!")
        page.get_by_label("Confirm Password").fill("SecurePass123!")
        page.get_by_role("button", name="Register").click()
        expect(page.get_by_text("Email already registered")).to_be_visible()

    def test_register_with_mismatched_passwords(self, page: Page):
        """Verify error when passwords do not match."""
        page.goto("{url}")
        page.get_by_label("Full Name").fill("Test User")
        page.get_by_label("Email").fill("newuser@test.com")
        page.get_by_label("Password").fill("SecurePass123!")
        page.get_by_label("Confirm Password").fill("DifferentPass456!")
        page.get_by_role("button", name="Register").click()
        expect(page.get_by_text("Passwords do not match")).to_be_visible()

    def test_register_with_weak_password(self, page: Page):
        """Verify error when password is too weak."""
        page.goto("{url}")
        page.get_by_label("Full Name").fill("Test User")
        page.get_by_label("Email").fill("newuser@test.com")
        page.get_by_label("Password").fill("weak")
        page.get_by_label("Confirm Password").fill("weak")
        page.get_by_role("button", name="Register").click()
        expect(page.get_by_text("Password too weak")).to_be_visible()


class TestRegistrationEdgeCases:
    """Edge case tests for user registration."""

    def test_register_with_unicode_name(self, page: Page):
        """Verify registration handles unicode characters in name."""
        page.goto("{url}")
        page.get_by_label("Full Name").fill("Tëst Üser")
        page.get_by_label("Email").fill("unicode@test.com")
        page.get_by_label("Password").fill("SecurePass123!")
        page.get_by_label("Confirm Password").fill("SecurePass123!")
        page.get_by_role("button", name="Register").click()
        expect(page.get_by_text("Registration successful")).to_be_visible()

    def test_register_with_xss_in_name(self, page: Page):
        """Verify registration sanitises XSS in name field."""
        page.goto("{url}")
        page.get_by_label("Full Name").fill("<script>alert(\\'xss\\')</script>")
        page.get_by_label("Email").fill("xss@test.com")
        page.get_by_label("Password").fill("SecurePass123!")
        page.get_by_label("Confirm Password").fill("SecurePass123!")
        page.get_by_role("button", name="Register").click()
        expect(page.locator("script")).to_have_count(0)


class TestRegistrationBoundary:
    """Boundary value tests for user registration."""

    def test_register_with_single_char_name(self, page: Page):
        """Verify registration with minimum name length."""
        page.goto("{url}")
        page.get_by_label("Full Name").fill("A")
        page.get_by_label("Email").fill("short@test.com")
        page.get_by_label("Password").fill("SecurePass123!")
        page.get_by_label("Confirm Password").fill("SecurePass123!")
        page.get_by_role("button", name="Register").click()
        expect(page.get_by_text("Name too short")).to_be_visible()

    def test_register_with_max_length_email(self, page: Page):
        """Verify registration handles maximum length email."""
        long_email = "a" * 243 + "@test.com"
        page.goto("{url}")
        page.get_by_label("Full Name").fill("Test User")
        page.get_by_label("Email").fill(long_email)
        page.get_by_label("Password").fill("SecurePass123!")
        page.get_by_label("Confirm Password").fill("SecurePass123!")
        page.get_by_role("button", name="Register").click()
        expect(page.locator("body")).to_contain_text("error", timeout=5000)
'''

DEMO_GHERKIN_REGISTRATION = '''Feature: User Registration
  As a new visitor
  I want to create an account
  So that I can access the application

  Background:
    Given I am on the registration page at "{url}"

  @happy-path
  Scenario: Successful registration with valid details
    When I enter "Test User" in the full name field
    And I enter "newuser@test.com" in the email field
    And I enter "SecurePass123!" in the password field
    And I enter "SecurePass123!" in the confirm password field
    And I click the "Register" button
    Then I should see "Registration successful"

  @negative
  Scenario: Registration with existing email
    When I enter "Test User" in the full name field
    And I enter "existing@test.com" in the email field
    And I enter "SecurePass123!" in the password field
    And I enter "SecurePass123!" in the confirm password field
    And I click the "Register" button
    Then I should see an error message "Email already registered"

  @negative
  Scenario: Registration with mismatched passwords
    When I enter "Test User" in the full name field
    And I enter "newuser@test.com" in the email field
    And I enter "SecurePass123!" in the password field
    And I enter "DifferentPass456!" in the confirm password field
    And I click the "Register" button
    Then I should see an error message "Passwords do not match"

  @edge-case @security
  Scenario: XSS attempt in name field
    When I enter "<script>alert(\\'xss\\')</script>" in the full name field
    And I enter "xss@test.com" in the email field
    And I enter "SecurePass123!" in the password field
    And I enter "SecurePass123!" in the confirm password field
    And I click the "Register" button
    Then the script should not execute

  @boundary
  Scenario: Registration with single character name
    When I enter "A" in the full name field
    And I enter "short@test.com" in the email field
    And I enter "SecurePass123!" in the password field
    And I enter "SecurePass123!" in the confirm password field
    And I click the "Register" button
    Then I should see an error message "Name too short"
'''


def _detect_feature(url: str = "", description: str = "") -> str:
    """Detect what type of feature is being tested based on keywords."""
    text = (url + " " + description).lower()
    if any(kw in text for kw in ["registr", "signup", "sign up", "create account"]):
        return "registration"
    # Default to login for login keywords or anything else
    return "login"


def get_demo_output(
    format: str,
    url: str = "",
    description: str = "",
) -> str:
    """Return a pre-built demo test output.

    Args:
        format: 'playwright' or 'gherkin'
        url: Optional URL to insert into templates
        description: Optional feature description

    Returns:
        Generated test code string.
    """
    feature = _detect_feature(url, description)
    target_url = url or "https://practicetestautomation.com/practice-test-login/"

    templates = {
        ("playwright", "login"): DEMO_PLAYWRIGHT_LOGIN,
        ("playwright", "registration"): DEMO_PLAYWRIGHT_REGISTRATION,
        ("gherkin", "login"): DEMO_GHERKIN_LOGIN,
        ("gherkin", "registration"): DEMO_GHERKIN_REGISTRATION,
    }

    template = templates.get((format, feature), DEMO_PLAYWRIGHT_LOGIN)
    return template.format(url=target_url)
