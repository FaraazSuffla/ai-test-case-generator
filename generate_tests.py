#!/usr/bin/env python3
"""AI Test Case Generator — CLI entry point.

Usage:
    python generate_tests.py --url https://example.com/login --format playwright
    python generate_tests.py --describe "User registration" --format gherkin
    python generate_tests.py --url https://example.com --format playwright --analyze
    python generate_tests.py --demo --describe "login page" --format playwright
    python generate_tests.py --demo --url https://example.com/login --format playwright --report
    python generate_tests.py --url https://example.com/login --format playwright --run
    python generate_tests.py --url https://example.com/login --format playwright --watch
    python generate_tests.py --costs
"""

import subprocess
import sys
import time
import webbrowser
import os

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


def _run_generation(
    url, describe, output_format, provider, model, analyze, demo, report, open_report, conftest
) -> tuple[str, str]:
    """Core generation logic. Returns (filepath, report_path or '')."""
    source = url or describe

    if demo:
        console.print(
            "\n[yellow]⚡ Demo mode:[/yellow] Using built-in templates (no API key required)\n"
        )
        test_code = get_demo_output(
            format=output_format,
            url=url or "",
            description=describe or "",
        )
        console.print(f"[green]✓[/green] Generated {output_format} demo tests")
    else:
        from src.analyzer import analyse_page
        from src.generator import generate_tests

        analysis = None
        if url:
            analysis = analyse_page(url, include_a11y=analyze)

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

    active_provider = provider if not demo else "demo"

    if output_format == "playwright":
        filepath = save_playwright_tests(test_code, source, active_provider)
    else:
        filepath = save_gherkin_tests(test_code, source, active_provider)

    conftest_path = None
    if conftest and output_format == "playwright":
        from src.conftest_generator import generate_conftest
        conftest_path = generate_conftest()

    report_path = ""
    if report:
        from src.report import generate_report
        report_path = generate_report(
            test_code=test_code,
            source=source,
            format=output_format,
            provider=active_provider,
            test_filepath=filepath,
            auto_open=open_report,
        )
        console.print(f"[green]✓[/green] Report: [bold]{report_path}[/bold]")

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

    return filepath, report_path


def _run_tests(filepath: str, output_format: str) -> None:
    """Execute the generated tests using pytest or behave."""
    if output_format == "playwright":
        cmd = [sys.executable, "-m", "pytest", filepath, "-v", "--tb=short"]
        runner = "pytest"
    else:
        cmd = [sys.executable, "-m", "behave", filepath]
        runner = "behave"

    console.print(f"\n[cyan]🚀 Running tests with {runner}...[/cyan]\n")
    result = subprocess.run(cmd)

    if result.returncode == 0:
        console.print("\n[green]✅ All tests passed![/green]")
    else:
        console.print(f"\n[red]❌ Tests finished with exit code {result.returncode}[/red]")


def _get_page_hash(url: str) -> str | None:
    """Fetch the page and return a hash of its content for change detection."""
    try:
        import hashlib
        import requests
        resp = requests.get(url, timeout=15)
        return hashlib.md5(resp.text.encode()).hexdigest()
    except Exception:
        return None


@click.command()
@click.option("--url", type=str, default=None, help="URL of the web page to generate tests for.")
@click.option("--describe", type=str, default=None, help="Feature description to generate tests from.")
@click.option(
    "--format", "output_format",
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
@click.option("--model", type=str, default=None, help="Specific model to use (overrides provider default).")
@click.option("--analyze", is_flag=True, default=False, help="Analyse page accessibility tree for context-aware tests.")
@click.option("--demo", is_flag=True, default=False, help="Run in demo mode using built-in templates (no API key needed).")
@click.option("--report", is_flag=True, default=False, help="Generate an HTML report alongside test files.")
@click.option("--open-report", is_flag=True, default=False, help="Auto-open the HTML report in the browser after generation (implies --report).")
@click.option("--run", "run_tests", is_flag=True, default=False, help="Generate tests then immediately execute them with pytest or behave.")
@click.option(
    "--watch", is_flag=True, default=False,
    help="Watch the target URL for changes and regenerate tests automatically. Re-runs every 60 seconds."
)
@click.option("--watch-interval", type=int, default=60, help="How often to check for page changes in --watch mode (seconds, default: 60).")
@click.option("--costs", is_flag=True, default=False, help="Display API usage cost summary and exit.")
@click.option("--conftest/--no-conftest", default=True, help="Generate conftest.py with Playwright fixtures (default: enabled for playwright format).")
def main(
    url, describe, output_format, provider, model,
    analyze, demo, report, open_report, run_tests, watch, watch_interval, costs, conftest,
) -> None:
    """Generate AI-powered test cases from URLs or feature descriptions."""
    console.print(Panel(BANNER, border_style="blue", width=45))

    if costs:
        from src.cost_tracker import display_cost_summary
        display_cost_summary()
        return

    if not url and not describe:
        console.print(
            "[red]✗ Error:[/red] Provide either --url or --describe.\n"
            "\nExamples:\n"
            "  python generate_tests.py --url https://example.com/login --format playwright\n"
            "  python generate_tests.py --describe \"User registration\" --format gherkin\n"
            "  python generate_tests.py --demo --describe \"login page\" --format playwright"
        )
        sys.exit(1)

    # --open-report implies --report
    if open_report:
        report = True

    # --watch mode: poll for changes and regenerate
    if watch:
        if not url:
            console.print("[red]✗ Error:[/red] --watch requires --url.")
            sys.exit(1)

        console.print(
            f"[cyan]👁️  Watch mode:[/cyan] Checking [bold]{url}[/bold] every {watch_interval}s for changes.\n"
            "Press [bold]Ctrl+C[/bold] to stop.\n"
        )

        last_hash = None
        run_count = 0

        try:
            while True:
                current_hash = _get_page_hash(url)

                if current_hash != last_hash:
                    if last_hash is None:
                        console.print("[green]✓[/green] Initial run...")
                    else:
                        console.print("[yellow]⚠️  Page changed — regenerating tests...[/yellow]")

                    run_count += 1
                    filepath, report_path = _run_generation(
                        url, describe, output_format, provider, model,
                        analyze, demo, report, open_report, conftest
                    )

                    if run_tests:
                        _run_tests(filepath, output_format)

                    last_hash = current_hash
                else:
                    console.print(f"[dim]⏳ No changes detected. Next check in {watch_interval}s... (run #{run_count})[/dim]")

                time.sleep(watch_interval)

        except KeyboardInterrupt:
            console.print(f"\n[yellow]Watch stopped after {run_count} generation(s).[/yellow]")
        return

    # Normal single run
    filepath, report_path = _run_generation(
        url, describe, output_format, provider, model,
        analyze, demo, report, open_report, conftest
    )

    if run_tests:
        _run_tests(filepath, output_format)


if __name__ == "__main__":
    main()
