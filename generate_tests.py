#!/usr/bin/env python3
"""AI Test Case Generator — CLI entry point.

Usage:
    python generate_tests.py --url https://example.com/login --format playwright
    python generate_tests.py --describe "User registration" --format gherkin
    python generate_tests.py --url https://example.com --format playwright --analyze
    python generate_tests.py --demo --describe "login page" --format playwright
    python generate_tests.py --demo --url https://example.com/login --format playwright --report
    python generate_tests.py --costs
"""

import sys

import click
from rich.console import Console
from rich.panel import Panel

from src.formatters.playwright_fmt import save_playwright_tests
from src.formatters.gherkin_fmt import save_gherkin_tests
from src.demo_templates import get_demo_output

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
    "--demo",
    is_flag=True,
    default=False,
    help="Run in demo mode using built-in templates (no API key needed).",
)
@click.option(
    "--report",
    is_flag=True,
    default=False,
    help="Generate an HTML report alongside test files.",
)
@click.option(
    "--costs",
    is_flag=True,
    default=False,
    help="Display API usage cost summary and exit.",
)
@click.option(
    "--conftest/--no-conftest",
    default=True,
    help="Generate conftest.py with Playwright fixtures (default: enabled for playwright format).",
)
def main(
    url: str,
    describe: str,
    output_format: str,
    provider: str,
    model: str,
    analyze: bool,
    demo: bool,
    report: bool,
    costs: bool,
    conftest: bool,
) -> None:
    """Generate AI-powered test cases from URLs or feature descriptions."""
    console.print(Panel(BANNER, border_style="blue", width=45))

    # Cost summary mode
    if costs:
        from src.cost_tracker import display_cost_summary
        display_cost_summary()
        return

    # Validate inputs
    if not url and not describe:
        console.print(
            "[red]✗ Error:[/red] Provide either --url or --describe.\n"
            "\nExamples:\n"
            "  python generate_tests.py --url https://example.com/login --format playwright\n"
            "  python generate_tests.py --describe \"User registration\" --format gherkin\n"
            "  python generate_tests.py --demo --describe \"login page\" --format playwright"
        )
        sys.exit(1)

    source = url or describe

    # Demo mode — no API key needed
    if demo:
        console.print(
            "\n[yellow]⚡ Demo mode:[/yellow] Using built-in templates (no API key required)\n"
        )
        test_code = get_demo_output(
            format=output_format,
            url=url or "",
            description=describe or "",
        )
        console.print(
            f"[green]✓[/green] Generated {output_format} demo tests"
        )
    else:
        # Only import heavy dependencies when actually needed
        from src.analyzer import analyse_page
        from src.generator import generate_tests

        # Analyse page if URL provided
        analysis = None
        if url:
            analysis = analyse_page(url, include_a11y=analyze)

        # Generate tests via LLM
        try:
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
            console.print(
                "\n[yellow]💡 Tip:[/yellow] Run with [bold]--demo[/bold] to "
                "try the tool without an API key:\n"
                "  python generate_tests.py --demo --describe \"login page\" --format playwright"
            )
            sys.exit(1)
        except Exception as e:
            console.print(f"\n[red]✗ Generation failed:[/red] {e}")
            sys.exit(1)

    # Save output
    active_provider = provider if not demo else "demo"
    if output_format == "playwright":
        filepath = save_playwright_tests(test_code, source, active_provider)
    else:
        filepath = save_gherkin_tests(test_code, source, active_provider)

    # Generate conftest.py for Playwright tests
    conftest_path = None
    if conftest and output_format == "playwright":
        from src.conftest_generator import generate_conftest
        conftest_path = generate_conftest()

    # Generate HTML report if requested
    report_path = None
    if report:
        from src.report import generate_report
        report_path = generate_report(
            test_code=test_code,
            source=source,
            format=output_format,
            provider=active_provider,
            test_filepath=filepath,
        )
        console.print(f"[green]✓[/green] Report: [bold]{report_path}[/bold]")

    # Final summary
    mode_label = " (demo)" if demo else ""
    summary_lines = [
        f"[green]✓ Tests generated successfully!{mode_label}[/green]\n",
        f"File:     [bold]{filepath}[/bold]",
        f"Format:   {output_format}",
        f"Provider: {'demo (built-in templates)' if demo else provider}",
    ]
    if conftest_path:
        summary_lines.append(f"Conftest: [bold]{conftest_path}[/bold]")
    if report_path:
        summary_lines.append(f"Report:   [bold]{report_path}[/bold]")
    summary_lines.append(
        f"\nRun with: [dim]{'pytest ' + filepath + ' -v' if output_format == 'playwright' else 'behave ' + filepath}[/dim]"
    )

    console.print(
        Panel(
            "\n".join(summary_lines),
            title="✨ Complete",
            border_style="green",
            width=60,
        )
    )


if __name__ == "__main__":
    main()
