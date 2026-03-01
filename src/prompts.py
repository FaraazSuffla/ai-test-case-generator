"""Prompt templates for AI test case generation.

Contains structured prompts that guide the LLM to produce
consistent, comprehensive test cases across different formats.
"""

SYSTEM_PROMPT = """You are an expert QA automation engineer. Your job is to generate
comprehensive, production-quality test cases for web applications.

For every feature or page you analyse, you MUST generate tests in these categories:
1. **Happy Path** — Core user flows that should always work.
2. **Negative** — Invalid inputs, missing data, unauthorised access.
3. **Edge Cases** — Unusual but valid scenarios (unicode, XSS, SQL injection, long strings).
4. **Boundary Values** — Min/max lengths, zero values, off-by-one errors.

Rules:
- Use modern Playwright best practices (role-based locators, expect assertions).
- Each test must have a clear docstring explaining what it verifies.
- Group tests into classes by category.
- Include accessibility checks where relevant.
- Be specific with selectors — prefer get_by_role, get_by_label, get_by_text.
- Never use hard-coded waits; use Playwright's built-in auto-waiting.
"""

PLAYWRIGHT_TEMPLATE = """Generate Playwright (Python) test stubs for the following:

{context}

Requirements:
- Use pytest with Playwright fixtures (page: Page).
- Import: `import pytest` and `from playwright.sync_api import Page, expect`.
- Group tests into classes: TestHappyPath, TestNegative, TestEdgeCases, TestBoundary.
- Each test method must have a descriptive docstring.
- Use role-based and label-based selectors (get_by_role, get_by_label, get_by_text).
- Include accessibility tests if relevant (aria labels, tab order, screen reader).
- Output ONLY valid Python code, no markdown fences or explanations.

Generate at minimum 8 tests covering all four categories.
"""

GHERKIN_TEMPLATE = """Generate Gherkin feature file content for the following:

{context}

Requirements:
- Start with a Feature: block with a clear description.
- Include a Background: section for common setup steps.
- Write Scenarios for: happy path, negative, edge cases, and boundary values.
- Use Scenario Outline with Examples tables where appropriate.
- Each Scenario must have a descriptive name.
- Use Given/When/Then/And steps clearly.
- Include @tags for each category: @happy-path, @negative, @edge-case, @boundary.
- Output ONLY valid Gherkin syntax, no markdown fences or explanations.

Generate at minimum 8 scenarios covering all four categories.
"""

URL_CONTEXT_TEMPLATE = """I need test cases for the web page at: {url}

Here is the page analysis:
- Title: {title}
- Forms found: {forms}
- Interactive elements: {interactive_elements}
- Navigation links: {nav_links}

Generate comprehensive test cases for all functionality visible on this page.
"""

URL_WITH_ACCESSIBILITY_TEMPLATE = """I need test cases for the web page at: {url}

Here is the page analysis:
- Title: {title}
- Forms found: {forms}
- Interactive elements: {interactive_elements}
- Navigation links: {nav_links}

Accessibility tree summary:
{accessibility_tree}

Generate comprehensive test cases for all functionality visible on this page.
Include dedicated accessibility test cases based on the accessibility tree data.
"""

DESCRIPTION_CONTEXT_TEMPLATE = """I need test cases for the following feature:

{description}

Generate comprehensive test cases for this feature, imagining a typical
web implementation with forms, buttons, and user interactions.
"""
