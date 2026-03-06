# 🤖 AI Test Case Generator

Generate structured **Playwright** or **Gherkin** test cases from any URL or feature description — powered by Claude and OpenAI.

---

## ⚡ Quick Start (2 steps)

### 1. Clone & run setup

**Windows — Command Prompt (`cmd.exe`):**
```bat
git clone https://github.com/FaraazSuffla/ai-test-case-generator.git
cd ai-test-case-generator
setup.bat
```

**Windows — Git Bash:**
```bash
git clone https://github.com/FaraazSuffla/ai-test-case-generator.git
cd ai-test-case-generator
source .venv/Scripts/activate
```
> ⚠️ Run `setup.bat` first from Command Prompt, then use Git Bash for running commands.

**Mac / Linux:**
```bash
git clone https://github.com/FaraazSuffla/ai-test-case-generator.git
cd ai-test-case-generator
bash setup.sh
```

The setup script will:
- ✅ Check your Python version
- ✅ Create an isolated virtual environment
- ✅ Install all dependencies
- ✅ Install the Playwright browser
- ✅ Create a `.env` file ready for your API key

### 2. Add your API key

Open the `.env` file and set:

```
ANTHROPIC_API_KEY=your-key-here
```

Get a free key at [console.anthropic.com](https://console.anthropic.com).

That’s it — you’re ready.

---

## Usage

| Terminal | Command prefix |
|----------|---------------|
| Windows Command Prompt | `testgen.bat` |
| Windows Git Bash | `python generate_tests.py` |
| Mac / Linux | `./testgen.sh` |

### Try demo mode first (no API key needed)

```bat
testgen.bat --demo --url https://practicetestautomation.com/practice-test-login/ --format playwright
testgen.bat --demo --url https://practicetestautomation.com/practice-test-login/ --format gherkin
testgen.bat --demo --url https://practicetestautomation.com/practice-test-login/ --format playwright --report
```

### Generate real tests from any URL

```bat
testgen.bat --url https://your-app.com/login --format playwright
testgen.bat --url https://your-app.com/login --format gherkin
testgen.bat --describe "Shopping cart with coupon codes" --format playwright
```

### Auto-open the HTML report in your browser

```bat
testgen.bat --url https://your-app.com/login --format playwright --open-report
```

### Generate tests and run them immediately

```bat
testgen.bat --url https://your-app.com/login --format playwright --run
```

Combine with demo mode to test without an API key:

```bat
testgen.bat --demo --url https://practicetestautomation.com/practice-test-login/ --format playwright --run
```

### Watch a URL for changes and auto-regenerate

```bat
testgen.bat --url https://your-app.com/login --format playwright --watch
```

Checks every 60 seconds by default. Change the interval:

```bat
testgen.bat --url https://your-app.com/login --format playwright --watch --watch-interval 30
```

Combine with `--run` to regenerate AND re-run tests on every change:

```bat
testgen.bat --url https://your-app.com/login --format playwright --watch --run
```

Press `Ctrl+C` to stop watching.

### Use OpenAI instead of Claude

```bat
testgen.bat --url https://your-app.com/login --format playwright --provider openai
```

---

## All CLI Flags

| Flag | Description | Default |
|------|-------------|------|
| `--url` | URL to generate tests for | — |
| `--describe` | Feature description to generate from | — |
| `--format` | `playwright` or `gherkin` | `playwright` |
| `--demo` | Use built-in templates — no API key needed | off |
| `--report` | Generate an HTML coverage report | off |
| `--open-report` | Generate report and auto-open in browser | off |
| `--run` | Generate tests then immediately execute them | off |
| `--watch` | Watch URL for changes and regenerate automatically | off |
| `--watch-interval` | Seconds between checks in watch mode | `60` |
| `--provider` | `anthropic` or `openai` | `anthropic` |
| `--model` | Override the default model | — |
| `--analyze` | Extract accessibility tree for smarter tests | off |
| `--costs` | Show API usage and cost summary | off |

---

## What Gets Generated

Every run produces tests across **4 categories**:

| Category | What’s Tested | Example |
|----------|--------------|----------|
| ✅ **Happy Path** | Valid inputs, expected flows | Login with correct credentials |
| ❌ **Negative** | Invalid inputs, error handling | Wrong password, empty fields |
| 🔄 **Edge Cases** | Security & unusual inputs | SQL injection, XSS payloads |
| 📏 **Boundary** | Limits & extremes | 500-char username, special chars |

---

## Running Generated Tests

**Command Prompt** (use the exact filename from output):
```bat
pytest output\test_practicetestautomation_com_practice_test_login_playwright.py -v
```

**Git Bash / Mac / Linux:**
```bash
pytest output/test_*.py -v
```

Or skip the manual step entirely — use `--run` to do it automatically.

---

## Cost Tracking

```bat
testgen.bat --costs
```

---

## Project Structure

```
ai-test-case-generator/
├── setup.bat / setup.sh         # One-command installer
├── testgen.bat / testgen.sh     # Easy run shortcuts
├── generate_tests.py            # CLI entry point
├── .env.example                 # API key template
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
└── examples/                    # Sample outputs
```

## Tech Stack

Python 3.10+ · Anthropic SDK · OpenAI SDK · Playwright · BeautifulSoup4 · Rich · Click

## License

MIT — see [LICENSE](LICENSE).
