#!/usr/bin/env python3
"""AI Test Case Generator — CLI entry point.

Usage:
    python generate_tests.py --url https://example.com/login --format playwright
    python generate_tests.py --describe "User registration" --format gherkin
    python generate_tests.py --url https://example.com --format playwright --analyze
    python generate_tests.py --costs
"""

import sys

import click
from rich.console import Console
from rich.panel import Panel

from src.analyzer import analyse_page
from src.generator import generate_tests
from src.formatters.playwright_fmt import save_playwright_tests
from src.formatters.gherkin_fmt import save_gherkin_tests
from src.cost_tracker import display_cost_summary

console = Console()

BANNER = """
🤖 AI Test Case Generator
   Powered by Claude & OpenAI
"""


@click.command()
@click.option(
    "--url",
    type=str,
    default=None,
    help="URL of the web page to generate tests for.",
)
@click.option(
    "--describe",
    type=str,
    default=None,
    help="Feature description to generate tests from.",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["playwright", "gherkin"], case_sensitive=False),
    default="playwright",
    help="Output format: playwright (Python) or gherkin (.feature).",
)
@click.option(
    "--provider",
    type=click.Choice(["anthropic", "openai"], case_sensitive=False),
    default="anthropic",
    help="LLM provider to use (default: anthropic).",
)
@click.option(
    "--model",
    type=str,
    default=None,
    help="Specific model to use (overrides provider default).",
)
@click.option(
    "--analyze",
    is_flag=True,
    default=False,
    help="Analyse page accessibility tree for context-aware tests.",
)
@click.option(
    "--costs",
    is_flag=True,
    default=False,
    help="Display API usage cost summary and exit.",
)
def main(
    url: str,
    describe: str,
    output_format: str,
    provider: str,
    model: str,
    analyze: bool,
    costs: bool,
) -> None:
    """Generate AI-powered test cases from URLs or feature descriptions."""
    console.print(Panel(BANNER, border_style="blue", width=45))

    # Cost summary mode
    if costs:
        display_cost_summary()
        return

    # Validate inputs
    if not url and not describe:
        console.print(
            "[red]✗ Error:[/red] Provide either --url or --describe.\n"
            "\nExamples:\n"
            "  python generate_tests.py --url https://example.com/login --format playwright\n"
            "  python generate_tests.py --describe \"User registration\" --format gherkin"
        )
        sys.exit(1)

    # Analyse page if URL provided
    analysis = None
    if url:
        analysis = analyse_page(url, include_a11y=analyze)

    # Generate tests
    try:
        source = url or describe
        test_code = generate_tests(
            format=output_format,
            provider=provider,
            model=model,
            url=url,
            description=describe,
            analysis=analysis,
            include_a11y=analyze,
        )
    except EnvironmentError as e:
        console.print(f"\n[red]✗ Configuration error:[/red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]✗ Generation failed:[/red] {e}")
        sys.exit(1)

    # Save output
    if output_format == "playwright":
        filepath = save_playwright_tests(test_code, source, provider)
    else:
        filepath = save_gherkin_tests(test_code, source, provider)

    # Final summary
    console.print(
        Panel(
            f"[green]✓ Tests generated successfully![/green]\n\n"
            f"File: [bold]{filepath}[/bold]\n"
            f"Format: {output_format}\n"
            f"Provider: {provider}\n\n"
            f"Run with: [dim]{'pytest ' + filepath + ' -v' if output_format == 'playwright' else 'behave ' + filepath}[/dim]",
            title="✨ Complete",
            border_style="green",
            width=60,
        )
    )


if __name__ == "__main__":
    main()
