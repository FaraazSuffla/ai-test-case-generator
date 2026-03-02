"""HTML report generator for test case output.

Produces a polished, standalone HTML report showing generated test
cases with syntax highlighting, category breakdowns, and metadata.
Opens automatically in the default browser after generation.
"""

import os
import re
import webbrowser
from datetime import datetime
from html import escape


OUTPUT_DIR = "output"


def _count_tests_by_category(test_code: str, fmt: str) -> dict:
    """Parse generated test code and count tests per category."""
    categories = {
        "happy_path": 0,
        "negative": 0,
        "edge_cases": 0,
        "boundary": 0,
    }

    if fmt == "playwright":
        # Count methods per class
        current_category = None
        for line in test_code.split("\n"):
            lower = line.lower()
            if "class test" in lower:
                if "happypath" in lower or "happy_path" in lower:
                    current_category = "happy_path"
                elif "negative" in lower:
                    current_category = "negative"
                elif "edgecase" in lower or "edge_case" in lower:
                    current_category = "edge_cases"
                elif "boundary" in lower:
                    current_category = "boundary"
                else:
                    current_category = None
            elif line.strip().startswith("def test_") and current_category:
                categories[current_category] += 1

    elif fmt == "gherkin":
        current_tag = None
        for line in test_code.split("\n"):
            stripped = line.strip()
            if stripped.startswith("@"):
                tags = stripped.lower()
                if "happy-path" in tags or "happy_path" in tags:
                    current_tag = "happy_path"
                elif "negative" in tags:
                    current_tag = "negative"
                elif "edge-case" in tags or "edge_case" in tags:
                    current_tag = "edge_cases"
                elif "boundary" in tags:
                    current_tag = "boundary"
            elif stripped.startswith("Scenario:") or stripped.startswith("Scenario Outline:"):
                if current_tag:
                    categories[current_tag] += 1
                current_tag = None

    return categories


def _extract_test_names(test_code: str, fmt: str) -> list[dict]:
    """Extract individual test names and their docstrings/descriptions."""
    tests = []

    if fmt == "playwright":
        current_class = ""
        lines = test_code.split("\n")
        for i, line in enumerate(lines):
            if line.strip().startswith("class "):
                match = re.match(r'\s*class\s+(\w+)', line)
                if match:
                    current_class = match.group(1)
            elif line.strip().startswith("def test_"):
                match = re.match(r'\s*def\s+(test_\w+)', line)
                if match:
                    name = match.group(1)
                    docstring = ""
                    # Look for docstring on next line(s)
                    for j in range(i + 1, min(i + 3, len(lines))):
                        if '"""' in lines[j]:
                            docstring = lines[j].strip().strip('"""').strip('"')
                            break
                    tests.append({
                        "name": name,
                        "class": current_class,
                        "description": docstring,
                    })

    elif fmt == "gherkin":
        for line in test_code.split("\n"):
            stripped = line.strip()
            if stripped.startswith("Scenario:") or stripped.startswith("Scenario Outline:"):
                name = stripped.split(":", 1)[1].strip()
                tests.append({
                    "name": name,
                    "class": "Feature",
                    "description": "",
                })

    return tests


def _get_category_label(key: str) -> str:
    """Convert category key to display label."""
    labels = {
        "happy_path": "Happy Path",
        "negative": "Negative",
        "edge_cases": "Edge Cases",
        "boundary": "Boundary",
    }
    return labels.get(key, key.replace("_", " ").title())


def _get_category_color(key: str) -> str:
    """Get the color for a category."""
    colors = {
        "happy_path": "#22c55e",
        "negative": "#ef4444",
        "edge_cases": "#f59e0b",
        "boundary": "#3b82f6",
    }
    return colors.get(key, "#6b7280")


def _get_category_icon(key: str) -> str:
    """Get the emoji icon for a category."""
    icons = {
        "happy_path": "&#x2705;",
        "negative": "&#x274C;",
        "edge_cases": "&#x1F504;",
        "boundary": "&#x1F4CF;",
    }
    return icons.get(key, "&#x1F4CB;")


def generate_report(
    test_code: str,
    source: str,
    format: str,
    provider: str,
    test_filepath: str,
) -> str:
    """Generate an HTML report for the generated test cases.

    Args:
        test_code: The generated test code string.
        source: URL or description used to generate tests.
        format: 'playwright' or 'gherkin'.
        provider: The LLM provider or 'demo'.
        test_filepath: Path to the saved test file.

    Returns:
        Path to the generated HTML report.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    categories = _count_tests_by_category(test_code, format)
    tests = _extract_test_names(test_code, format)
    total_tests = sum(categories.values())
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Build category cards
    category_cards = ""
    for key, count in categories.items():
        if count > 0:
            category_cards += f"""
            <div class="card">
                <div class="card-icon">{_get_category_icon(key)}</div>
                <div class="card-count">{count}</div>
                <div class="card-label">{_get_category_label(key)}</div>
                <div class="card-bar" style="background: {_get_category_color(key)}; width: {max(count / max(total_tests, 1) * 100, 15):.0f}%"></div>
            </div>"""

    # Build test list
    test_rows = ""
    for i, test in enumerate(tests, 1):
        badge_class = "badge-happy"
        cls_lower = test["class"].lower()
        if "negative" in cls_lower:
            badge_class = "badge-negative"
        elif "edge" in cls_lower:
            badge_class = "badge-edge"
        elif "boundary" in cls_lower:
            badge_class = "badge-boundary"

        category_name = test["class"].replace("Test", "").replace("_", " ")
        desc = test["description"] or "—"

        test_rows += f"""
                <tr>
                    <td class="row-num">{i}</td>
                    <td class="test-name"><code>{escape(test['name'])}</code></td>
                    <td><span class="badge {badge_class}">{escape(category_name)}</span></td>
                    <td class="test-desc">{escape(desc)}</td>
                </tr>"""

    # Escape the code for HTML display
    escaped_code = escape(test_code)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Report — AI Test Case Generator</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            line-height: 1.6;
        }}

        .container {{
            max-width: 960px;
            margin: 0 auto;
            padding: 2rem 1.5rem;
        }}

        /* Header */
        .header {{
            text-align: center;
            margin-bottom: 2.5rem;
            padding-bottom: 2rem;
            border-bottom: 1px solid #1e293b;
        }}

        .header h1 {{
            font-size: 1.8rem;
            font-weight: 700;
            color: #f8fafc;
            margin-bottom: 0.5rem;
        }}

        .header h1 span {{
            color: #38bdf8;
        }}

        .header .subtitle {{
            color: #94a3b8;
            font-size: 0.95rem;
        }}

        /* Meta info */
        .meta {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
            background: #1e293b;
            border-radius: 12px;
            padding: 1.25rem 1.5rem;
        }}

        .meta-item {{
            display: flex;
            flex-direction: column;
            gap: 0.2rem;
        }}

        .meta-label {{
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #64748b;
        }}

        .meta-value {{
            font-size: 0.95rem;
            color: #e2e8f0;
            word-break: break-all;
        }}

        /* Summary cards */
        .section-title {{
            font-size: 1.1rem;
            font-weight: 600;
            color: #f8fafc;
            margin-bottom: 1rem;
        }}

        .cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1rem;
            margin-bottom: 2.5rem;
        }}

        .card {{
            background: #1e293b;
            border-radius: 12px;
            padding: 1.25rem;
            position: relative;
            overflow: hidden;
        }}

        .card-icon {{
            font-size: 1.3rem;
            margin-bottom: 0.5rem;
        }}

        .card-count {{
            font-size: 2rem;
            font-weight: 700;
            color: #f8fafc;
        }}

        .card-label {{
            font-size: 0.85rem;
            color: #94a3b8;
            margin-bottom: 0.75rem;
        }}

        .card-bar {{
            height: 4px;
            border-radius: 2px;
            opacity: 0.8;
        }}

        /* Total badge */
        .total-banner {{
            text-align: center;
            margin-bottom: 2.5rem;
        }}

        .total-badge {{
            display: inline-block;
            background: linear-gradient(135deg, #3b82f6, #8b5cf6);
            color: white;
            font-size: 1.1rem;
            font-weight: 600;
            padding: 0.6rem 2rem;
            border-radius: 50px;
        }}

        /* Test table */
        .table-wrap {{
            overflow-x: auto;
            margin-bottom: 2.5rem;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        th {{
            text-align: left;
            padding: 0.75rem 1rem;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #64748b;
            border-bottom: 1px solid #1e293b;
        }}

        td {{
            padding: 0.75rem 1rem;
            border-bottom: 1px solid #1e293b;
            font-size: 0.9rem;
        }}

        tr:hover {{
            background: #1e293b;
        }}

        .row-num {{
            color: #475569;
            width: 40px;
        }}

        .test-name code {{
            background: #1e293b;
            padding: 0.15rem 0.5rem;
            border-radius: 4px;
            font-size: 0.85rem;
            color: #38bdf8;
        }}

        .test-desc {{
            color: #94a3b8;
            font-size: 0.85rem;
        }}

        /* Badges */
        .badge {{
            display: inline-block;
            padding: 0.2rem 0.6rem;
            border-radius: 50px;
            font-size: 0.75rem;
            font-weight: 500;
        }}

        .badge-happy {{ background: #052e16; color: #22c55e; }}
        .badge-negative {{ background: #450a0a; color: #ef4444; }}
        .badge-edge {{ background: #451a03; color: #f59e0b; }}
        .badge-boundary {{ background: #172554; color: #3b82f6; }}

        /* Code block */
        .code-section {{
            margin-bottom: 2.5rem;
        }}

        .code-toggle {{
            background: #1e293b;
            color: #94a3b8;
            border: 1px solid #334155;
            padding: 0.5rem 1.25rem;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.9rem;
            margin-bottom: 1rem;
            display: inline-block;
        }}

        .code-toggle:hover {{
            background: #334155;
            color: #e2e8f0;
        }}

        .code-block {{
            background: #1e293b;
            border-radius: 12px;
            padding: 1.5rem;
            overflow-x: auto;
            display: none;
        }}

        .code-block.visible {{
            display: block;
        }}

        .code-block pre {{
            margin: 0;
            font-family: 'Cascadia Code', 'Fira Code', 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            line-height: 1.7;
            color: #e2e8f0;
            white-space: pre;
        }}

        /* Footer */
        .footer {{
            text-align: center;
            padding-top: 2rem;
            border-top: 1px solid #1e293b;
            color: #475569;
            font-size: 0.8rem;
        }}

        .footer a {{
            color: #38bdf8;
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>&#x1F916; <span>AI Test Case Generator</span> — Report</h1>
            <p class="subtitle">Auto-generated test coverage summary</p>
        </div>

        <div class="meta">
            <div class="meta-item">
                <span class="meta-label">Source</span>
                <span class="meta-value">{escape(source)}</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">Format</span>
                <span class="meta-value">{escape(format.title())}</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">Provider</span>
                <span class="meta-value">{escape(provider)}</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">Generated</span>
                <span class="meta-value">{timestamp}</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">Test File</span>
                <span class="meta-value">{escape(test_filepath)}</span>
            </div>
        </div>

        <div class="total-banner">
            <span class="total-badge">&#x1F9EA; {total_tests} Test Cases Generated</span>
        </div>

        <h2 class="section-title">Coverage by Category</h2>
        <div class="cards">
            {category_cards}
        </div>

        <h2 class="section-title">Test Case Breakdown</h2>
        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Test Name</th>
                        <th>Category</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>
                    {test_rows}
                </tbody>
            </table>
        </div>

        <div class="code-section">
            <h2 class="section-title">Generated Code</h2>
            <button class="code-toggle" onclick="document.getElementById('codeBlock').classList.toggle('visible')">
                &#x1F4CB; Show / Hide Code
            </button>
            <div id="codeBlock" class="code-block">
                <pre>{escaped_code}</pre>
            </div>
        </div>

        <div class="footer">
            <p>Generated by <a href="https://github.com/FaraazSuffla/ai-test-case-generator">AI Test Case Generator</a> &middot; {timestamp}</p>
        </div>
    </div>
</body>
</html>"""

    # Save report
    safe_name = re.sub(r"[^a-zA-Z0-9]", "_", source)
    safe_name = re.sub(r"_+", "_", safe_name).strip("_")[:50]
    report_filename = f"report_{safe_name}.html"
    report_path = os.path.join(OUTPUT_DIR, report_filename)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html)

    # Try to open in browser
    try:
        abs_path = os.path.abspath(report_path)
        webbrowser.open(f"file://{abs_path}")
    except Exception:
        pass  # Silently skip if no browser available

    return report_path
