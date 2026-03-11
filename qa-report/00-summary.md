# QA Summary Report — ai-test-case-generator

**Tested:** 2026-03-11
**Method:** README-only — all testing performed following README.md instructions exclusively, simulating a brand-new user experience
**Platform:** Windows 11, Python 3.14.3, cp1252 terminal encoding
**Reports:** [01-setup.md](01-setup.md) · [02-features.md](02-features.md) · [03-readme-audit.md](03-readme-audit.md)

---

## Overall Verdict

> **The project works — but new Windows users can't reach it.**

Once running, the tool is solid. All demo commands produce correct output. Feature flags behave as documented. The generated files look well-structured. **However, every single command crashes on a stock Windows terminal before producing any output**, due to an undocumented Unicode encoding requirement. A new user following the README exactly hits a cryptic Python traceback on their very first command.

The fix is one environment variable (`PYTHONUTF8=1`). The README never mentions it.

---

## Top 3 Friction Points for a New User

### 1. The tool crashes immediately on Windows (before any output)
**What happens:** Running any command from the README on a standard Windows terminal produces:
```
UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f916'
character maps to <undefined>
```
The banner contains the 🤖 emoji, which Windows cp1252 encoding cannot render. The crash happens before any useful work is done.

**Who is affected:** Every Windows user using Command Prompt or PowerShell with default encoding.
**Workaround:** Prefix commands with `PYTHONUTF8=1` — but this is undocumented.
**Severity:** Complete blocker. Nothing in the README hints at a fix.

---

### 2. `--output-dir` doesn't fully redirect output
**What happens:** Running `py generate_tests.py --demo ... --output-dir my-dir` sends the test `.py` or `.feature` file to `my-dir/` correctly, but `conftest.py` still lands in the default `output/` directory.

**Impact:** The pytest run command shown at the end points to `my-dir/test_*.py`, but `conftest.py` (which defines the Playwright fixtures needed to run those tests) is in `output/`. Tests will fail to find fixtures. The user sees no warning.

**Severity:** Silent correctness bug — tests appear to be set up correctly but will fail when executed.

---

### 3. Python version requirement is buried 290 lines down
**What happens:** Python 3.10+ is required (the f-string and match-case syntax used throughout won't work on older versions). This information appears only in the "Tech Stack" section at the very end of the README.

**Impact:** A user with Python 3.8 or 3.9 will follow the full Quick Start, install all dependencies, and hit obscure syntax errors with no guidance pointing them back to the version requirement.

**Severity:** Affects any user running an older Python install. Easy to miss.

---

## Top 3 README Fixes with Highest Impact

### Fix 1 — Add Windows encoding note to Quick Start
**Where:** Immediately after "Step 2 — Install dependencies", or as a callout before the first demo command.

**Content:**
```
> **Windows users:** If you see a `UnicodeEncodeError` when running any command,
> prepend `PYTHONUTF8=1` to enable UTF-8 mode:
>
> ```bash
> PYTHONUTF8=1 py generate_tests.py --demo --url ...
> ```
> Or set it permanently: `set PYTHONUTF8=1` in your terminal session.
```

**Impact:** Unblocks 100% of affected Windows users with one line.

---

### Fix 2 — Move Python version requirement to the top
**Where:** Add a "Prerequisites" section before Step 1 in Quick Start.

**Content:**
```
## Prerequisites
- Python 3.10 or higher (`py --version` to check)
- [git](https://git-scm.com/) for cloning
```

**Impact:** Prevents version mismatch errors before any installation happens.

---

### Fix 3 — Fix or document the `--output-dir` + conftest behavior
**Option A (code fix):** Make `conftest.py` respect `--output-dir` like all other generated files.
**Option B (documentation):** Add a note to the `--output-dir` row in the flags table:
```
> **Note:** `conftest.py` is always written to `output/` regardless of this setting.
```

**Impact:** Prevents silent test failures when users customize their output location.

---

## Usability Score

### 6 / 10

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| First-run success (Windows) | 2/10 | Crashes before producing any output |
| First-run success (Mac/Linux) | 8/10 | Likely works cleanly; encoding not an issue |
| Feature completeness | 9/10 | All tested features work correctly |
| Error messaging | 7/10 | Missing-arg error is helpful; encoding crash is not |
| README clarity | 6/10 | Well-structured but missing critical platform notes |
| Output quality | 9/10 | Generated files are clean and well-formatted |

**Justification:** The tool itself is well-built — clean output, correct behavior, good feature coverage. The score is dragged down by a single undocumented encoding issue that makes the tool completely inaccessible to Windows users out of the box. Fix that one issue and the score jumps to ~8.5/10. The `--output-dir` / conftest bug and the buried Python version requirement are secondary but real friction points. The README is thorough but platform-blind.

---

## Quick-Fix Checklist

- [ ] Add `PYTHONUTF8=1` note for Windows users in Quick Start
- [ ] Move Python 3.10+ requirement to Prerequisites before Step 1
- [ ] Fix `--output-dir` to redirect `conftest.py` (or document the exception)
- [ ] Add one sentence to `--costs` section about the empty-state message
- [ ] Add `--run` dependency note (pytest / behave must be installed)
- [ ] Add Windows `dir`/`type` equivalents to "Viewing Your Output" section
- [ ] Update error-message examples from `python` to `py` for Windows consistency
