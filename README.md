# 🤖 AI Test Case Generator

Generate structured **Playwright** or **Gherkin** test cases from any URL or feature description — powered by Claude and OpenAI.

---

## Try it in 60 seconds

No API key. No setup script. Three commands.

```bash
git clone https://github.com/FaraazSuffla/ai-test-case-generator.git
cd ai-test-case-generator
py -m pip install click rich python-dotenv beautifulsoup4 requests
py generate_tests.py --demo --describe "User login" --format playwright
```

You'll see 18 Playwright tests written to `output/`. Ready for your own app? See [Full AI Mode](#full-ai-mode) below.

---

## Quick Start

### Prerequisites

- **Python 3.10 or higher** — check with `py --version`
- **git** — for cloning ([download](https://git-scm.com/))

> **Mac / Linux users:** Replace `py` with `python3` in all commands below.

### Step 1 — Clone the repo

```bash
git clone https://github.com/FaraazSuffla/ai-test-case-generator.git
cd ai-test-case-generator
```

### Step 2 — Run setup

Run the setup script for your terminal. This creates a virtual environment and installs all dependencies.

**Windows (Command Prompt):**
```cmd
setup.bat
```

**Windows (PowerShell):**
```powershell
.\setup.bat
```

**Mac / Linux:**
```bash
./setup.sh
```

> **Note:** PowerShell requires `.\` before script names. CMD does not.

> **Tip:** If you get `ModuleNotFoundError` without using the setup script, run `py -m pip install -r requirements.txt` manually.

> **Windows users:** If you see a `UnicodeEncodeError`, run `set PYTHONUTF8=1` once in your session, then retry.

### Shortcut Wrappers (optional)

After setup, use the `testgen` shortcut instead of typing `py generate_tests.py` every time.

**Windows (Command Prompt):**
```cmd
testgen.bat --url https://example.com/login --format playwright
testgen.bat --demo --describe "login page" --format playwright
```

**Windows (PowerShell):**
```powershell
.\testgen.bat --url https://example.com/login --format playwright
.\testgen.bat --demo --describe "login page" --format playwright
```

**Mac / Linux:**
```bash
./testgen.sh --url https://example.com/login --format playwright
./testgen.sh --demo --describe "login page" --format playwright
```

> **Note:** `testgen.py` is a stub — do not run it directly.

---

## Two Modes

| Mode | What it does | API key needed? |
|------|-------------|-----------------|
| `--demo` | Uses built-in templates against a real login page | ❌ No |
| Full | AI-generates tests for any URL or description | ✅ Yes |

---

## Demo Mode

No API key required. Runs against [Practice Test Automation](https://practicetestautomation.com/practice-test-login/) — a real login page with known credentials (`student` / `Password123`) and real selectors, so the generated tests are actually runnable.

```bash
# Generate Playwright tests
py generate_tests.py --demo --url https://practicetestautomation.com/practice-test-login/ --format playwright

# Generate Gherkin scenarios
py generate_tests.py --demo --url https://practicetestautomation.com/practice-test-login/ --format gherkin

# Add an HTML coverage report
py generate_tests.py --demo --url https://practicetestautomation.com/practice-test-login/ --format playwright --report

# Generate from a description instead of a URL
py generate_tests.py --demo --describe "User registration" --format gherkin
```

Demo mode produces **18 Playwright tests** or **16 Gherkin scenarios** across 4 categories per run.

---

## Full AI Mode

Set your API key, then point the tool at any URL or description:

```bash
# Set your key (pick one)
export ANTHROPIC_API_KEY="your-key"
export OPENAI_API_KEY="your-key"

# Generate tests from a live page (uses Claude by default)
py generate_tests.py --url https://your-app.com/login --format playwright

# Use OpenAI instead
py generate_tests.py --url https://your-app.com/login --format gherkin --provider openai

# Include accessibility tree analysis for smarter tests
py generate_tests.py --url https://your-app.com/login --format playwright --analyze

# Generate from a description (no URL needed)
py generate_tests.py --describe "Shopping cart with coupon codes" --format playwright
```

---

## All CLI Flags

| Flag | Description | Default |
|------|-------------|---------|
| `--url` | URL to generate tests for | — |
| `--describe` | Feature description to generate from | — |
| `--format` | `playwright` or `gherkin` | `playwright` |
| `--output-dir` | Directory to write generated test files into | `output` |
| `--provider` | `anthropic` or `openai` | `anthropic` |
| `--model` | Override the default model (`claude-sonnet-4-20250514` / `gpt-4o`) | — |
| `--analyze` | Extract accessibility tree for smarter tests | off |
| `--demo` | Use built-in templates, no API key needed | off |
| `--report` | Generate an HTML coverage report | off |
| `--open-report` | Generate report and open it in the browser immediately | off |
| `--run` | Generate tests then execute them immediately with pytest / behave (requires `pytest` or `behave` installed) | off |
| `--watch` | Re-generate whenever the target URL changes (requires `--url`) | off |
| `--watch-interval` | Polling interval for `--watch` mode (seconds) | `60` |
| `--conftest/--no-conftest` | Generate `conftest.py` with Playwright fixtures | on |
| `--no-retry` | Disable retry logic for API calls (useful in CI) | off |
| `--costs` | Show API usage and cost summary | off |

> Either `--url` or `--describe` is required on every run.

---

## Viewing Your Output

All generated files are saved to the `output/` folder by default. Use `--output-dir <path>` to write to a different location.

**Windows (Command Prompt):**
```cmd
dir output\
type output\test_*.py
for %f in (output\report_*.html) do start %f
```

**Windows (PowerShell):**
```powershell
dir output\
Get-Content output\test_*.py
start (Get-Item output/report_*.html).FullName
```

**Mac / Linux:**
```bash
ls output/
cat output/test_*.py
open output/report_*.html        # macOS
xdg-open output/report_*.html   # Linux
```

> **Tip:** Add `--open-report` to any command to generate and open the report automatically.

---

## What Gets Generated

Every run produces tests across 4 categories:

| Category | What's Tested | Example |
|----------|--------------|---------| 
| ✅ Happy Path | Valid inputs, expected flows | Login with correct credentials |
| ❌ Negative | Invalid inputs, error handling | Wrong password, empty fields |
| 🔄 Edge Cases | Security & unusual inputs | SQL injection, XSS, case sensitivity |
| 📏 Boundary | Limits & extremes | 500-char username, special characters |

### Example: what the tool generates vs. what a junior might write

**Typical junior test:**
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
        ...  # verifies Log out link is visible

class TestLoginNegative:
    def test_login_with_invalid_username(self, page: Page):
        ...  # verifies "Your username is invalid!" error

    def test_login_with_invalid_password(self, page: Page):
        ...  # verifies "Your password is invalid!" error

class TestLoginEdgeCases:
    def test_login_with_sql_injection_in_username(self, page: Page):
        ...  # verifies injection doesn't bypass auth

class TestLoginBoundary:
    def test_login_with_very_long_username(self, page: Page):
        ...  # sends 500-char string, verifies error
```
18 tests. 4 categories. Real selectors. Runnable.

---

## Running the Generated Tests

Add `--run` to execute tests immediately after generation:

```bash
py generate_tests.py --demo --url https://practicetestautomation.com/practice-test-login/ --format playwright --run
```

Or run them manually after generation:

```bash
py -m pip install playwright pytest
playwright install chromium
pytest output/test_practicetestautomation_com_practice_test_login_playwright.py -v
```

> **Note on the HTML report status column:** Tests show as "Pending" because the tool *generates* test code — it doesn't execute it. Use `--run` to execute and see real results in the terminal.

---

## HTML Coverage Report

Add `--report` to any command to generate a standalone HTML report:

```bash
py generate_tests.py --demo --url https://practicetestautomation.com/practice-test-login/ --format playwright --report
```

The report includes:
- Total test count with category breakdown
- Collapsible sections per category
- Pass/fail status column (shows "Pending" until tests are executed)
- Export to PDF button
- Full generated code in a collapsible block
- Dark theme, no external dependencies

---

## Cost Tracking (Full Mode)

Every API call is logged. View your usage at any time:

```bash
py generate_tests.py --costs
```

Shows total requests, token counts, estimated cost, and a per-provider breakdown. If no API calls have been made yet, it shows "No API calls logged yet."

---

## Project Structure

```
ai-test-case-generator/
├── generate_tests.py          # CLI entry point
├── src/
│   ├── analyzer.py            # Page analysis & accessibility tree
│   ├── generator.py           # LLM integration (Claude + OpenAI)
│   ├── conftest_generator.py  # Playwright fixture generator
│   ├── demo_templates.py      # Built-in templates for --demo mode
│   ├── report.py              # HTML coverage report generator
│   ├── cost_tracker.py        # API usage tracking
│   ├── prompts.py             # LLM prompt templates
│   └── formatters/
│       ├── playwright_fmt.py  # Saves .py test files
│       └── gherkin_fmt.py     # Saves .feature files
├── tests/                     # Unit tests for core logic
├── output/                    # Generated tests & reports land here
├── examples/                  # Sample outputs
└── requirements.txt
```

---

## Roadmap

- **Cypress support** — Add Cypress as an output format alongside Playwright and Gherkin
- **Batch URL processing** — Generate tests for multiple pages in a single run
- **Visual regression tests** — Generate screenshot comparison tests
- **Custom prompt templates** — Let users define their own generation prompts
- **Jira / Azure DevOps export** — Push generated test cases directly to test management tools

Have a feature request? [Open an issue](https://github.com/FaraazSuffla/ai-test-case-generator/issues) or ⭐ the repo.

---

## Tech Stack

Python 3.10+ · Anthropic SDK · OpenAI SDK · Playwright · BeautifulSoup4 · Rich · Click

## License

MIT — see [LICENSE](LICENSE).
