# 🤖 AI Test Case Generator

Generate structured **Playwright** or **Gherkin** test cases from any URL or feature description — powered by Claude and OpenAI.

---

## Table of Contents

- [Try it in 60 seconds](#try-it-in-60-seconds)
- [Quick Start](#quick-start)
- [Two Modes](#two-modes)
- [Demo Mode](#demo-mode)
- [Full AI Mode](#full-ai-mode)
- [All CLI Flags](#all-cli-flags)
- [Viewing Your Output](#viewing-your-output)
- [Shortcut Wrappers (optional)](#shortcut-wrappers-optional)
- [What Gets Generated](#what-gets-generated)
- [Running the Generated Tests](#running-the-generated-tests)
- [HTML Coverage Report](#html-coverage-report)
- [Cost Tracking](#cost-tracking-full-mode)
- [Project Structure](#project-structure)
- [Roadmap](#roadmap)

---

## Try it in 60 seconds

No API key. No setup script. Pick your terminal and run the commands below.

> **Start from your home folder** — open a fresh terminal (it defaults to your home folder). Never clone into `C:\WINDOWS\System32` or other protected directories.

<details>
<summary><b>Windows (Command Prompt)</b></summary>

```cmd
cd %USERPROFILE%
git clone https://github.com/FaraazSuffla/ai-test-case-generator.git
cd ai-test-case-generator
py -m pip install click rich python-dotenv beautifulsoup4 requests
py generate_tests.py --demo --describe "User login" --format playwright
```

</details>

<details>
<summary><b>Windows (PowerShell)</b></summary>

```powershell
cd ~
git clone https://github.com/FaraazSuffla/ai-test-case-generator.git
cd ai-test-case-generator
py -m pip install click rich python-dotenv beautifulsoup4 requests
py generate_tests.py --demo --describe "User login" --format playwright
```

</details>

<details>
<summary><b>Mac / Linux</b></summary>

```bash
cd ~
git clone https://github.com/FaraazSuffla/ai-test-case-generator.git
cd ai-test-case-generator
pip3 install click rich python-dotenv beautifulsoup4 requests
python3 generate_tests.py --demo --describe "User login" --format playwright
```

</details>

You'll see 18 Playwright tests written to `output/`. Ready for your own app? See [Full AI Mode](#full-ai-mode) below.

---

## Quick Start

### Prerequisites

- **Python 3.10 or higher** — check with `py --version` (Windows) or `python3 --version` (Mac/Linux)
- **git** — for cloning ([download](https://git-scm.com/))

### Step 1 — Clone the repo

Open a fresh terminal in your home or projects folder, then run:

```bash
git clone https://github.com/FaraazSuffla/ai-test-case-generator.git
cd ai-test-case-generator
```

### Step 2 — Run setup

This creates a virtual environment and installs all dependencies. Pick your terminal:

<details>
<summary><b>Windows (Command Prompt)</b></summary>

```cmd
setup.bat
```

</details>

<details>
<summary><b>Windows (PowerShell)</b></summary>

```powershell
.\setup.bat
```

> PowerShell requires `.\` before script names. CMD does not.

</details>

<details>
<summary><b>Mac / Linux</b></summary>

```bash
./setup.sh
```

</details>

> **Tip:** If you get `ModuleNotFoundError`, run `py -m pip install -r requirements.txt` manually.

> **Windows users:** If you see a `UnicodeEncodeError`, run `set PYTHONUTF8=1` once in your session, then retry.

Once setup is complete, see [Shortcut Wrappers](#shortcut-wrappers-optional) to skip typing `py generate_tests.py` every time.

---

## Two Modes

| Mode | What it does | API key needed? |
|------|-------------|-----------------|
| `--demo` | Uses built-in templates against a real login page | ❌ No |
| Full | AI-generates tests for any URL or description | ✅ Yes |

---

## Demo Mode

No API key required. Runs against [Practice Test Automation](https://practicetestautomation.com/practice-test-login/) — a real login page with known credentials (`student` / `Password123`) and real selectors, so the generated tests are actually runnable.

<details>
<summary><b>Windows (Command Prompt)</b></summary>

```cmd
py generate_tests.py --demo --url https://practicetestautomation.com/practice-test-login/ --format playwright
py generate_tests.py --demo --url https://practicetestautomation.com/practice-test-login/ --format gherkin
py generate_tests.py --demo --url https://practicetestautomation.com/practice-test-login/ --format playwright --report
py generate_tests.py --demo --describe "User registration" --format gherkin
```

</details>

<details>
<summary><b>Windows (PowerShell)</b></summary>

```powershell
py generate_tests.py --demo --url https://practicetestautomation.com/practice-test-login/ --format playwright
py generate_tests.py --demo --url https://practicetestautomation.com/practice-test-login/ --format gherkin
py generate_tests.py --demo --url https://practicetestautomation.com/practice-test-login/ --format playwright --report
py generate_tests.py --demo --describe "User registration" --format gherkin
```

</details>

<details>
<summary><b>Mac / Linux</b></summary>

```bash
python3 generate_tests.py --demo --url https://practicetestautomation.com/practice-test-login/ --format playwright
python3 generate_tests.py --demo --url https://practicetestautomation.com/practice-test-login/ --format gherkin
python3 generate_tests.py --demo --url https://practicetestautomation.com/practice-test-login/ --format playwright --report
python3 generate_tests.py --demo --describe "User registration" --format gherkin
```

</details>

Demo mode produces **18 Playwright tests** or **16 Gherkin scenarios** across 4 categories per run.

---

## Full AI Mode

Set your API key first, then point the tool at any URL or description.

<details>
<summary><b>Windows (Command Prompt)</b></summary>

```cmd
set ANTHROPIC_API_KEY=your-key
py generate_tests.py --url https://your-app.com/login --format playwright
py generate_tests.py --url https://your-app.com/login --format gherkin --provider openai
py generate_tests.py --url https://your-app.com/login --format playwright --analyze
py generate_tests.py --describe "Shopping cart with coupon codes" --format playwright
```

</details>

<details>
<summary><b>Windows (PowerShell)</b></summary>

```powershell
$env:ANTHROPIC_API_KEY="your-key"
py generate_tests.py --url https://your-app.com/login --format playwright
py generate_tests.py --url https://your-app.com/login --format gherkin --provider openai
py generate_tests.py --url https://your-app.com/login --format playwright --analyze
py generate_tests.py --describe "Shopping cart with coupon codes" --format playwright
```

</details>

<details>
<summary><b>Mac / Linux</b></summary>

```bash
export ANTHROPIC_API_KEY="your-key"
python3 generate_tests.py --url https://your-app.com/login --format playwright
python3 generate_tests.py --url https://your-app.com/login --format gherkin --provider openai
python3 generate_tests.py --url https://your-app.com/login --format playwright --analyze
python3 generate_tests.py --describe "Shopping cart with coupon codes" --format playwright
```

</details>

---

## All CLI Flags

<details>
<summary><b>Show all flags</b></summary>

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
| `--run` | Generate tests then execute them immediately with pytest / behave | off |
| `--watch` | Re-generate whenever the target URL changes (requires `--url`) | off |
| `--watch-interval` | Polling interval for `--watch` mode (seconds) | `60` |
| `--conftest/--no-conftest` | Generate `conftest.py` with Playwright fixtures | on |
| `--no-retry` | Disable retry logic for API calls (useful in CI) | off |
| `--costs` | Show API usage and cost summary | off |

> Either `--url` or `--describe` is required on every run.

</details>

---

## Viewing Your Output

All generated files are saved to the `output/` folder. Use `--output-dir <path>` to write elsewhere.

<details>
<summary><b>Windows (Command Prompt)</b></summary>

```cmd
dir output\
type output\test_*.py
for %f in (output\report_*.html) do start %f
```

</details>

<details>
<summary><b>Windows (PowerShell)</b></summary>

```powershell
dir output\
Get-Content output\test_*.py
start (Get-Item output/report_*.html).FullName
```

</details>

<details>
<summary><b>Mac / Linux</b></summary>

```bash
ls output/
cat output/test_*.py
open output/report_*.html        # macOS
xdg-open output/report_*.html   # Linux
```

</details>

> **Tip:** Add `--open-report` to any command to generate and open the report automatically.

---

## Shortcut Wrappers (optional)

After setup, use the `testgen` shortcut instead of typing `py generate_tests.py` every time.

<details>
<summary><b>Windows (Command Prompt)</b></summary>

```cmd
testgen.bat --url https://example.com/login --format playwright
testgen.bat --demo --describe "login page" --format playwright
```

</details>

<details>
<summary><b>Windows (PowerShell)</b></summary>

```powershell
.\testgen.bat --url https://example.com/login --format playwright
.\testgen.bat --demo --describe "login page" --format playwright
```

</details>

<details>
<summary><b>Mac / Linux</b></summary>

```bash
./testgen.sh --url https://example.com/login --format playwright
./testgen.sh --demo --describe "login page" --format playwright
```

</details>

> **Note:** PowerShell requires `.\` before script names. CMD does not. `testgen.py` is a stub — do not run it directly.

---

## What Gets Generated

Every run produces tests across 4 categories:

| Category | What's Tested | Example |
|----------|--------------|---------|
| ✅ Happy Path | Valid inputs, expected flows | Login with correct credentials |
| ❌ Negative | Invalid inputs, error handling | Wrong password, empty fields |
| 🔄 Edge Cases | Security & unusual inputs | SQL injection, XSS, case sensitivity |
| 📏 Boundary | Limits & extremes | 500-char username, special characters |

<details>
<summary><b>See example: what this tool generates vs. a typical junior test</b></summary>

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

</details>

---

## Running the Generated Tests

Add `--run` to execute tests immediately after generation:

<details>
<summary><b>Windows (Command Prompt / PowerShell)</b></summary>

```cmd
py generate_tests.py --demo --url https://practicetestautomation.com/practice-test-login/ --format playwright --run
```

Or run manually after generation:

```cmd
py -m pip install playwright pytest
playwright install chromium
pytest output/test_practicetestautomation_com_practice_test_login_playwright.py -v
```

</details>

<details>
<summary><b>Mac / Linux</b></summary>

```bash
python3 generate_tests.py --demo --url https://practicetestautomation.com/practice-test-login/ --format playwright --run
```

Or run manually after generation:

```bash
pip3 install playwright pytest
playwright install chromium
pytest output/test_practicetestautomation_com_practice_test_login_playwright.py -v
```

</details>

> **Note on the HTML report status column:** Tests show as "Pending" because the tool *generates* test code — it doesn't execute it. Use `--run` to execute and see real results in the terminal.

---

## HTML Coverage Report

Add `--report` to any command to generate a standalone HTML report:

<details>
<summary><b>Windows (Command Prompt / PowerShell)</b></summary>

```cmd
py generate_tests.py --demo --url https://practicetestautomation.com/practice-test-login/ --format playwright --report
```

</details>

<details>
<summary><b>Mac / Linux</b></summary>

```bash
python3 generate_tests.py --demo --url https://practicetestautomation.com/practice-test-login/ --format playwright --report
```

</details>

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

<details>
<summary><b>Windows (Command Prompt / PowerShell)</b></summary>

```cmd
py generate_tests.py --costs
```

</details>

<details>
<summary><b>Mac / Linux</b></summary>

```bash
python3 generate_tests.py --costs
```

</details>

Shows total requests, token counts, estimated cost, and a per-provider breakdown.

---

## Project Structure

<details>
<summary><b>Show project structure</b></summary>

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

</details>

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
