# Demo Mode QA Report

**Spec source**: GitHub README only — https://github.com/FaraazSuffla/ai-test-case-generator
**Test date**: 2026-03-11
**Environment**: Windows 11, Python 3.14.3, pytest 9.0.2
**Status**: All bugs fixed — final results below

---

## Summary

| Result | Count |
|--------|-------|
| ✅ PASS | 9 |
| ❌ FAIL | 0 |
| ⚠️ PARTIAL | 0 |

**Overall verdict**: README is accurate. All 9 claims verified. All bugs found in initial run have been fixed.

---

## Claim-by-Claim Results

### Claim 1 — `--demo --describe "User login" --format playwright` → 18 Playwright tests
**Result**: ✅ PASS — exactly 18 `def test_` methods across 4 categories

### Claim 2 — `--demo --url ... --format gherkin` → 16 Gherkin scenarios
**Result**: ✅ PASS — exactly 16 `Scenario:` lines with @happy-path, @negative, @edge-case, @boundary tags

### Claim 3 — `--demo ... --report` → HTML coverage report
**Result**: ✅ PASS

| Feature | Found? |
|---------|--------|
| Total test count with category breakdown | ✅ "🧪 18 Test Cases Generated" badge + 4 cards |
| Collapsible sections per category | ✅ JS-toggled category sections |
| Pass/fail status showing "Pending" | ✅ All 18 rows show `⏳ Pending` |
| Export to PDF button | ✅ Calls `window.print()` |
| Full generated code in collapsible block | ✅ Show/Hide Code block |
| Dark theme | ✅ `background: #0f172a` |
| No external dependencies | ✅ Zero CDN links — all inline |

### Claim 4 — `--demo --describe "User registration" --format gherkin` → registration template
**Result**: ✅ PASS (fixed)
**Fix applied**: `_detect_feature()` keyword was `"register"` — not a substring of `"registration"` (`registr` ≠ `register`). Changed to `"registr"` which matches `register`, `registration`, `registered`, etc.
**Verified**: `output/User_registration.feature` now starts with `Feature: User Registration`

### Claim 5 — `--demo ... --run` → executes tests immediately
**Result**: ✅ PASS (fixed)
**Final run**: `18 passed in 48.01s` — clean, no errors, no failures

### Claim 6 — All outputs saved to `output/` folder
**Result**: ✅ PASS

### Claim 7 — 4 categories present in every generated file
**Result**: ✅ PASS — Happy Path, Negative, Edge Cases, Boundary in all files

### Claim 8 — `conftest.py` generated
**Result**: ✅ PASS

### Claim 9 — HTML report features
**Result**: ✅ PASS — see Claim 3

---

## Bugs Found and Fixed

| Bug | Root Cause | Fix | File |
|-----|-----------|-----|------|
| B1: Registration template served login content | `"register"` is NOT a substring of `"registration"` (`registr` ≠ `register`) | Changed keyword to `"registr"` | `src/demo_templates.py:479` |
| B2: `conftest.py` `NameError: 'os' not defined` | Template string used `os` before module-level `import os` | Added `import os` to template imports | `src/conftest_generator.py` |
| B2a: `conftest.py` `SyntaxError` (encoding) | `open()` used system default encoding (cp1252); em dash `—` is non-ASCII | Added `encoding="utf-8"` to `open()` | `src/conftest_generator.py:142` |
| B3: `to_have_url_matching` / `not_to_have_url_matching` | These methods don't exist in Playwright Python | Changed to `to_have_url(re.compile(...))` / `not_to_have_url(re.compile(...))` + added `import re` | `src/demo_templates.py` |
| B4: Wrong logout URL assertion | Template expected `https://practicetestautomation.com/` but site returns to login page | Changed assertion to `expect(page).to_have_url(BASE_URL)` | `src/demo_templates.py:56` |

---

## Commands Tested (Post-Fix)

```bash
# All pass ✅
py generate_tests.py --demo --describe "User login" --format playwright
py generate_tests.py --demo --url https://practicetestautomation.com/practice-test-login/ --format gherkin
py generate_tests.py --demo --url https://practicetestautomation.com/practice-test-login/ --format playwright --report
py generate_tests.py --demo --describe "User registration" --format gherkin
py generate_tests.py --demo --url https://practicetestautomation.com/practice-test-login/ --format playwright --run
# Result: 18 passed in 48.01s ✅
```
