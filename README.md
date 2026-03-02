# 🤖 AI Test Case Generator

Generate structured **Playwright** or **Gherkin** test cases from any URL or feature description — powered by Claude and OpenAI.

---

## Setup

```bash
git clone https://github.com/FaraazSuffla/ai-test-case-generator.git
cd ai-test-case-generator
py -m pip install click rich python-dotenv beautifulsoup4 requests
```

That's it. You're ready to use demo mode. For full AI mode, also run:

```bash
py -m pip install -r requirements.txt
playwright install chromium
```

> **Troubleshooting:** If you get `ModuleNotFoundError`, use `py -m pip install` instead of `pip install`.

---

## Usage

The tool has two modes: **demo** (built-in templates, no API key) and **full** (AI-generated via Claude or OpenAI).

### Demo Mode

No API key needed. Generates tests against [Practice Test Automation](https://practicetestautomation.com/practice-test-login/), a real login page with known credentials (`student` / `Password123`).

```bash
# Playwright tests
py generate_tests.py --demo --url https://practicetestautomation.com/practice-test-login/ --format playwright

# Gherkin scenarios
py generate_tests.py --demo --url https://practicetestautomation.com/practice-test-login/ --format gherkin

# With HTML coverage report
py generate_tests.py --demo --url https://practicetestautomation.com/practice-test-login/ --format playwright --report

# From a description instead of URL
py generate_tests.py --demo --describe "User registration" --format gherkin
```

Demo tests use the site's **actual selectors** (`#username`, `#password`, `#submit`) and **real error messages**, so they're runnable — not just stubs.

### Full Mode

Set your API key, then point at any URL:

```bash
export ANTHROPIC_API_KEY="your-key"    # or OPENAI_API_KEY

# Claude generates tests from a live page
py generate_tests.py --url https://your-app.com/login --format playwright

# Use OpenAI instead
py generate_tests.py --url https://your-app.com/login --format gherkin --provider openai

# Include accessibility tree analysis
py generate_tests.py --url https://your-app.com/login --format playwright --analyze

# Generate from a description (no URL needed)
py generate_tests.py --describe "Shopping cart with coupon codes" --format playwright
```

### Viewing Results

All files go to the `output/` folder:

```bash
ls output/                          # see what was generated
cat output/test_*.py                # view Playwright tests
cat output/*.feature                # view Gherkin scenarios
start output/report_*.html          # open HTML report (Windows)
open output/report_*.html           # open HTML report (macOS)
```

---

## All CLI Flags

| Flag | Description | Required |
|------|-------------|----------|
| `--url` | URL to generate tests for | One of `--url` or `--describe` |
| `--describe` | Feature description to generate from | One of `--url` or `--describe` |
| `--format` | `playwright` or `gherkin` (default: `playwright`) | No |
| `--demo` | Use built-in templates — no API key needed | No |
| `--report` | Generate HTML coverage report | No |
| `--provider` | `anthropic` or `openai` (default: `anthropic`) | No |
| `--model` | Override the default model | No |
| `--analyze` | Extract accessibility tree for smarter tests | No |
| `--costs` | Show API usage and cost summary | No |

---

## HTML Coverage Report

Add `--report` to any command:

```bash
py generate_tests.py --demo --url https://practicetestautomation.com/practice-test-login/ --format playwright --report
```

Opens a standalone HTML page in your browser with:

- Total test count and category breakdown (happy path, negative, edge cases, boundary)
- Collapsible sections per category with individual test details
- Pass/fail status column (currently shows "Pending" — see note below)
- Export to PDF button
- Full generated code in a collapsible block
- Dark theme, no external dependencies

> **Note on status column:** The report shows tests that were *generated*, not executed. All statuses display as "Pending" because the tool generates test code — it doesn't run them. See the [Roadmap](#roadmap) for planned improvements.

If it doesn't auto-open, run `start output/report_*.html` (Windows) or `open output/report_*.html` (macOS).

---

## What Gets Generated

Every run produces tests across **4 categories**:

| Category | What's Tested | Example |
|----------|---------------|---------|
| ✅ **Happy Path** | Valid inputs, expected flows | Login with correct credentials, verify success page |
| ❌ **Negative** | Invalid inputs, error handling | Wrong password, empty fields, unregistered user |
| 🔄 **Edge Cases** | Security & unusual inputs | SQL injection, XSS payloads, case sensitivity |
| 📏 **Boundary** | Limits & extremes | 500-char username, single character, special characters |

Demo mode generates **18 Playwright tests** or **16 Gherkin scenarios** per run.

---

## Example Output

**What a junior might write:**

```python
def test_login():
    page.goto("https://practicetestautomation.com/practice-test-login/")
    page.fill("#username", "student")
    page.fill("#password", "Password123")
    page.click("#submit")
    assert "logged-in-successfully" in page.url
```

1 test. Happy path only.

**What this tool generates:**

```python
class TestLoginHappyPath:
    def test_successful_login_with_valid_credentials(self, page: Page):
        page.goto(BASE_URL)
        page.locator("#username").fill("student")
        page.locator("#password").fill("Password123")
        page.locator("#submit").click()
        expect(page).to_have_url_matching(".*logged-in-successfully.*")

    def test_successful_login_displays_logout_button(self, page: Page):
        # ... verifies Log out link is visible

class TestLoginNegative:
    def test_login_with_invalid_username(self, page: Page):
        # ... verifies "Your username is invalid!" error

    def test_login_with_invalid_password(self, page: Page):
        # ... verifies "Your password is invalid!" error

class TestLoginEdgeCases:
    def test_login_with_sql_injection_in_username(self, page: Page):
        # ... verifies injection doesn't bypass auth

class TestLoginBoundary:
    def test_login_with_very_long_username(self, page: Page):
        # ... sends 500-char string, verifies error
```

18 tests. 4 categories. Real selectors. Runnable.

---

## Running the Generated Tests

If you installed Playwright, you can actually execute the generated tests:

```bash
py -m pip install playwright pytest
playwright install chromium
pytest output/test_practicetestautomation_com_practice_test_login_playwright.py -v
```

---

## Cost Tracking

Every API call in full mode is logged. View your usage with:

```bash
py generate_tests.py --costs
```

Shows total requests, token counts, estimated cost, and per-provider breakdown.

---

## Roadmap

These features may be added in future releases if there is enough demand:

- [ ] **Automated pass/fail reporting** — Run generated tests via pytest and populate the report's status column with real pass/fail results
- [ ] **conftest.py generator** — Auto-generate Playwright fixtures so tests are runnable out of the box
- [ ] **Cypress test generation** — Support Cypress as an output format alongside Playwright and Gherkin
- [ ] **Batch URL processing** — Generate tests for multiple pages in a single run
- [ ] **Visual regression tests** — Generate screenshot comparison tests
- [ ] **CI/CD integration** — GitHub Actions workflow to run generated tests automatically
- [ ] **Custom prompt templates** — Let users define their own test generation prompts
- [ ] **Jira / Azure DevOps import** — Export generated test cases directly to test management tools

Have a feature request? [Open an issue](https://github.com/FaraazSuffla/ai-test-case-generator/issues) or give this repo a ⭐ to show interest.

---

## Project Structure

```
ai-test-case-generator/
├── generate_tests.py            # CLI entry point
├── src/
│   ├── analyzer.py              # Page analysis & accessibility tree
│   ├── generator.py             # LLM integration (Claude + OpenAI)
│   ├── demo_templates.py        # Built-in templates for --demo mode
│   ├── report.py                # HTML coverage report generator
│   ├── cost_tracker.py          # API usage tracking
│   ├── prompts.py               # LLM prompt templates
│   └── formatters/
│       ├── playwright_fmt.py    # Saves .py test files
│       └── gherkin_fmt.py       # Saves .feature files
├── output/                      # Generated tests & reports
├── examples/                    # Sample outputs
└── requirements.txt
```

## Tech Stack

Python 3.10+ · Anthropic SDK · OpenAI SDK · Playwright · BeautifulSoup4 · Rich · Click

## License

MIT — see [LICENSE](LICENSE).
