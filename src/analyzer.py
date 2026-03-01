"""Page analysis and accessibility tree extraction.

Uses Playwright to load a URL, extract forms, interactive elements,
navigation, and optionally the full accessibility tree for
context-aware test generation.
"""

from dataclasses import dataclass, field
from playwright.sync_api import sync_playwright, Page
from bs4 import BeautifulSoup
from rich.console import Console

console = Console()


@dataclass
class PageAnalysis:
    """Structured result of analysing a web page."""

    url: str
    title: str = ""
    forms: list[dict] = field(default_factory=list)
    interactive_elements: list[dict] = field(default_factory=list)
    nav_links: list[dict] = field(default_factory=list)
    accessibility_tree: str = ""

    def to_context_string(self, include_a11y: bool = False) -> str:
        """Format analysis as a string for LLM prompt context."""
        forms_str = "\n".join(
            f"  - Form: action={f.get('action', 'N/A')}, "
            f"fields={f.get('fields', [])}"
            for f in self.forms
        ) or "  None found"

        elements_str = "\n".join(
            f"  - {e['tag']} | role={e.get('role', 'N/A')} | "
            f"text='{e.get('text', '')[:50]}'"
            for e in self.interactive_elements[:30]
        ) or "  None found"

        nav_str = "\n".join(
            f"  - {n.get('text', 'N/A')[:40]} -> {n.get('href', 'N/A')[:60]}"
            for n in self.nav_links[:15]
        ) or "  None found"

        context = (
            f"URL: {self.url}\n"
            f"Title: {self.title}\n\n"
            f"Forms:\n{forms_str}\n\n"
            f"Interactive Elements:\n{elements_str}\n\n"
            f"Navigation Links:\n{nav_str}"
        )

        if include_a11y and self.accessibility_tree:
            context += f"\n\nAccessibility Tree:\n{self.accessibility_tree}"

        return context


def _extract_forms(soup: BeautifulSoup) -> list[dict]:
    """Extract form elements and their input fields."""
    forms = []
    for form in soup.find_all("form"):
        fields = []
        for inp in form.find_all(["input", "select", "textarea"]):
            fields.append({
                "tag": inp.name,
                "type": inp.get("type", "text"),
                "name": inp.get("name", inp.get("id", "unnamed")),
                "placeholder": inp.get("placeholder", ""),
                "required": inp.has_attr("required"),
                "aria_label": inp.get("aria-label", ""),
            })
        forms.append({
            "action": form.get("action", ""),
            "method": form.get("method", "GET").upper(),
            "fields": fields,
        })
    return forms


def _extract_interactive_elements(soup: BeautifulSoup) -> list[dict]:
    """Extract buttons, links, and other interactive elements."""
    elements = []
    selectors = ["button", "a[href]", "[role='button']", "[onclick]",
                 "input[type='submit']", "input[type='button']"]

    seen_texts = set()
    for selector in selectors:
        for el in soup.select(selector):
            text = el.get_text(strip=True)
            if text in seen_texts:
                continue
            seen_texts.add(text)
            elements.append({
                "tag": el.name,
                "text": text,
                "role": el.get("role", ""),
                "href": el.get("href", ""),
                "aria_label": el.get("aria-label", ""),
                "type": el.get("type", ""),
            })
    return elements


def _extract_nav_links(soup: BeautifulSoup) -> list[dict]:
    """Extract navigation links from nav elements and header."""
    links = []
    nav_areas = soup.find_all(["nav", "header"])
    if not nav_areas:
        nav_areas = [soup]  # Fallback to full page

    seen_hrefs = set()
    for area in nav_areas:
        for a in area.find_all("a", href=True):
            href = a["href"]
            if href in seen_hrefs or href.startswith("#"):
                continue
            seen_hrefs.add(href)
            links.append({
                "text": a.get_text(strip=True),
                "href": href,
            })
    return links


def _get_accessibility_tree(page: Page) -> str:
    """Extract a simplified accessibility tree snapshot from the page."""
    try:
        snapshot = page.accessibility.snapshot()
        if not snapshot:
            return "Accessibility tree not available."
        return _format_a11y_node(snapshot, depth=0)
    except Exception as e:
        return f"Could not extract accessibility tree: {e}"


def _format_a11y_node(node: dict, depth: int = 0) -> str:
    """Recursively format an accessibility tree node."""
    indent = "  " * depth
    role = node.get("role", "unknown")
    name = node.get("name", "")
    value = node.get("value", "")

    line = f"{indent}{role}"
    if name:
        line += f' "{name}"'
    if value:
        line += f" [{value}]"

    lines = [line]

    for child in node.get("children", []):
        lines.append(_format_a11y_node(child, depth + 1))

    # Limit total output to prevent token explosion
    result = "\n".join(lines)
    if depth == 0 and len(result) > 5000:
        result = result[:5000] + "\n... (truncated for token efficiency)"
    return result


def analyse_page(url: str, include_a11y: bool = False) -> PageAnalysis:
    """Analyse a web page and extract structured data for test generation.

    Args:
        url: The URL to analyse.
        include_a11y: Whether to extract the accessibility tree.

    Returns:
        A PageAnalysis dataclass with extracted page data.
    """
    console.print(f"\n[cyan]🔍 Analysing page:[/cyan] {url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(2000)  # Allow dynamic content to render

            html = page.content()
            title = page.title()

            soup = BeautifulSoup(html, "html.parser")

            analysis = PageAnalysis(
                url=url,
                title=title,
                forms=_extract_forms(soup),
                interactive_elements=_extract_interactive_elements(soup),
                nav_links=_extract_nav_links(soup),
            )

            if include_a11y:
                console.print("[cyan]♿ Extracting accessibility tree...[/cyan]")
                analysis.accessibility_tree = _get_accessibility_tree(page)

            console.print(
                f"[green]✓[/green] Found {len(analysis.forms)} form(s), "
                f"{len(analysis.interactive_elements)} interactive element(s), "
                f"{len(analysis.nav_links)} nav link(s)"
            )

            return analysis

        except Exception as e:
            console.print(f"[red]✗ Error analysing page:[/red] {e}")
            return PageAnalysis(url=url, title=f"Error: {e}")

        finally:
            browser.close()
