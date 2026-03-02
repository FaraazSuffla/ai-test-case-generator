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

The `--demo` flag lets you run the full tool using built-in templates — no API key or spending required:

```bash
# Generate Playwright tests in demo mode
py generate_tests.py --demo --url https://example.com/login --format playwright

# Generate Gherkin feature file in demo mode
py generate_tests.py --demo --describe "User registration with email and password" --format gherkin

# Try different features — the tool detects login vs registration automatically
py generate_tests.py --demo --describe "sign up page" --format playwright

# Generate tests WITH an HTML coverage report (opens in browser)
py generate_tests.py --demo --url https://example.com/login --format playwright --report
```

Demo mode produces the same structured output as the real AI — it's perfect for seeing the tool in action, understanding the output format, or demonstrating the project in interviews.

### Check the Output

Generated files are saved to the `output/` directory:

```bash
# List all generated files
ls output/

# View a generated test file
cat output/test_example_com_login_playwright.py

# Open the HTML report in your browser (Windows)
start output/report_https___example_com_login.html

# Open the HTML report (macOS)
open output/report_https___example_com_login.html

# Open the HTML report (Linux)
xdg-open output/report_https___example_com_login.html
```

```
output/
├── test_example_com_login_playwright.py
├── example_com_login.feature
├── test_sign_up_page_playwright.py
└── report_https___example_com_login.html   ← HTML report (with --report flag)
```

### Full Mode (With API Key)

For AI-generated tests tailored to any page or feature:

```bash
# Set your API key
export ANTHROPIC_API_KEY="your-key-here"
# OR
export OPENAI_API_KEY="your-key-here"

# Generate Playwright tests from a URL
py generate_tests.py --url https://example.com/login --format playwright

# Generate Gherkin feature files from a URL
py generate_tests.py --url https://example.com/login --format gherkin

# Generate tests from a feature description
py generate_tests.py --describe "User registration with email and password" --format playwright

# Use OpenAI instead of Claude
py generate_tests.py --url https://example.com --format gherkin --provider openai

# Analyze page accessibility tree for context-aware tests
py generate_tests.py --url https://example.com/login --format playwright --analyze

# Generate tests with an HTML coverage report
py generate_tests.py --url https://example.com/login --format playwright --report

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
py generate_tests.py --demo --url https://example.com/login --format playwright --report

# Step 2: Open the report in your browser (Windows)
start output/report_https___example_com_login.html
```

The report includes:

- **Test metadata** — source URL, format, provider, timestamp
- **Coverage dashboard** — total test count with category breakdown cards
- **Test case table** — every test listed with name, category badge, and description
- **Full generated code** — collapsible code block with the complete test file
- **Dark theme** — responsive, self-contained HTML with no external dependencies

The report auto-opens in your default browser on generation. If it doesn't, open it manually with `start output/report_*.html` (Windows) or `open output/report_*.html` (macOS).

## Example: AI-Generated vs Hand-Written Tests

### Hand-Written Login Test (typical junior approach)

```python
from playwright.sync_api import sync_playwright

def test_login():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://example.com/login")
        page.fill("#email", "user@test.com")
        page.fill("#password", "password123")
        page.click("#submit")
        assert page.url == "https://example.com/dashboard"
        browser.close()
```

**Coverage: 1 test, happy path only.**

### AI-Generated Login Tests (from this tool)

```python
import pytest
from playwright.sync_api import Page, expect


class TestLoginHappyPath:
    """Happy path tests for login functionality."""

    def test_login_with_valid_credentials(self, page: Page):
        """Verify user can log in with valid email and password."""
        page.goto("https://example.com/login")
        page.get_by_label("Email").fill("user@test.com")
        page.get_by_label("Password").fill("ValidPass123!")
        page.get_by_role("button", name="Sign In").click()
        expect(page).to_have_url("https://example.com/dashboard")

    def test_login_redirects_to_original_page(self, page: Page):
        """Verify user is redirected to the page they came from after login."""
        page.goto("https://example.com/settings")
        page.get_by_label("Email").fill("user@test.com")
        page.get_by_label("Password").fill("ValidPass123!")
        page.get_by_role("button", name="Sign In").click()
        expect(page).to_have_url("https://example.com/settings")


class TestLoginNegative:
    """Negative tests for login functionality."""

    def test_login_with_invalid_password(self, page: Page):
        """Verify error message when password is incorrect."""
        page.goto("https://example.com/login")
        page.get_by_label("Email").fill("user@test.com")
        page.get_by_label("Password").fill("wrongpassword")
        page.get_by_role("button", name="Sign In").click()
        expect(page.get_by_text("Invalid credentials")).to_be_visible()

    def test_login_with_unregistered_email(self, page: Page):
        """Verify error when email is not registered."""
        page.goto("https://example.com/login")
        page.get_by_label("Email").fill("nobody@test.com")
        page.get_by_label("Password").fill("SomePass123!")
        page.get_by_role("button", name="Sign In").click()
        expect(page.get_by_text("Invalid credentials")).to_be_visible()

    def test_login_with_empty_fields(self, page: Page):
        """Verify form validation when fields are empty."""
        page.goto("https://example.com/login")
        page.get_by_role("button", name="Sign In").click()
        expect(page.get_by_text("Email is required")).to_be_visible()


class TestLoginEdgeCases:
    """Edge case tests for login functionality."""

    def test_login_with_sql_injection_attempt(self, page: Page):
        """Verify login is safe from SQL injection."""
        page.goto("https://example.com/login")
        page.get_by_label("Email").fill("' OR 1=1 --")
        page.get_by_label("Password").fill("anything")
        page.get_by_role("button", name="Sign In").click()
        expect(page).to_have_url("https://example.com/login")

    def test_login_with_xss_attempt(self, page: Page):
        """Verify login sanitises XSS payloads."""
        page.goto("https://example.com/login")
        page.get_by_label("Email").fill("<script>alert('xss')</script>")
        page.get_by_label("Password").fill("test")
        page.get_by_role("button", name="Sign In").click()
        expect(page.locator("script")).to_have_count(0)

    def test_rapid_login_attempts_rate_limited(self, page: Page):
        """Verify brute force protection after multiple failed attempts."""
        page.goto("https://example.com/login")
        for _ in range(6):
            page.get_by_label("Email").fill("user@test.com")
            page.get_by_label("Password").fill("wrong")
            page.get_by_role("button", name="Sign In").click()
        expect(page.get_by_text("Too many attempts")).to_be_visible()


class TestLoginBoundary:
    """Boundary value tests for login functionality."""

    def test_login_with_max_length_email(self, page: Page):
        """Verify login handles maximum length email (254 chars)."""
        long_email = "a" * 243 + "@test.com"  # 254 chars total
        page.goto("https://example.com/login")
        page.get_by_label("Email").fill(long_email)
        page.get_by_label("Password").fill("ValidPass123!")
        page.get_by_role("button", name="Sign In").click()
        expect(page.get_by_text("Invalid credentials")).to_be_visible()

    def test_login_with_minimum_password(self, page: Page):
        """Verify login with minimum acceptable password length."""
        page.goto("https://example.com/login")
        page.get_by_label("Email").fill("user@test.com")
        page.get_by_label("Password").fill("Ab1!")
        page.get_by_role("button", name="Sign In").click()
        expect(page.get_by_text("Password too short")).to_be_visible()
```

**Coverage: 10 tests across 4 categories — happy path, negative, edge cases, and boundary values.**

The AI-generated tests use modern Playwright best practices (role-based selectors, `expect` assertions), cover security concerns (SQL injection, XSS, rate limiting), and test boundary values that manual testing often misses.

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
