# 🤖 AI Test Case Generator

A Python CLI tool that uses LLMs (Claude or OpenAI) to automatically generate structured test cases from URLs or feature descriptions. Outputs runnable **Playwright test stubs** or **Gherkin `.feature` files** — ready to integrate into your CI/CD pipeline.

## Why This Exists

Manual test case writing is time-consuming and often misses edge cases. This tool leverages AI to generate comprehensive test coverage in seconds, including:

- ✅ **Happy path** tests
- ❌ **Negative** tests
- 🔄 **Edge case** tests
- 📏 **Boundary value** tests
- ♿ **Accessibility** tests (when using URL mode with page analysis)

## Quick Start

### Installation

```bash
git clone https://github.com/FaraazSuffla/ai-test-case-generator.git
cd ai-test-case-generator
```

**For demo mode** (lightweight — no API key needed):

```bash
py -m pip install click rich python-dotenv beautifulsoup4 requests
```

**For full mode** (includes Playwright and AI providers):

```bash
py -m pip install -r requirements.txt
playwright install chromium
```

> **Windows note:** Use `py -m pip install` instead of `pip install` to avoid `ModuleNotFoundError` issues.

### Try It Instantly (No API Key Needed)

The `--demo` flag generates tests using built-in templates — no API key required. Demo mode targets [Practice Test Automation](https://practicetestautomation.com/practice-test-login/) by default, a real login page with known credentials (`student` / `Password123`):

```bash
# Generate 18 Playwright tests for the Practice Test Automation login page
py generate_tests.py --demo --url https://practicetestautomation.com/practice-test-login/ --format playwright

# Generate 16 Gherkin scenarios for the same page
py generate_tests.py --demo --url https://practicetestautomation.com/practice-test-login/ --format gherkin

# Or just run with no URL — defaults to the Practice Test Automation site
py generate_tests.py --demo --format playwright

# Generate tests WITH an HTML coverage report (opens in browser)
py generate_tests.py --demo --url https://practicetestautomation.com/practice-test-login/ --format playwright --report

# Generate registration tests from a description
py generate_tests.py --demo --describe "User registration with email and password" --format gherkin
```

The demo tests use the **actual selectors** (`#username`, `#password`, `#submit`, `#error`) and **real error messages** from the site, so you can install Playwright and run them for real:

```bash
py -m pip install playwright
playwright install chromium
pytest output/test_practicetestautomation_com_practice_test_login_playwright.py -v
```

### Check the Output

Generated files are saved to the `output/` directory:

```bash
# List all generated files
ls output/

# View a generated test file
cat output/test_practicetestautomation_com_practice_test_login_playwright.py

# Open the HTML report in your browser (Windows)
start output/report_practicetestautomation_com_practice_test_login.html

# Open the HTML report (macOS)
open output/report_practicetestautomation_com_practice_test_login.html

# Open the HTML report (Linux)
xdg-open output/report_practicetestautomation_com_practice_test_login.html
```

```
output/
├── test_practicetestautomation_com_practice_test_login_playwright.py
├── practicetestautomation_com_practice_test_login.feature
└── report_practicetestautomation_com_practice_test_login.html   ← HTML report
```

### Full Mode (With API Key)

For AI-generated tests tailored to any page or feature:

```bash
# Set your API key
export ANTHROPIC_API_KEY="your-key-here"
# OR
export OPENAI_API_KEY="your-key-here"

# Generate Playwright tests from a URL
py generate_tests.py --url https://practicetestautomation.com/practice-test-login/ --format playwright

# Generate Gherkin feature files from a URL
py generate_tests.py --url https://practicetestautomation.com/practice-test-login/ --format gherkin

# Generate tests from a feature description
py generate_tests.py --describe "Shopping cart checkout with coupon codes" --format playwright

# Use OpenAI instead of Claude
py generate_tests.py --url https://practicetestautomation.com/practice-test-login/ --format gherkin --provider openai

# Analyze page accessibility tree for context-aware tests
py generate_tests.py --url https://practicetestautomation.com/practice-test-login/ --format playwright --analyze

# Generate tests with an HTML coverage report
py generate_tests.py --url https://practicetestautomation.com/practice-test-login/ --format playwright --report

# View API cost summary
py generate_tests.py --costs
```

## CLI Options

| Flag | Description |
|------|-------------|
| `--url` | URL of the web page to generate tests for |
| `--describe` | Feature description to generate tests from |
| `--format` | Output format: `playwright` or `gherkin` (default: playwright) |
| `--provider` | LLM provider: `anthropic` or `openai` (default: anthropic) |
| `--model` | Specific model to use (overrides provider default) |
| `--analyze` | Extract page accessibility tree for context-aware tests |
| `--demo` | Run with built-in templates — no API key needed |
| `--report` | Generate an HTML coverage report alongside test files |
| `--costs` | Display API usage cost summary |

## HTML Coverage Report

Add `--report` to any command to generate a visual HTML report:

```bash
# Step 1: Generate tests with report
py generate_tests.py --demo --url https://practicetestautomation.com/practice-test-login/ --format playwright --report

# Step 2: Open the report in your browser (Windows)
start output/report_practicetestautomation_com_practice_test_login.html
```

The report includes:

- **Test metadata** — source URL, format, provider, timestamp
- **Coverage dashboard** — total test count with category breakdown cards
- **Test case table** — every test listed with name, category badge, and description
- **Full generated code** — collapsible code block with the complete test file
- **Dark theme** — responsive, self-contained HTML with no external dependencies

The report auto-opens in your default browser on generation. If it doesn't, open it manually with `start output/report_*.html` (Windows) or `open output/report_*.html` (macOS).

## Demo Test Coverage

The demo mode generates **18 Playwright tests** (or **16 Gherkin scenarios**) against the Practice Test Automation login page, covering:

| Category | Tests | What's Covered |
|----------|-------|----------------|
| **Happy Path** | 4 | Valid login, success message, logout button, logout flow |
| **Negative** | 5 | Invalid username, invalid password, empty fields (username, password, both) |
| **Edge Cases** | 5 | SQL injection, XSS payload, case-sensitive username, case-sensitive password, whitespace handling |
| **Boundary** | 4 | Very long username, very long password, single character username, special characters |

All tests use the site's actual selectors and error messages, so they're **runnable** with Playwright — not just stubs.

## Example: AI-Generated vs Hand-Written Tests

### Hand-Written Login Test (typical junior approach)

```python
from playwright.sync_api import sync_playwright

def test_login():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://practicetestautomation.com/practice-test-login/")
        page.fill("#username", "student")
        page.fill("#password", "Password123")
        page.click("#submit")
        assert "logged-in-successfully" in page.url
        browser.close()
```

**Coverage: 1 test, happy path only.**

### AI-Generated Login Tests (from this tool)

```python
import pytest
from playwright.sync_api import Page, expect


BASE_URL = "https://practicetestautomation.com/practice-test-login/"


class TestLoginHappyPath:
    """Happy path tests for login functionality."""

    def test_successful_login_with_valid_credentials(self, page: Page):
        """Verify user can log in with valid username and password."""
        page.goto(BASE_URL)
        page.locator("#username").fill("student")
        page.locator("#password").fill("Password123")
        page.locator("#submit").click()
        expect(page).to_have_url_matching(".*logged-in-successfully.*")

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
        page.locator("#username").fill("' OR 1=1 --")
        page.locator("#password").fill("anything")
        page.locator("#submit").click()
        expect(page.locator("#error")).to_be_visible()

    def test_login_with_case_sensitive_username(self, page: Page):
        """Verify username is case-sensitive (Student != student)."""
        page.goto(BASE_URL)
        page.locator("#username").fill("Student")
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

    def test_login_with_special_characters_in_username(self, page: Page):
        """Verify system handles special characters in username."""
        page.goto(BASE_URL)
        page.locator("#username").fill("!@#$%^&*()")
        page.locator("#password").fill("Password123")
        page.locator("#submit").click()
        expect(page.locator("#error")).to_be_visible()
```

**Coverage: 18 tests across 4 categories — happy path, negative, edge cases, and boundary values.**

The AI-generated tests use the **actual page selectors** (`#username`, `#password`, `#submit`, `#error`), verify the **real error messages** ("Your username is invalid!", "Your password is invalid!"), and cover security concerns (SQL injection, XSS), case sensitivity, and boundary values.

## Project Structure

```
ai-test-case-generator/
├── generate_tests.py          # CLI entry point
├── src/
│   ├── __init__.py
│   ├── analyzer.py            # Page analysis & accessibility tree extraction
│   ├── generator.py           # LLM integration (Claude + OpenAI)
│   ├── demo_templates.py      # Built-in templates for --demo mode
│   ├── report.py              # HTML coverage report generator
│   ├── formatters/
│   │   ├── __init__.py
│   │   ├── playwright_fmt.py  # Playwright test stub formatter
│   │   └── gherkin_fmt.py     # Gherkin .feature file formatter
│   ├── cost_tracker.py        # API usage and cost tracking
│   └── prompts.py             # Prompt templates for test generation
├── output/                    # Generated test files & reports
├── examples/                  # Example outputs
├── requirements.txt
├── .env.example
└── README.md
```

## Cost Tracking

Every API call is logged with token usage and estimated cost:

```bash
$ py generate_tests.py --costs

╭──────────────────── API Cost Summary ────────────────────╮
│ Total requests:    47                                    │
│ Total tokens:      125,340                               │
│ Estimated cost:    $1.23                                 │
│                                                          │
│ Last 7 days:       12 requests · $0.31                   │
│ Provider breakdown:                                      │
│   Claude (claude-sonnet-4-20250514): 38 req · $0.95      │
│   OpenAI (gpt-4o):                    9 req · $0.28      │
╰──────────────────────────────────────────────────────────╯
```

## Tech Stack

- **Python 3.10+** — Core language
- **Anthropic SDK** — Claude API integration
- **OpenAI SDK** — OpenAI API integration
- **Playwright** — Browser automation & page analysis
- **BeautifulSoup4** — HTML parsing
- **Rich** — Beautiful CLI output
- **Click** — CLI framework

## Contributing

Feel free to open issues or submit PRs. Some ideas for future enhancements:

- [ ] Support for Cypress test generation
- [ ] Visual regression test generation
- [ ] Integration with Jira/Azure DevOps for test case import
- [ ] Batch URL processing
- [ ] Custom prompt templates

## License

MIT License — see [LICENSE](LICENSE) for details.
