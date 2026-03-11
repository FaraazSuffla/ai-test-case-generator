# QA Report — Setup Tester (Teammate 1)

## Environment

| Item | Value |
|------|-------|
| OS | Windows 11 (cp1252 terminal encoding) |
| Python version | 3.14.3 |
| Date tested | 2026-03-11 |
| Working directory | D:\GitHubProjects\ai-test-case-generator |

---

## Dependency Installation

**Command run (as per README "Demo mode only" section):**
```
py -m pip install click rich python-dotenv beautifulsoup4 requests
```
**Result:** PASS — all packages already satisfied (no installation errors)

**Notes:** The README correctly identifies the minimum packages for demo mode. No issues here.

---

## Demo Command Results

### Command A
```
py generate_tests.py --demo --url https://practicetestautomation.com/practice-test-login/ --format playwright
```
**Result: FAIL (CRITICAL)**

**Output:**
```
Traceback (most recent call last):
  File "generate_tests.py", line 297, in <module>
    main()
  File "generate_tests.py", line 218, in main
    console.print(Panel(BANNER, border_style="blue", width=45))
  ...
  File "C:\...\cp1252.py", line 19, in encode
    return codecs.charmap_encode(input,self.errors,encoding_table)[0]
UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f916' in position 0:
character maps to <undefined>
```

**Root cause:** The banner contains the robot emoji `🤖` which cannot be encoded in Windows's default cp1252 terminal encoding. The tool crashes before producing any output.

**Workaround found:** Running with `PYTHONUTF8=1` prefix resolves the issue:
```
PYTHONUTF8=1 py generate_tests.py --demo --url ... --format playwright
```
But **the README never mentions this workaround** or this requirement.

---

### Command A (with workaround applied)
```
PYTHONUTF8=1 py generate_tests.py --demo --url https://practicetestautomation.com/practice-test-login/ --format playwright
```
**Result: PASS**

**Output:**
```
🤖 AI Test Case Generator
   Powered by Claude & OpenAI

⚡ Demo mode: Using built-in templates (no API key required)

✓ Generated playwright demo tests
✓ Saved: output\test_practicetestautomation_com_practice_test_login_playwright.py
✓ Generated: output\conftest.py

✨ Complete — Tests generated successfully! (demo)
```

---

### Command B
```
py generate_tests.py --demo --url https://practicetestautomation.com/practice-test-login/ --format gherkin
```
**Result: FAIL (same UnicodeEncodeError as Command A)**

**With workaround — PASS:**
```
✓ Generated gherkin demo tests
✓ Saved: output\practicetestautomation_com_practice_test_login.feature
```

---

### Command C
```
py generate_tests.py --demo --url https://practicetestautomation.com/practice-test-login/ --format playwright --report
```
**Result: FAIL (same UnicodeEncodeError)**

**With workaround — PASS:**
```
✓ Generated playwright demo tests
✓ Saved: output\test_practicetestautomation_com_practice_test_login_playwright.py
⚠ conftest.py already exists at output\conftest.py — skipping
✓ Report: output\report_https_practicetestautomation_com_practice_test_log.html
```

---

### Command D
```
py generate_tests.py --demo --describe "User registration" --format gherkin
```
**Result: FAIL (same UnicodeEncodeError)**

**With workaround — PASS:**
```
✓ Generated gherkin demo tests
✓ Saved: output\User_registration.feature
```

---

## Generated Output Files

After all commands ran (with workaround), the `output/` directory contained:

```
User_registration.feature
checkout_flow.feature
conftest.py
practicetestautomation_com_practice_test_login.feature
report_https_practicetestautomation_com_practice_test_log.html
test_login_playwright.py
test_practicetestautomation_com_practice_test_login_playwright.py
```

The README states demo mode produces "18 Playwright tests" and "16 Gherkin scenarios across 4 categories". This was not independently verified (would require opening the files), but file generation was confirmed.

---

## README Gaps & Issues Found

1. **[BLOCKER — P1]** No mention of Windows encoding issue. Every single demo command fails on a stock Windows terminal with cp1252 encoding. The fix (`PYTHONUTF8=1` or using Windows Terminal with UTF-8) is never mentioned anywhere in the README. A new user on Windows hits this immediately and has no guidance.

2. **[P2]** No mention of minimum Python version requirement in the Quick Start section. The Tech Stack section at the very bottom says "Python 3.10+" but this is easy to miss. A user running an older Python version would get confusing errors.

3. **[P2]** Step 1 says "Clone the repo" — this assumes the user has git installed. No prerequisite check or alternative download method (e.g., Download ZIP from GitHub) is mentioned.

4. **[P3]** The README says "Demo mode produces 18 Playwright tests or 16 Gherkin scenarios across 4 categories" but doesn't explain how to verify this (e.g., "open the generated file and count the `def test_` functions"). New users may not know what to check.

5. **[P3]** The README's "Viewing Your Output" section uses `ls` and `cat` (Unix commands) and `start` (Windows). A Windows user following sequentially would need to know that `ls` = `dir` in CMD. Minor, but could confuse total beginners.

6. **[P3]** The shortcut wrappers section says `testgen.bat` is optional and mentions `testgen.py` is a stub not to run directly. This is a potential foot-gun — no obvious indication in the file listing which wrapper to use.

---

## Summary Verdict

**Setup fails for all new Windows users** due to an undocumented Unicode encoding requirement. Once `PYTHONUTF8=1` is prepended (or UTF-8 mode is enabled at the OS level), all 4 demo commands run successfully and produce the expected output files. The tool works correctly — but new users will hit a cryptic `UnicodeEncodeError` crash with no README guidance on how to fix it.
