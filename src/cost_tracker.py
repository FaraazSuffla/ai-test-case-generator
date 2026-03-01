"""API usage and cost tracking.

Logs every LLM API call with token counts and estimated costs.
Data is persisted to a local JSON file for review.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

COST_LOG_FILE = "cost_log.json"

# Pricing per 1K tokens (as of 2026) — update as needed
PRICING = {
    "claude-sonnet-4-20250514": {"input": 0.003, "output": 0.015},
    "claude-haiku-4-5-20251001": {"input": 0.001, "output": 0.005},
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
}

console = Console()


def _load_log() -> list[dict]:
    """Load existing cost log from disk."""
    if not os.path.exists(COST_LOG_FILE):
        return []
    with open(COST_LOG_FILE, "r") as f:
        return json.load(f)


def _save_log(entries: list[dict]) -> None:
    """Persist cost log to disk."""
    with open(COST_LOG_FILE, "w") as f:
        json.dump(entries, f, indent=2, default=str)


def log_api_call(
    provider: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    purpose: str = "test_generation",
) -> dict:
    """Record an API call with token usage and estimated cost.

    Args:
        provider: 'anthropic' or 'openai'
        model: Model identifier string
        input_tokens: Number of input/prompt tokens
        output_tokens: Number of output/completion tokens
        purpose: What the call was used for

    Returns:
        The logged entry dict including estimated cost.
    """
    pricing = PRICING.get(model, {"input": 0.003, "output": 0.015})
    cost = (
        (input_tokens / 1000) * pricing["input"]
        + (output_tokens / 1000) * pricing["output"]
    )

    entry = {
        "timestamp": datetime.now().isoformat(),
        "provider": provider,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "estimated_cost_usd": round(cost, 6),
        "purpose": purpose,
    }

    entries = _load_log()
    entries.append(entry)
    _save_log(entries)

    return entry


def get_cost_summary(days: Optional[int] = None) -> dict:
    """Calculate cost summary, optionally filtered to recent N days.

    Args:
        days: If provided, only include entries from the last N days.

    Returns:
        Summary dict with totals and per-provider breakdown.
    """
    entries = _load_log()

    if days is not None:
        cutoff = datetime.now() - timedelta(days=days)
        entries = [
            e
            for e in entries
            if datetime.fromisoformat(e["timestamp"]) >= cutoff
        ]

    total_requests = len(entries)
    total_tokens = sum(e["total_tokens"] for e in entries)
    total_cost = sum(e["estimated_cost_usd"] for e in entries)

    # Per-provider breakdown
    providers: dict[str, dict] = {}
    for entry in entries:
        key = f"{entry['provider']} ({entry['model']})"
        if key not in providers:
            providers[key] = {"requests": 0, "cost": 0.0}
        providers[key]["requests"] += 1
        providers[key]["cost"] += entry["estimated_cost_usd"]

    return {
        "total_requests": total_requests,
        "total_tokens": total_tokens,
        "total_cost_usd": round(total_cost, 2),
        "providers": providers,
    }


def display_cost_summary() -> None:
    """Print a rich-formatted cost summary to the terminal."""
    all_time = get_cost_summary()
    last_week = get_cost_summary(days=7)

    if all_time["total_requests"] == 0:
        console.print(
            "\n[dim]No API calls logged yet. Generate some tests first![/dim]\n"
        )
        return

    lines = [
        f"Total requests:    {all_time['total_requests']}",
        f"Total tokens:      {all_time['total_tokens']:,}",
        f"Estimated cost:    ${all_time['total_cost_usd']:.2f}",
        "",
        f"Last 7 days:       {last_week['total_requests']} requests \u00b7 ${last_week['total_cost_usd']:.2f}",
        "",
        "Provider breakdown:",
    ]

    for provider, data in all_time["providers"].items():
        lines.append(
            f"  {provider}: {data['requests']} req \u00b7 ${data['cost']:.2f}"
        )

    panel = Panel(
        "\n".join(lines),
        title="💰 API Cost Summary",
        border_style="green",
        width=58,
    )
    console.print(panel)
