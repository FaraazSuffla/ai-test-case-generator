"""Tests for src/prompts.py — all five template constants."""

import pytest

from src.prompts import (
    SYSTEM_PROMPT,
    PLAYWRIGHT_TEMPLATE,
    GHERKIN_TEMPLATE,
    URL_CONTEXT_TEMPLATE,
    URL_WITH_ACCESSIBILITY_TEMPLATE,
    DESCRIPTION_CONTEXT_TEMPLATE,
)


# ---------------------------------------------------------------------------
# SYSTEM_PROMPT
# ---------------------------------------------------------------------------

def test_system_prompt_is_nonempty_string():
    assert isinstance(SYSTEM_PROMPT, str) and len(SYSTEM_PROMPT) > 0


@pytest.mark.parametrize("category", ["Happy Path", "Negative", "Edge Cases", "Boundary Values"])
def test_system_prompt_covers_category(category):
    assert category in SYSTEM_PROMPT


# ---------------------------------------------------------------------------
# PLAYWRIGHT_TEMPLATE and GHERKIN_TEMPLATE — shared roundtrip
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "template",
    [PLAYWRIGHT_TEMPLATE, GHERKIN_TEMPLATE],
    ids=["playwright", "gherkin"],
)
def test_single_context_template_roundtrip(template):
    assert "{context}" in template
    result = template.format(context="STUB")
    assert "STUB" in result
    assert "{" not in result


# ---------------------------------------------------------------------------
# URL_CONTEXT_TEMPLATE
# ---------------------------------------------------------------------------

_URL_CTX_KWARGS = dict(url="U", title="T", forms="F", interactive_elements="IE", nav_links="NL")


def test_url_context_template_has_all_placeholders():
    for placeholder in ["{url}", "{title}", "{forms}", "{interactive_elements}", "{nav_links}"]:
        assert placeholder in URL_CONTEXT_TEMPLATE


def test_url_context_template_formats_without_error():
    URL_CONTEXT_TEMPLATE.format(**_URL_CTX_KWARGS)


def test_url_context_template_output_contains_all_values():
    result = URL_CONTEXT_TEMPLATE.format(**_URL_CTX_KWARGS)
    for value in ["U", "T", "F", "IE", "NL"]:
        assert value in result


def test_url_context_template_no_unresolved_placeholders():
    result = URL_CONTEXT_TEMPLATE.format(**_URL_CTX_KWARGS)
    assert "{" not in result


# ---------------------------------------------------------------------------
# URL_WITH_ACCESSIBILITY_TEMPLATE
# ---------------------------------------------------------------------------

_A11Y_KWARGS = dict(
    url="U", title="T", forms="F", interactive_elements="IE", nav_links="NL",
    accessibility_tree="A11Y",
)


def test_a11y_template_has_all_placeholders():
    for placeholder in [
        "{url}", "{title}", "{forms}", "{interactive_elements}",
        "{nav_links}", "{accessibility_tree}",
    ]:
        assert placeholder in URL_WITH_ACCESSIBILITY_TEMPLATE


def test_a11y_template_formats_without_error():
    URL_WITH_ACCESSIBILITY_TEMPLATE.format(**_A11Y_KWARGS)


def test_a11y_template_output_contains_all_values():
    result = URL_WITH_ACCESSIBILITY_TEMPLATE.format(**_A11Y_KWARGS)
    for value in ["U", "T", "F", "IE", "NL", "A11Y"]:
        assert value in result


def test_a11y_template_no_unresolved_placeholders():
    result = URL_WITH_ACCESSIBILITY_TEMPLATE.format(**_A11Y_KWARGS)
    assert "{" not in result


# ---------------------------------------------------------------------------
# DESCRIPTION_CONTEXT_TEMPLATE
# ---------------------------------------------------------------------------

def test_description_template_has_placeholder():
    assert "{description}" in DESCRIPTION_CONTEXT_TEMPLATE


def test_description_template_formats_without_error():
    DESCRIPTION_CONTEXT_TEMPLATE.format(description="Login feature")


def test_description_template_output_contains_description():
    result = DESCRIPTION_CONTEXT_TEMPLATE.format(description="Login feature")
    assert "Login feature" in result


def test_description_template_no_unresolved_placeholders():
    result = DESCRIPTION_CONTEXT_TEMPLATE.format(description="Login feature")
    assert "{" not in result
