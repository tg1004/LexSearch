"""Remove formatting artifacts and normalize judgement text."""

from __future__ import annotations

import re
import unicodedata

# Patterns for common Indian Kanoon / PDF conversion artifacts.
ARTIFACT_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\x0c"), ""),  # form feed
    (re.compile(r"\u00a0"), " "),  # non-breaking space
    (re.compile(r"[\u200b-\u200d\ufeff]"), ""),  # zero-width chars
    (re.compile(r"-\s*\n\s*"), ""),  # hyphenated line breaks
    (re.compile(r"\n{3,}"), "\n\n"),  # excessive newlines
    (re.compile(r"[ \t]{2,}"), " "),  # repeated spaces
    (re.compile(r"^\s*Page \d+ of \d+\s*$", re.MULTILINE | re.IGNORECASE), ""),
    (re.compile(r"^\s*Downloaded on .*$", re.MULTILINE | re.IGNORECASE), ""),
    (re.compile(r"^\s*Indian Kanoon.*$", re.MULTILINE | re.IGNORECASE), ""),
    (re.compile(r"^\s*Share Link.*$", re.MULTILINE | re.IGNORECASE), ""),
    (re.compile(r"^\s*Free features.*$", re.MULTILINE | re.IGNORECASE), ""),
    (re.compile(r"^\s*Premium Member.*$", re.MULTILINE | re.IGNORECASE), ""),
]


def normalize_unicode(text: str) -> str:
    return unicodedata.normalize("NFKC", text)


def clean_text(text: str) -> str:
    """Clean raw judgement text for chunking and indexing."""
    if not text:
        return ""

    cleaned = normalize_unicode(text)

    for pattern, replacement in ARTIFACT_PATTERNS:
        cleaned = pattern.sub(replacement, cleaned)

    # Normalize line endings and trim each line.
    lines = [line.strip() for line in cleaned.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    lines = [line for line in lines if line]
    cleaned = "\n".join(lines)

    return cleaned.strip()
