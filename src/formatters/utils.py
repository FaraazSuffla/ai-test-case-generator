"""Shared utilities for test file formatters."""

import re

FILENAME_MAX_LEN = 60


def _sanitise_name(source: str) -> str:
    """Convert a URL or description into a sanitised base name (no extension)."""
    name = source.replace("https://", "").replace("http://", "")
    name = re.sub(r"[^a-zA-Z0-9]", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    if len(name) > FILENAME_MAX_LEN:
        name = name[:FILENAME_MAX_LEN]
    return name
