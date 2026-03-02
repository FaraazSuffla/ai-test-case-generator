"""HTML report generator for test case summaries.

Creates a visual HTML report showing generated test cases,
their categories, coverage stats, and metadata. The report
is self-contained with inline CSS — no external dependencies.
"""

import os
import re
from datetime import datetime
from typing import Optional


OUTPUT_DIR = "output"


def _count_tests_by_category(code: str, format: str) -> dict:
    """Parse generated test code and count tests per category."""
    categories = {
        "happy_path": {"count": 0, "names": [], "icon": "✅", "label": "Happy Path"},
        "negative": {"count": 0, "names": [], "icon": "❌", "label": "Negative"},
        "edge_case": {"count": 0, "names": [], "icon": "🔄", "label": "Edge Cases"},
        "boundary": {"count": 0, "names": [], "icon": "📏", "label": "Boundary"},
    }

    if format == "playwright":
        current_category = None
        for line in code.split("\n"):
            line_lower = line.lower()
            if "class test" in line_lower or "class test" in line.lower():
                if "happypath" in line_lower or "happy_path" in line_lower:
                    current_category = "happy_path"
                elif "negative" in line_lower:
                    current_category = "negative"
                elif "edge" in line_lower:
                    current_category = "edge_case"
                elif "boundary" in line_lower:
                    current_category = "boundary"
            elif line.strip().startswith("def test_") and current_category:
                test_name = line.strip().split("(")[0].replace("def ", "")
                categories[current_category]["count"] += 1
                categories[current_category]["names"].append(test_name)

    elif format == "gherkin":
        current_category = None
        for line in code.split("\n"):
            line_stripped = line.strip()
            if line_stripped.startswith("@"):
                tags = line_stripped.lower()
                if "happy" in tags:
                    current_category = "happy_path"
                elif "negative" in tags:
                    current_category = "negative"
                elif "edge" in tags:
                    current_category = "edge_case"
                elif "boundary" in tags:
                    current_category = "boundary"
            elif line_stripped.startswith("Scenario:") or line_stripped.startswith("Scenario Outline:"):
                if current_category:
                    name = line_stripped.split(":", 1)[1].strip()
                    categories[current_category]["count"] += 1
                    categories[current_category]["names"].append(name)

    return categories


def _generate_html(
    categories: dict,
    source: str,
    format: str,
    provider: str,
    test_code: str,
    filepath: str,
) -> str:
    """Generate the full HTML report content."""
    total_tests = sum(c["count"] for c in categories.values())
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Build category cards
    category_cards = ""
    for key, cat in categories.items():
        if cat["count"] == 0:
            continue
        test_list = "".join(
            f'<li>{name}</li>' for name in cat["names"]
        )
        percentage = round((cat["count"] / total_tests) * 100) if total_tests > 0 else 0
        category_cards += f"""
        <div class="card">
            <div class="card-header">
                <span class="card-icon">{cat['icon']}</span>
                <span class="card-title">{cat['label']}</span>
                <span class="card-count">{cat['count']}</span>
            </div>
            <div class="card-bar">
                <div class="card-bar-fill" style="width: {percentage}%"></div>
            </div>
            <ul class="test-list">{test_list}</ul>
        </div>"""

    # Escape the code for HTML display
    escaped_code = (
        test_code
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Generation Report — AI Test Case Generator</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            line-height: 1.6;
        }}
        .container {{ max-width: 960px; margin: 0 auto; padding: 2rem 1.5rem; }}

        /* Header */
        .header {{
            text-align: center;
            margin-bottom: 2.5rem;
            padding-bottom: 2rem;
            border-bottom: 1px solid #1e293b;
        }}
        .header h1 {{
            font-size: 1.75rem;
            font-weight: 700;
            color: #f8fafc;
            margin-bottom: 0.5rem;
        }}
        .header h1 span {{ color: #38bdf8; }}
        .header p {{ color: #94a3b8; font-size: 0.9rem; }}

        /* Meta info */
        .meta {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        .meta-item {{
            background: #1e293b;
            border-radius: 8px;
            padding: 1rem 1.25rem;
        }}
        .meta-label {{ font-size: 0.75rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; }}
        .meta-value {{ font-size: 1rem; color: #f1f5f9; font-weight: 600; margin-top: 0.25rem; word-break: break-all; }}

        /* Stats banner */
        .stats {{
            display: flex;
            justify-content: center;
            gap: 2.5rem;
            margin-bottom: 2.5rem;
            padding: 1.5rem;
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border: 1px solid #334155;
            border-radius: 12px;
        }}
        .stat {{ text-align: center; }}
        .stat-number {{ font-size: 2rem; font-weight: 800; color: #38bdf8; }}
        .stat-label {{ font-size: 0.8rem; color: #94a3b8; margin-top: 0.1rem; }}

        /* Category cards */
        .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); gap: 1.25rem; margin-bottom: 2.5rem; }}
        .card {{
            background: #1e293b;
            border-radius: 10px;
            padding: 1.25rem;
            border: 1px solid #334155;
        }}
        .card-header {{ display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem; }}
        .card-icon {{ font-size: 1.25rem; }}
        .card-title {{ font-weight: 600; color: #f1f5f9; flex: 1; }}
        .card-count {{
            background: #38bdf8;
            color: #0f172a;
            font-size: 0.8rem;
            font-weight: 700;
            padding: 0.15rem 0.6rem;
            border-radius: 999px;
        }}
        .card-bar {{ height: 4px; background: #334155; border-radius: 4px; margin-bottom: 0.75rem; }}
        .card-bar-fill {{ height: 100%; background: #38bdf8; border-radius: 4px; transition: width 0.5s ease; }}
        .test-list {{ list-style: none; }}
        .test-list li {{
            font-size: 0.85rem;
            color: #cbd5e1;
            padding: 0.3rem 0;
            border-bottom: 1px solid #1e293b;
            font-family: 'SF Mono', 'Fira Code', monospace;
        }}
        .test-list li:last-child {{ border-bottom: none; }}

        /* Code block */
        .code-section {{ margin-bottom: 2rem; }}
        .code-section h2 {{
            font-size: 1.1rem;
            color: #f1f5f9;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .code-block {{
            background: #0d1117;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 1.25rem;
            overflow-x: auto;
            max-height: 500px;
            overflow-y: auto;
        }}
        .code-block pre {{
            font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', monospace;
            font-size: 0.82rem;
            color: #c9d1d9;
            line-height: 1.5;
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
        .footer a {{ color: #38bdf8; text-decoration: none; }}
        .footer a:hover {{ text-decoration: underline; }}

        @media (max-width: 600px) {{
            .cards {{ grid-template-columns: 1fr; }}
            .stats {{ flex-direction: column; gap: 1rem; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 <span>AI Test Case Generator</span> — Report</h1>
            <p>Auto-generated test coverage summary</p>
        </div>

        <div class="meta">
            <div class="meta-item">
                <div class="meta-label">Source</div>
                <div class="meta-value">{source}</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">Format</div>
                <div class="meta-value">{'Playwright (Python)' if format == 'playwright' else 'Gherkin (.feature)'}</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">Provider</div>
                <div class="meta-value">{provider}</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">Generated</div>
                <div class="meta-value">{timestamp}</div>
            </div>
        </div>

        <div class="stats">
            <div class="stat">
                <div class="stat-number">{total_tests}</div>
                <div class="stat-label">Total Tests</div>
            </div>
            <div class="stat">
                <div class="stat-number">{sum(1 for c in categories.values() if c['count'] > 0)}</div>
                <div class="stat-label">Categories</div>
            </div>
            <div class="stat">
                <div class="stat-number">{'PW' if format == 'playwright' else 'BDD'}</div>
                <div class="stat-label">Framework</div>
            </div>
        </div>

        <div class="cards">
            {category_cards}
        </div>

        <div class="code-section">
            <h2>📄 Generated Test Code</h2>
            <div class="code-block">
                <pre>{escaped_code}</pre>
            </div>
        </div>

        <div class="footer">
            <p>Generated by <a href="https://github.com/FaraazSuffla/ai-test-case-generator">AI Test Case Generator</a> · {timestamp}</p>
        </div>
    </div>
</body>
</html>"""


def generate_report(
    test_code: str,
    source: str,
    format: str,
    provider: str,
    test_filepath: str,
) -> str:
    """Generate an HTML report for the generated test cases.

    Args:
        test_code: The generated test code content.
        source: The URL or description used to generate tests.
        format: 'playwright' or 'gherkin'.
        provider: The LLM provider or 'demo'.
        test_filepath: Path to the saved test file.

    Returns:
        The path to the saved HTML report.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    categories = _count_tests_by_category(test_code, format)

    html = _generate_html(
        categories=categories,
        source=source,
        format=format,
        provider=provider,
        test_code=test_code,
        filepath=test_filepath,
    )

    # Generate report filename from source
    name = source.replace("https://", "").replace("http://", "")
    name = re.sub(r"[^a-zA-Z0-9]", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    if len(name) > 50:
        name = name[:50]

    report_path = os.path.join(OUTPUT_DIR, f"report_{name}.html")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html)

    return report_path
