"""Demo/mock templates for testing without an API key.

Provides realistic pre-built test outputs so users can see
the tool in action without spending money on API calls.
"""


DEMO_PLAYWRIGHT_LOGIN = '''import pytest
from playwright.sync_api import Page, expect


class TestLoginHappyPath:
    """Happy path tests for login functionality."""

    def test_login_with_valid_credentials(self, page: Page):
        """Verify user can log in with valid email and password."""
        page.goto("{url}")
        page.get_by_label("Email").fill("user@test.com")
        page.get_by_label("Password").fill("ValidPass123!")
        page.get_by_role("button", name="Sign In").click()
        expect(page).to_have_url("{url}/dashboard")

    def test_login_with_remember_me(self, page: Page):
        """Verify Remember Me checkbox persists session."""
        page.goto("{url}")
        page.get_by_label("Email").fill("user@test.com")
        page.get_by_label("Password").fill("ValidPass123!")
        page.get_by_label("Remember me").check()
        page.get_by_role("button", name="Sign In").click()
        expect(page).to_have_url("{url}/dashboard")


class TestLoginNegative:
    """Negative tests for login functionality."""

    def test_login_with_invalid_password(self, page: Page):
        """Verify error message when password is incorrect."""
        page.goto("{url}")
        page.get_by_label("Email").fill("user@test.com")
        page.get_by_label("Password").fill("wrongpassword")
        page.get_by_role("button", name="Sign In").click()
        expect(page.get_by_text("Invalid credentials")).to_be_visible()

    def test_login_with_empty_fields(self, page: Page):
        """Verify form validation when all fields are empty."""
        page.goto("{url}")
        page.get_by_role("button", name="Sign In").click()
        expect(page.get_by_text("Email is required")).to_be_visible()

    def test_login_with_malformed_email(self, page: Page):
        """Verify validation rejects malformed email addresses."""
        page.goto("{url}")
        page.get_by_label("Email").fill("not-an-email")
        page.get_by_label("Password").fill("ValidPass123!")
        page.get_by_role("button", name="Sign In").click()
        expect(page.get_by_text("Enter a valid email")).to_be_visible()


class TestLoginEdgeCases:
    """Edge case tests for login functionality."""

    def test_login_with_sql_injection_attempt(self, page: Page):
        """Verify login is safe from SQL injection."""
        page.goto("{url}")
        page.get_by_label("Email").fill("' OR 1=1 --")
        page.get_by_label("Password").fill("anything")
        page.get_by_role("button", name="Sign In").click()
        expect(page).to_have_url("{url}")

    def test_login_with_xss_payload(self, page: Page):
        """Verify login sanitises XSS payloads."""
        page.goto("{url}")
        page.get_by_label("Email").fill("<script>alert('xss')</script>")
        page.get_by_label("Password").fill("test")
        page.get_by_role("button", name="Sign In").click()
        expect(page.get_by_text("Invalid credentials")).to_be_visible()

    def test_rapid_login_attempts_rate_limited(self, page: Page):
        """Verify brute force protection after multiple failed attempts."""
        page.goto("{url}")
        for _ in range(6):
            page.get_by_label("Email").fill("user@test.com")
            page.get_by_label("Password").fill("wrong")
            page.get_by_role("button", name="Sign In").click()
        expect(page.get_by_text("Too many attempts")).to_be_visible()


class TestLoginBoundary:
    """Boundary value tests for login functionality."""

    def test_login_with_max_length_email(self, page: Page):
        """Verify handling of maximum length email (254 chars)."""
        long_email = "a" * 243 + "@test.com"
        page.goto("{url}")
        page.get_by_label("Email").fill(long_email)
        page.get_by_label("Password").fill("ValidPass123!")
        page.get_by_role("button", name="Sign In").click()
        expect(page.get_by_text("Invalid credentials")).to_be_visible()

    def test_login_with_minimum_password(self, page: Page):
        """Verify validation for password below minimum length."""
        page.goto("{url}")
        page.get_by_label("Email").fill("user@test.com")
        page.get_by_label("Password").fill("Ab1!")
        page.get_by_role("button", name="Sign In").click()
        expect(page.get_by_text("Password too short")).to_be_visible()
'''

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
        page.get_by_label("Full Name").fill("Test User n")
        page.get_by_label("Email").fill("unicode@test.com")
        page.get_by_label("Password").fill("SecurePass123!")
        page.get_by_label("Confirm Password").fill("SecurePass123!")
        page.get_by_role("button", name="Register").click()
        expect(page.get_by_text("Registration successful")).to_be_visible()

    def test_register_with_xss_in_name(self, page: Page):
        """Verify registration sanitises XSS in name field."""
        page.goto("{url}")
        page.get_by_label("Full Name").fill("<script>alert('xss')</script>")
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

DEMO_GHERKIN_LOGIN = '''Feature: User Login
  As a registered user
  I want to log in to my account
  So that I can access the application dashboard

  Background:
    Given I am on the login page at "{url}"

  @happy-path
  Scenario: Successful login with valid credentials
    When I enter "user@test.com" in the email field
    And I enter "ValidPass123!" in the password field
    And I click the "Sign In" button
    Then I should be redirected to the dashboard

  @happy-path
  Scenario: Login with remember me enabled
    When I enter "user@test.com" in the email field
    And I enter "ValidPass123!" in the password field
    And I check the "Remember me" checkbox
    And I click the "Sign In" button
    Then I should be redirected to the dashboard
    And my session should persist after closing the browser

  @negative
  Scenario Outline: Login with invalid credentials
    When I enter "<email>" in the email field
    And I enter "<password>" in the password field
    And I click the "Sign In" button
    Then I should see an error message "<error>"

    Examples:
      | email             | password       | error                |
      | user@test.com     | wrongpassword  | Invalid credentials  |
      | nobody@test.com   | SomePass123!   | Invalid credentials  |
      | not-an-email      | ValidPass123!  | Enter a valid email  |

  @negative
  Scenario: Login with empty fields
    When I leave all fields empty
    And I click the "Sign In" button
    Then I should see an error message "Email is required"

  @edge-case @security
  Scenario: SQL injection attempt in email field
    When I enter "' OR 1=1 --" in the email field
    And I enter "anything" in the password field
    And I click the "Sign In" button
    Then I should remain on the login page

  @edge-case @security
  Scenario: XSS attempt in email field
    When I enter "<script>alert('xss')</script>" in the email field
    And I enter "test" in the password field
    And I click the "Sign In" button
    Then the script should not execute

  @edge-case @security
  Scenario: Brute force protection
    When I attempt to login 6 times with incorrect passwords
    Then I should see a rate limiting message "Too many attempts"

  @boundary
  Scenario: Login with maximum length email
    When I enter a 254-character email address
    And I enter "ValidPass123!" in the password field
    And I click the "Sign In" button
    Then the system should handle the input without crashing

  @boundary
  Scenario: Login with minimum length password
    When I enter "user@test.com" in the email field
    And I enter "Ab1!" in the password field
    And I click the "Sign In" button
    Then I should see an error message "Password too short"
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

  @negative
  Scenario Outline: Registration with invalid inputs
    When I enter "<name>" in the full name field
    And I enter "<email>" in the email field
    And I enter "<password>" in the password field
    And I enter "<confirm>" in the confirm password field
    And I click the "Register" button
    Then I should see an error message "<error>"

    Examples:
      | name      | email            | password       | confirm        | error                |
      |           | user@test.com    | SecurePass123! | SecurePass123! | Name is required     |
      | Test User | not-an-email     | SecurePass123! | SecurePass123! | Enter a valid email  |
      | Test User | user@test.com    | weak           | weak           | Password too weak    |

  @edge-case @security
  Scenario: XSS attempt in name field
    When I enter "<script>alert('xss')</script>" in the full name field
    And I enter "xss@test.com" in the email field
    And I enter "SecurePass123!" in the password field
    And I enter "SecurePass123!" in the confirm password field
    And I click the "Register" button
    Then the script should not execute

  @edge-case
  Scenario: Registration with unicode name
    When I enter "Test User n" in the full name field
    And I enter "unicode@test.com" in the email field
    And I enter "SecurePass123!" in the password field
    And I enter "SecurePass123!" in the confirm password field
    And I click the "Register" button
    Then I should see "Registration successful"

  @boundary
  Scenario: Registration with single character name
    When I enter "A" in the full name field
    And I enter "short@test.com" in the email field
    And I enter "SecurePass123!" in the password field
    And I enter "SecurePass123!" in the confirm password field
    And I click the "Register" button
    Then I should see an error message "Name too short"

  @boundary
  Scenario: Registration with maximum length email
    When I enter "Test User" in the full name field
    And I enter a 254-character email address
    And I enter "SecurePass123!" in the password field
    And I enter "SecurePass123!" in the confirm password field
    And I click the "Register" button
    Then the system should handle the input without crashing
'''


def _detect_feature(url: str = "", description: str = "") -> str:
    """Detect what type of feature is being tested based on keywords."""
    text = (url + " " + description).lower()
    if any(kw in text for kw in ["login", "sign in", "signin", "auth"]):
        return "login"
    elif any(kw in text for kw in ["register", "signup", "sign up", "create account"]):
        return "registration"
    return "login"  # Default fallback


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
    target_url = url or "https://example.com"

    templates = {
        ("playwright", "login"): DEMO_PLAYWRIGHT_LOGIN,
        ("playwright", "registration"): DEMO_PLAYWRIGHT_REGISTRATION,
        ("gherkin", "login"): DEMO_GHERKIN_LOGIN,
        ("gherkin", "registration"): DEMO_GHERKIN_REGISTRATION,
    }

    template = templates.get((format, feature), DEMO_PLAYWRIGHT_LOGIN)
    return template.format(url=target_url)
