"""Tests for src/formatters/playwright_fmt.py and src/formatters/gherkin_fmt.py."""

import os
from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from src.formatters.playwright_fmt import (
    _sanitise_filename as pw_sanitise,
    save_playwright_tests,
)
from src.formatters.gherkin_fmt import (
    _sanitise_filename as gh_sanitise,
    save_gherkin_tests,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_output(tmp_path):
    return str(tmp_path / "output")


@pytest.fixture(autouse=True)
def suppress_console():
    with (
        patch("src.formatters.playwright_fmt.console.print", MagicMock()),
        patch("src.formatters.gherkin_fmt.console.print", MagicMock()),
    ):
        yield


# ---------------------------------------------------------------------------
# 4.2  playwright_fmt._sanitise_filename
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("source,check", [
    ("https://example.com/login", lambda r: "https://" not in r),
    ("http://example.com",        lambda r: "http://" not in r),
    ("https://foo.com/bar?x=1&y=2", lambda r: "?" not in r and "=" not in r and "&" not in r),
    ("https://a...b.com",          lambda r: "__" not in r),
])
def test_pw_sanitise_parametrized(source, check):
    assert check(pw_sanitise(source))


def test_pw_sanitise_truncates_at_60_chars():
    long_source = "a" * 200
    result = pw_sanitise(long_source)
    # strip prefix "test_" and suffix "_playwright.py" to get the stem
    stem = result[len("test_"):-len("_playwright.py")]
    assert len(stem) <= 60


def test_pw_sanitise_has_test_prefix():
    assert pw_sanitise("https://example.com").startswith("test_")


def test_pw_sanitise_has_playwright_suffix():
    assert pw_sanitise("https://example.com").endswith("_playwright.py")


def test_pw_sanitise_plain_description():
    assert pw_sanitise("Login feature") == "test_Login_feature_playwright.py"


# ---------------------------------------------------------------------------
# 4.3  gherkin_fmt._sanitise_filename
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("source,check", [
    ("https://example.com/login", lambda r: "https://" not in r),
    ("http://example.com",        lambda r: "http://" not in r),
    ("https://foo.com/bar?x=1",   lambda r: "?" not in r and "=" not in r),
    ("https://a...b.com",          lambda r: "__" not in r),
])
def test_gh_sanitise_parametrized(source, check):
    assert check(gh_sanitise(source))


def test_gh_sanitise_truncates_at_60_chars():
    long_source = "a" * 200
    result = gh_sanitise(long_source)
    stem = result[:-len(".feature")]
    assert len(stem) <= 60


def test_gh_sanitise_has_feature_suffix():
    assert gh_sanitise("https://example.com").endswith(".feature")


def test_gh_sanitise_plain_description():
    assert gh_sanitise("Login feature") == "Login_feature.feature"


# ---------------------------------------------------------------------------
# 4.4  save_playwright_tests
# ---------------------------------------------------------------------------

def test_save_pw_creates_file(tmp_output):
    path = save_playwright_tests("def test_foo(): pass", "https://example.com", output_dir=tmp_output)
    assert os.path.exists(path)


def test_save_pw_returns_path_inside_output_dir(tmp_output):
    path = save_playwright_tests("def test_foo(): pass", "https://example.com", output_dir=tmp_output)
    assert path.startswith(tmp_output)


def test_save_pw_filename_matches_sanitise(tmp_output):
    path = save_playwright_tests("def test_foo(): pass", "https://example.com", output_dir=tmp_output)
    assert os.path.basename(path) == pw_sanitise("https://example.com")


def test_save_pw_header_contains_source(tmp_output):
    path = save_playwright_tests("def test_foo(): pass", "https://example.com", output_dir=tmp_output)
    content = open(path).read()
    assert "https://example.com" in content


def test_save_pw_header_contains_provider(tmp_output):
    path = save_playwright_tests("def test_foo(): pass", "https://example.com", provider="openai", output_dir=tmp_output)
    content = open(path).read()
    assert "openai" in content


def test_save_pw_header_contains_date(tmp_output):
    path = save_playwright_tests("def test_foo(): pass", "https://example.com", output_dir=tmp_output)
    content = open(path).read()
    assert date.today().strftime("%Y-%m-%d") in content


def test_save_pw_adds_imports_when_missing(tmp_output):
    path = save_playwright_tests("def test_foo(): pass", "https://example.com", output_dir=tmp_output)
    content = open(path).read()
    assert "import pytest" in content


def test_save_pw_no_duplicate_imports_when_present(tmp_output):
    code = "import pytest\nfrom playwright.sync_api import Page, expect\n\ndef test_foo(): pass"
    path = save_playwright_tests(code, "https://example.com", output_dir=tmp_output)
    content = open(path).read()
    assert content.count("import pytest") == 1


def test_save_pw_code_body_in_file(tmp_output):
    path = save_playwright_tests("def test_foo(): pass", "https://example.com", output_dir=tmp_output)
    content = open(path).read()
    assert "def test_foo(): pass" in content


def test_save_pw_file_ends_with_newline(tmp_output):
    path = save_playwright_tests("def test_foo(): pass", "https://example.com", output_dir=tmp_output)
    content = open(path).read()
    assert content[-1] == "\n"


def test_save_pw_default_provider_is_anthropic(tmp_output):
    path = save_playwright_tests("def test_foo(): pass", "https://example.com", output_dir=tmp_output)
    content = open(path).read()
    assert "anthropic" in content


def test_save_pw_creates_output_dir_if_absent(tmp_output):
    assert not os.path.exists(tmp_output)
    save_playwright_tests("def test_foo(): pass", "https://example.com", output_dir=tmp_output)
    assert os.path.isdir(tmp_output)


# ---------------------------------------------------------------------------
# 4.5  save_gherkin_tests
# ---------------------------------------------------------------------------

_GHERKIN_CODE = "Feature: Example\n  Scenario: works\n    Given something"


def test_save_gh_creates_file(tmp_output):
    path = save_gherkin_tests(_GHERKIN_CODE, "https://example.com", output_dir=tmp_output)
    assert os.path.exists(path)


def test_save_gh_returns_path_inside_output_dir(tmp_output):
    path = save_gherkin_tests(_GHERKIN_CODE, "https://example.com", output_dir=tmp_output)
    assert path.startswith(tmp_output)


def test_save_gh_filename_matches_sanitise(tmp_output):
    path = save_gherkin_tests(_GHERKIN_CODE, "https://example.com", output_dir=tmp_output)
    assert os.path.basename(path) == gh_sanitise("https://example.com")


def test_save_gh_filename_ends_with_feature(tmp_output):
    path = save_gherkin_tests(_GHERKIN_CODE, "https://example.com", output_dir=tmp_output)
    assert path.endswith(".feature")


def test_save_gh_header_contains_source(tmp_output):
    path = save_gherkin_tests(_GHERKIN_CODE, "https://example.com", output_dir=tmp_output)
    content = open(path).read()
    assert "https://example.com" in content


def test_save_gh_header_contains_provider(tmp_output):
    path = save_gherkin_tests(_GHERKIN_CODE, "https://example.com", provider="openai", output_dir=tmp_output)
    content = open(path).read()
    assert "openai" in content


def test_save_gh_header_contains_date(tmp_output):
    path = save_gherkin_tests(_GHERKIN_CODE, "https://example.com", output_dir=tmp_output)
    content = open(path).read()
    assert date.today().strftime("%Y-%m-%d") in content


def test_save_gh_code_body_preserved(tmp_output):
    path = save_gherkin_tests(_GHERKIN_CODE, "https://example.com", output_dir=tmp_output)
    content = open(path).read()
    assert _GHERKIN_CODE in content


def test_save_gh_file_ends_with_newline(tmp_output):
    path = save_gherkin_tests(_GHERKIN_CODE, "https://example.com", output_dir=tmp_output)
    content = open(path).read()
    assert content[-1] == "\n"


def test_save_gh_default_provider_is_anthropic(tmp_output):
    path = save_gherkin_tests(_GHERKIN_CODE, "https://example.com", output_dir=tmp_output)
    content = open(path).read()
    assert "anthropic" in content


def test_save_gh_creates_output_dir_if_absent(tmp_output):
    assert not os.path.exists(tmp_output)
    save_gherkin_tests(_GHERKIN_CODE, "https://example.com", output_dir=tmp_output)
    assert os.path.isdir(tmp_output)
