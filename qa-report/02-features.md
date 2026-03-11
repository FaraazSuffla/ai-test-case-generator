# QA Report — Feature Coverage Tester (Teammate 2)

## --help Output (full)

```
Usage: generate_tests.py [OPTIONS]

  Generate AI-powered test cases from URLs or feature descriptions.

Options:
  --url TEXT                     URL of the web page to generate tests for.
  --describe TEXT                Feature description to generate tests from.
  --format [playwright|gherkin]  Output format: playwright (Python) or gherkin
                                 (.feature).
  --provider [anthropic|openai]  LLM provider to use (default: anthropic).
  --model TEXT                   Specific model to use (default: claude-
                                 sonnet-4-20250514 for anthropic, gpt-4o for
                                 openai).
  --analyze                      Analyse page accessibility tree for context-
                                 aware tests.
  --demo                         Run in demo mode using built-in templates (no
                                 API key needed).
  --report                       Generate an HTML report alongside test files.
  --open-report                  Auto-open the HTML report in the browser
                                 after generation (implies --report).
  --run                          Generate tests then immediately execute them
                                 with pytest or behave.
  --watch                        Watch the target URL for changes and
                                 regenerate tests automatically. Re-runs every
                                 60 seconds.
  --watch-interval INTEGER       How often to check for page changes in
                                 --watch mode (seconds, default: 60).
  --costs                        Display API usage cost summary and exit.
  --conftest / --no-conftest     Generate conftest.py with Playwright fixtures
                                 (default: enabled for playwright format).
  --no-retry                     Disable retry logic (useful for CI/testing).
  --output-dir TEXT              Directory to write generated test files into.
                                 [default: output]
  --help                         Show this message and exit.
```

---

## Flag Checklist

| Flag | In README | In --help | Tested | Result |
|------|-----------|-----------|--------|--------|
| `--url` | ✅ | ✅ | ✅ (via demo commands) | PASS |
| `--describe` | ✅ | ✅ | ✅ (via demo commands) | PASS |
| `--format` | ✅ | ✅ | ✅ | PASS |
| `--output-dir` | ✅ | ✅ | ✅ | PASS (with bug, see below) |
| `--provider` | ✅ | ✅ | ❌ | UNTESTED — requires API key |
| `--model` | ✅ | ✅ | ❌ | UNTESTED — requires API key |
| `--analyze` | ✅ | ✅ | ❌ | UNTESTED — requires API key + URL |
| `--demo` | ✅ | ✅ | ✅ | PASS |
| `--report` | ✅ | ✅ | ✅ | PASS |
| `--open-report` | ✅ | ✅ | ❌ | SKIPPED — requires browser display |
| `--run` | ✅ | ✅ | ❌ | UNTESTED — requires API key or playwright install |
| `--watch` | ✅ | ✅ | ❌ | SKIPPED — infinite loop |
| `--watch-interval` | ✅ | ✅ | ❌ | SKIPPED — depends on --watch |
| `--costs` | ✅ | ✅ | ✅ | PASS (see notes) |
| `--conftest / --no-conftest` | ✅ | ✅ | ✅ | PASS |
| `--no-retry` | ✅ | ✅ | ✅ | PASS |

**All 15 README-documented flags appear in `--help`. No discrepancies between README and `--help`.**

---

## Test Results

### Test A: `--output-dir`
**Command:**
```
PYTHONUTF8=1 py generate_tests.py --demo --url https://practicetestautomation.com/practice-test-login/ --format playwright --output-dir qa-report/test-output
```
**Result: PARTIAL PASS — Bug Found**

**Output:**
```
✓ Generated playwright demo tests
✓ Saved: qa-report/test-output\test_practicetestautomation_com_practice_test_login_playwright.py
⚠ conftest.py already exists at output\conftest.py — skipping
```

**Bug:** The test `.py` file is correctly written to `qa-report/test-output/`. However, `conftest.py` is written to the default `output/` directory, **not** to the custom `--output-dir`. The completion summary panel also shows `Conftest: output\conftest.py`, confirming conftest ignores `--output-dir`.

**Impact:** A user setting `--output-dir` to organize their output will have tests in one location and the conftest fixture in another (`output/`). The pytest command shown at the end points to the custom dir but conftest.py won't be found there.

**README says:** "`--output-dir` — Directory to write generated test files into." No mention that conftest.py is excluded from this behavior.

---

### Test B: `--no-conftest`
**Command:**
```
PYTHONUTF8=1 py generate_tests.py --demo --url https://practicetestautomation.com/practice-test-login/ --format playwright --no-conftest
```
**Result: PASS**

**Output:**
```
✓ Generated playwright demo tests
✓ Saved: output\test_practicetestautomation_com_practice_test_login_playwright.py
```

**Confirmed:** No `conftest.py` generated. The completion panel does not show a "Conftest:" row. Works as documented.

---

### Test C: `--costs` (standalone)
**Command:**
```
PYTHONUTF8=1 py generate_tests.py --costs
```
**Result: PASS (with usability note)**

**Output:**
```
🤖 AI Test Case Generator
   Powered by Claude & OpenAI

No API calls logged yet. Generate some tests first!
```

**Notes:** Works correctly — exits cleanly after displaying cost info (or lack thereof). However, the README's "Cost Tracking" section says `py generate_tests.py --costs` "Shows total requests, token counts, estimated cost, and a per-provider breakdown." There is no mention of what happens when no API calls have been made yet. A new user running this as their first command will see "No API calls logged yet" and may be confused about whether the tool is broken or whether costs just haven't accumulated.

---

### Test D: `--no-retry`
**Command:**
```
PYTHONUTF8=1 py generate_tests.py --demo --describe "checkout flow" --format gherkin --no-retry
```
**Result: PASS**

**Output:**
```
✓ Generated gherkin demo tests
✓ Saved: output\checkout_flow.feature
```

Works correctly. No visible difference in behavior for demo mode (expected — retry logic only matters for live API calls).

---

### Test E: Missing required argument
**Command:**
```
PYTHONUTF8=1 py generate_tests.py --format playwright
```
**Result: PASS (error message is helpful)**

**Output (exit code 1):**
```
✗ Error: Provide either --url or --describe.

Examples:
  python generate_tests.py --url https://example.com/login --format playwright
  python generate_tests.py --describe "User registration" --format gherkin
  python generate_tests.py --demo --describe "login page" --format playwright
```

**Minor issue:** The error examples use `python` instead of `py`, inconsistent with the README's Quick Start which uses `py` throughout. Not a blocker but adds noise.

---

### Test F: Default `--format` (omitted)
**Command:**
```
PYTHONUTF8=1 py generate_tests.py --demo --describe "login"
```
**Result: PASS**

**Output:**
```
✓ Generated playwright demo tests
✓ Saved: output\test_login_playwright.py
Format: playwright
```

Default format is `playwright` as documented in the README flag table. Works correctly.

---

## README vs `--help` Discrepancies

**None found.** All 15 documented flags appear in `--help` with matching descriptions. The `--help` descriptions are slightly more verbose than the README table (e.g., `--watch` in `--help` says "Re-runs every 60 seconds" while README shows `--watch-interval` default as 60) but are consistent.

---

## Features Mentioned in README but Not Verifiable (No API Key)

| Feature | Flag | README Description |
|---------|------|--------------------|
| Accessibility tree analysis | `--analyze` | "Extract accessibility tree for smarter tests" |
| Execute after generation | `--run` | "Generate tests then execute them immediately with pytest / behave" |
| Provider selection | `--provider` | "`anthropic` or `openai`" |
| Model override | `--model` | "Override the default model (claude-sonnet-4-20250514 / gpt-4o)" |
| Auto-open report | `--open-report` | "Generate report and open it in the browser immediately" |
| Watch mode | `--watch` | "Re-generate whenever the target URL changes" |

All of these require either an API key or browser access that wasn't available during testing.

---

## Summary Verdict

Of the 15 documented flags, **9 were testable** without an API key. All 9 passed their core functionality. **One bug found:** `--output-dir` does not redirect `conftest.py` to the custom directory — it always writes conftest to `output/`. Additionally, the most critical discovery from a new-user perspective is the Windows encoding crash (documented in Report 01) that affects every command before any flag can be tested.
