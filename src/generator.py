"""LLM integration for test case generation.

Supports Anthropic (Claude) and OpenAI as providers.
Handles prompt assembly, API calls, response parsing,
and cost tracking.
"""

import os
import time
from typing import Optional

from dotenv import load_dotenv
from rich.console import Console

from src.prompts import (
    SYSTEM_PROMPT,
    PLAYWRIGHT_TEMPLATE,
    GHERKIN_TEMPLATE,
    URL_CONTEXT_TEMPLATE,
    URL_WITH_ACCESSIBILITY_TEMPLATE,
    DESCRIPTION_CONTEXT_TEMPLATE,
)
from src.analyzer import PageAnalysis
from src.cost_tracker import log_api_call

load_dotenv()
console = Console()

# Default models
DEFAULT_MODELS = {
    "anthropic": "claude-sonnet-4-20250514",
    "openai": "gpt-4o",
}

_RETRY_DELAYS: list[int] = [2, 4, 8]
LLM_MAX_OUTPUT_TOKENS = 4096


def _build_context(
    url: Optional[str] = None,
    description: Optional[str] = None,
    analysis: Optional[PageAnalysis] = None,
    include_a11y: bool = False,
) -> str:
    """Build the context string for the LLM prompt.

    Uses page analysis data if available, otherwise falls back
    to the raw URL or feature description.
    """
    if analysis and analysis.title and not analysis.title.startswith("Error"):
        if include_a11y and analysis.accessibility_tree:
            return URL_WITH_ACCESSIBILITY_TEMPLATE.format(
                url=analysis.url,
                title=analysis.title,
                forms=analysis.forms,
                interactive_elements=analysis.interactive_elements,
                nav_links=analysis.nav_links,
                accessibility_tree=analysis.accessibility_tree,
            )
        return URL_CONTEXT_TEMPLATE.format(
            url=analysis.url,
            title=analysis.title,
            forms=analysis.forms,
            interactive_elements=analysis.interactive_elements,
            nav_links=analysis.nav_links,
        )

    if url:
        return f"Generate test cases for the web page at: {url}"

    if description:
        return DESCRIPTION_CONTEXT_TEMPLATE.format(description=description)

    raise ValueError("Either url or description must be provided.")


def _call_anthropic(prompt: str, model: str, *, retry: bool = True) -> tuple[str, int, int]:
    """Call the Anthropic Claude API.

    Returns:
        Tuple of (response_text, input_tokens, output_tokens)
    """
    import anthropic

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY not set. Add it to your .env file or "
            "export it as an environment variable."
        )

    client = anthropic.Anthropic(api_key=api_key)

    _RETRYABLE = (
        anthropic.RateLimitError,
        anthropic.APIConnectionError,
        anthropic.InternalServerError,
    )

    for attempt, delay in enumerate(_RETRY_DELAYS + [None], start=1):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=LLM_MAX_OUTPUT_TOKENS,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            break  # success — exit the loop
        except _RETRYABLE as exc:
            is_last = delay is None
            if not retry or is_last:
                raise
            console.print(
                f"[yellow]⚠ Anthropic API error (attempt {attempt}/{len(_RETRY_DELAYS)}):[/yellow] "
                f"{type(exc).__name__} — retrying in {delay}s…"
            )
            time.sleep(delay)

    text = response.content[0].text
    input_tokens = response.usage.input_tokens
    output_tokens = response.usage.output_tokens

    return text, input_tokens, output_tokens


def _call_openai(prompt: str, model: str, *, retry: bool = True) -> tuple[str, int, int]:
    """Call the OpenAI API.

    Returns:
        Tuple of (response_text, input_tokens, output_tokens)
    """
    import openai
    from openai import OpenAI

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "OPENAI_API_KEY not set. Add it to your .env file or "
            "export it as an environment variable."
        )

    client = OpenAI(api_key=api_key)

    _RETRYABLE = (
        openai.RateLimitError,
        openai.APIConnectionError,
        openai.InternalServerError,
    )

    for attempt, delay in enumerate(_RETRY_DELAYS + [None], start=1):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=LLM_MAX_OUTPUT_TOKENS,
            )
            break
        except _RETRYABLE as exc:
            is_last = delay is None
            if not retry or is_last:
                raise
            console.print(
                f"[yellow]⚠ OpenAI API error (attempt {attempt}/{len(_RETRY_DELAYS)}):[/yellow] "
                f"{type(exc).__name__} — retrying in {delay}s…"
            )
            time.sleep(delay)

    text = response.choices[0].message.content
    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens

    return text, input_tokens, output_tokens


def generate_tests(
    format: str = "playwright",
    provider: str = "anthropic",
    model: Optional[str] = None,
    url: Optional[str] = None,
    description: Optional[str] = None,
    analysis: Optional[PageAnalysis] = None,
    include_a11y: bool = False,
    retry: bool = True,
) -> str:
    """Generate test cases using the specified LLM provider.

    Args:
        format: Output format — 'playwright' or 'gherkin'.
        provider: LLM provider — 'anthropic' or 'openai'.
        model: Specific model to use (defaults per provider).
        url: Target URL for test generation.
        description: Feature description for test generation.
        analysis: Pre-computed page analysis.
        include_a11y: Include accessibility tree in context.
        retry: Retry transient API errors with exponential back-off.

    Returns:
        Generated test code as a string.
    """
    if model is None:
        model = DEFAULT_MODELS.get(provider, DEFAULT_MODELS["anthropic"])

    # Build context from inputs
    context = _build_context(url, description, analysis, include_a11y)

    # Select format template
    if format == "playwright":
        prompt = PLAYWRIGHT_TEMPLATE.format(context=context)
    elif format == "gherkin":
        prompt = GHERKIN_TEMPLATE.format(context=context)
    else:
        raise ValueError(f"Unknown format: {format}. Use 'playwright' or 'gherkin'.")

    console.print(
        f"\n[cyan]🤖 Generating {format} tests with {provider} ({model})...[/cyan]"
    )

    # Call the appropriate provider
    if provider == "anthropic":
        text, input_tokens, output_tokens = _call_anthropic(prompt, model, retry=retry)
    elif provider == "openai":
        text, input_tokens, output_tokens = _call_openai(prompt, model, retry=retry)
    else:
        raise ValueError(
            f"Unknown provider: {provider}. Use 'anthropic' or 'openai'."
        )

    # Log cost
    entry = log_api_call(
        provider=provider,
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        purpose=f"{format}_generation",
    )

    console.print(
        f"[green]✓[/green] Generated {format} tests "
        f"({input_tokens + output_tokens:,} tokens, "
        f"${entry['estimated_cost_usd']:.4f})"
    )

    # Clean up response — remove markdown fences if present
    text = _clean_response(text, format)

    return text


def _clean_response(text: str, format: str) -> str:
    """Strip markdown code fences and leading/trailing whitespace."""
    lines = text.strip().split("\n")

    # Remove opening fence
    if lines and lines[0].strip().startswith("```"):
        lines = lines[1:]

    # Remove closing fence
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]

    return "\n".join(lines).strip()
