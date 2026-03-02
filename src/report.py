"""HTML report generator for test case output.

Produces a polished, standalone HTML report showing generated test
cases with syntax highlighting, category breakdowns, and metadata.
Opens automatically in the default browser after generation.

Features:
- Category breakdown cards with test counts
- Collapsible sections per category with individual tests
- Pass/fail status column (pending until tests are executed)
- Export to PDF button (uses browser print)
- Full generated code in collapsible block
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
        current_tag = ""
        for line in test_code.split("\n"):
            stripped = line.strip()
            if stripped.startswith("@"):
                tags = stripped.lower()
                if "happy-path" in tags or "happy_path" in tags:
                    current_tag = "HappyPath"
                elif "negative" in tags:
                    current_tag = "Negative"
                elif "edge-case" in tags or "edge_case" in tags:
                    current_tag = "EdgeCases"
                elif "boundary" in tags:
                    current_tag = "Boundary"
            elif stripped.startswith("Scenario:") or stripped.startswith("Scenario Outline:"):
                name = stripped.split(":", 1)[1].strip()
                tests.append({
                    "name": name,
                    "class": current_tag or "Feature",
                    "description": "",
                })

    return tests


def _get_category_label(key: str) -> str:
    labels = {
        "happy_path": "Happy Path",
        "negative": "Negative",
        "edge_cases": "Edge Cases",
        "boundary": "Boundary",
    }
    return labels.get(key, key.replace("_", " ").title())


def _get_category_color(key: str) -> str:
    colors = {
        "happy_path": "#22c55e",
        "negative": "#ef4444",
        "edge_cases": "#f59e0b",
        "boundary": "#3b82f6",
    }
    return colors.get(key, "#6b7280")


def _get_category_icon(key: str) -> str:
    icons = {
        "happy_path": "&#x2705;",
        "negative": "&#x274C;",
        "edge_cases": "&#x1F504;",
        "boundary": "&#x1F4CF;",
    }
    return icons.get(key, "&#x1F4CB;")


def _get_category_key_from_class(cls: str) -> str:
    """Map a class name to a category key."""
    lower = cls.lower()
    if "happypath" in lower or "happy_path" in lower:
        return "happy_path"
    elif "negative" in lower:
        return "negative"
    elif "edgecase" in lower or "edge_case" in lower or "edge" in lower:
        return "edge_cases"
    elif "boundary" in lower:
        return "boundary"
    return "unknown"


def generate_report(
    test_code: str,
    source: str,
    format: str,
    provider: str,
    test_filepath: str,
) -> str:
    """Generate an HTML report for the generated test cases."""
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

    # Group tests by category for collapsible sections
    grouped_tests: dict[str, list] = {}
    for test in tests:
        cat_key = _get_category_key_from_class(test["class"])
        if cat_key not in grouped_tests:
            grouped_tests[cat_key] = []
        grouped_tests[cat_key].append(test)

    # Build collapsible category sections
    category_order = ["happy_path", "negative", "edge_cases", "boundary"]
    collapsible_sections = ""
    global_index = 0

    for cat_key in category_order:
        if cat_key not in grouped_tests:
            continue
        cat_tests = grouped_tests[cat_key]
        label = _get_category_label(cat_key)
        color = _get_category_color(cat_key)
        icon = _get_category_icon(cat_key)
        count = len(cat_tests)

        # Badge class
        badge_map = {
            "happy_path": "badge-happy",
            "negative": "badge-negative",
            "edge_cases": "badge-edge",
            "boundary": "badge-boundary",
        }
        badge_class = badge_map.get(cat_key, "badge-happy")

        # Build rows for this category
        rows = ""
        for test in cat_tests:
            global_index += 1
            desc = test["description"] or "—"
            rows += f"""
                    <tr>
                        <td class="row-num">{global_index}</td>
                        <td class="test-name"><code>{escape(test['name'])}</code></td>
                        <td class="test-desc">{escape(desc)}</td>
                        <td class="test-status"><span class="status-pending">&#x23F3; Pending</span></td>
                    </tr>"""

        collapsible_sections += f"""
        <div class="category-section">
            <button class="category-toggle" onclick="this.parentElement.classList.toggle('open')" style="border-left: 4px solid {color};">
                <span class="toggle-left">
                    <span class="toggle-arrow">&#x25B6;</span>
                    <span>{icon} {label}</span>
                    <span class="badge {badge_class}" style="margin-left: 0.5rem;">{count} test{"s" if count != 1 else ""}</span>
                </span>
            </button>
            <div class="category-content">
                <table>
                    <thead>
                        <tr>
                            <th style="width:40px">#</th>
                            <th>Test Name</th>
                            <th>Description</th>
                            <th style="width:110px">Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </div>
        </div>"""

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

        .header-actions {{
            margin-top: 1rem;
            display: flex;
            justify-content: center;
            gap: 0.75rem;
        }}

        .btn {{
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.5rem 1.25rem;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 500;
            cursor: pointer;
            border: 1px solid #334155;
            transition: all 0.2s;
        }}

        .btn-pdf {{
            background: #1e293b;
            color: #e2e8f0;
        }}

        .btn-pdf:hover {{
            background: #334155;
        }}

        .btn-expand {{
            background: #1e293b;
            color: #94a3b8;
        }}

        .btn-expand:hover {{
            background: #334155;
            color: #e2e8f0;
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

        .card-icon {{ font-size: 1.3rem; margin-bottom: 0.5rem; }}
        .card-count {{ font-size: 2rem; font-weight: 700; color: #f8fafc; }}
        .card-label {{ font-size: 0.85rem; color: #94a3b8; margin-bottom: 0.75rem; }}
        .card-bar {{ height: 4px; border-radius: 2px; opacity: 0.8; }}

        /* Total badge */
        .total-banner {{ text-align: center; margin-bottom: 2.5rem; }}

        .total-badge {{
            display: inline-block;
            background: linear-gradient(135deg, #3b82f6, #8b5cf6);
            color: white;
            font-size: 1.1rem;
            font-weight: 600;
            padding: 0.6rem 2rem;
            border-radius: 50px;
        }}

        /* Collapsible category sections */
        .category-section {{
            margin-bottom: 0.5rem;
        }}

        .category-toggle {{
            width: 100%;
            text-align: left;
            background: #1e293b;
            color: #e2e8f0;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 0.85rem 1.25rem;
            cursor: pointer;
            font-size: 0.95rem;
            font-weight: 500;
            display: flex;
            align-items: center;
            justify-content: space-between;
            transition: background 0.2s;
        }}

        .category-toggle:hover {{
            background: #334155;
        }}

        .toggle-left {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .toggle-arrow {{
            display: inline-block;
            transition: transform 0.2s;
            font-size: 0.7rem;
            color: #64748b;
        }}

        .category-section.open .toggle-arrow {{
            transform: rotate(90deg);
        }}

        .category-content {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease;
        }}

        .category-section.open .category-content {{
            max-height: 2000px;
        }}

        .category-content table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 0.25rem;
        }}

        .category-content th {{
            text-align: left;
            padding: 0.6rem 1rem;
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #64748b;
            border-bottom: 1px solid #1e293b;
        }}

        .category-content td {{
            padding: 0.6rem 1rem;
            border-bottom: 1px solid #1e293b;
            font-size: 0.85rem;
        }}

        .category-content tr:hover {{
            background: #1e293b;
        }}

        .row-num {{ color: #475569; width: 40px; }}

        .test-name code {{
            background: #0f172a;
            padding: 0.15rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            color: #38bdf8;
        }}

        .test-desc {{ color: #94a3b8; font-size: 0.8rem; }}

        /* Status badges */
        .test-status {{ text-align: center; }}

        .status-pending {{
            display: inline-block;
            padding: 0.15rem 0.6rem;
            border-radius: 50px;
            font-size: 0.7rem;
            font-weight: 500;
            background: #1c1917;
            color: #a8a29e;
        }}

        .status-pass {{
            display: inline-block;
            padding: 0.15rem 0.6rem;
            border-radius: 50px;
            font-size: 0.7rem;
            font-weight: 500;
            background: #052e16;
            color: #22c55e;
        }}

        .status-fail {{
            display: inline-block;
            padding: 0.15rem 0.6rem;
            border-radius: 50px;
            font-size: 0.7rem;
            font-weight: 500;
            background: #450a0a;
            color: #ef4444;
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
        .code-section {{ margin-bottom: 2.5rem; }}

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

        .code-toggle:hover {{ background: #334155; color: #e2e8f0; }}

        .code-block {{
            background: #1e293b;
            border-radius: 12px;
            padding: 1.5rem;
            overflow-x: auto;
            display: none;
        }}

        .code-block.visible {{ display: block; }}

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

        .footer a {{ color: #38bdf8; text-decoration: none; }}

        /* Print / PDF styles */
        @media print {{
            body {{ background: #fff; color: #1e293b; }}
            .container {{ max-width: 100%; padding: 0; }}
            .header {{ border-bottom-color: #e2e8f0; }}
            .header h1 {{ color: #0f172a; }}
            .header h1 span {{ color: #2563eb; }}
            .header .subtitle {{ color: #64748b; }}
            .header-actions {{ display: none; }}
            .meta {{ background: #f1f5f9; border: 1px solid #e2e8f0; }}
            .meta-label {{ color: #64748b; }}
            .meta-value {{ color: #0f172a; }}
            .total-badge {{ background: #2563eb !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
            .card {{ background: #f1f5f9; border: 1px solid #e2e8f0; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
            .card-count {{ color: #0f172a; }}
            .card-label {{ color: #64748b; }}
            .card-bar {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
            .category-toggle {{ background: #f1f5f9; border-color: #e2e8f0; color: #0f172a; }}
            .category-content {{ max-height: none !important; overflow: visible !important; }}
            .category-content th {{ color: #64748b; border-bottom-color: #e2e8f0; }}
            .category-content td {{ border-bottom-color: #e2e8f0; color: #1e293b; }}
            .test-name code {{ background: #f1f5f9; color: #2563eb; }}
            .test-desc {{ color: #64748b; }}
            .badge {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
            .badge-happy {{ background: #dcfce7 !important; color: #166534 !important; }}
            .badge-negative {{ background: #fee2e2 !important; color: #991b1b !important; }}
            .badge-edge {{ background: #fef3c7 !important; color: #92400e !important; }}
            .badge-boundary {{ background: #dbeafe !important; color: #1e40af !important; }}
            .status-pending {{ background: #f1f5f9 !important; color: #64748b !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
            .status-pass {{ background: #dcfce7 !important; color: #166534 !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
            .status-fail {{ background: #fee2e2 !important; color: #991b1b !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
            .code-section {{ display: none; }}
            .footer {{ border-top-color: #e2e8f0; color: #94a3b8; }}
            .footer a {{ color: #2563eb; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>&#x1F916; <span>AI Test Case Generator</span> — Report</h1>
            <p class="subtitle">Auto-generated test coverage summary</p>
            <div class="header-actions">
                <button class="btn btn-pdf" onclick="window.print()">&#x1F4C4; Export PDF</button>
                <button class="btn btn-expand" onclick="toggleAll()">&#x1F4C2; Expand / Collapse All</button>
            </div>
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
        <div class="category-sections">
            {collapsible_sections}
        </div>

        <div class="code-section" style="margin-top: 2.5rem;">
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

    <script>
        function toggleAll() {{
            const sections = document.querySelectorAll('.category-section');
            const allOpen = Array.from(sections).every(s => s.classList.contains('open'));
            sections.forEach(s => {{
                if (allOpen) {{
                    s.classList.remove('open');
                }} else {{
                    s.classList.add('open');
                }}
            }});
        }}
    </script>
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
        pass

    return report_path
