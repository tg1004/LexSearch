"""Extract court, date, case type, outcome, and judges from judgement text."""

from __future__ import annotations

import re
from datetime import date, datetime

from data_pipeline.models import DocumentMetadata, RawDocument

MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "sept": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}

CASE_TYPE_KEYWORDS: dict[str, list[str]] = {
    "Constitutional": ["constitution", "article 14", "article 19", "article 21", "fundamental right", "writ petition"],
    "Criminal": ["ipc", "crpc", "criminal", "bail", "fir", "section 302", "section 420", "ndps", "pocso"],
    "Civil": ["civil suit", "specific relief", "contract", "damages", "injunction", "cpc"],
    "Family": ["divorce", "maintenance", "custody", "hindu marriage", "domestic violence", "dowry"],
    "Tax": ["income tax", "gst", "customs", "excise", "service tax", "taxation"],
    "Labour": ["industrial dispute", "labour", "workmen", "termination of service"],
    "Property": ["land acquisition", "property", "tenancy", "eviction", "real estate"],
}

OUTCOME_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bappeal\s+(?:is\s+)?dismissed\b", re.I), "Dismissed"),
    (re.compile(r"\bpetition\s+(?:is\s+)?dismissed\b", re.I), "Dismissed"),
    (re.compile(r"\bappeal\s+(?:is\s+)?allowed\b", re.I), "Allowed"),
    (re.compile(r"\bpetition\s+(?:is\s+)?allowed\b", re.I), "Allowed"),
    (re.compile(r"\bappeal\s+(?:is\s+)?partly\s+allowed\b", re.I), "Partly Allowed"),
    (re.compile(r"\bset\s+aside\b", re.I), "Set Aside"),
    (re.compile(r"\bremanded\b", re.I), "Remanded"),
    (re.compile(r"\bupheld\b", re.I), "Upheld"),
]

COURT_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"supreme\s+court\s+of\s+india", re.I), "Supreme Court"),
    (re.compile(r"delhi\s+high\s+court", re.I), "Delhi High Court"),
    (re.compile(r"bombay\s+high\s+court", re.I), "Bombay High Court"),
    (re.compile(r"madras\s+high\s+court", re.I), "Madras High Court"),
    (re.compile(r"calcutta\s+high\s+court", re.I), "Calcutta High Court"),
    (re.compile(r"karnataka\s+high\s+court", re.I), "Karnataka High Court"),
    (re.compile(r"allahabad\s+high\s+court", re.I), "Allahabad High Court"),
    (re.compile(r"gujarat\s+high\s+court", re.I), "Gujarat High Court"),
    (re.compile(r"punjab(?:\s+and\s+haryana)?\s+high\s+court", re.I), "Punjab and Haryana High Court"),
    (re.compile(r"rajasthan\s+high\s+court", re.I), "Rajasthan High Court"),
]

DATE_PATTERNS = [
    re.compile(
        r"\b(\d{1,2})(?:st|nd|rd|th)?\s+(January|February|March|April|May|June|July|August|September|October|November|December|"
        r"Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\s*,?\s*(\d{4})\b",
        re.I,
    ),
    re.compile(r"\b(\d{1,2})[-/](\d{1,2})[-/](\d{4})\b"),
    re.compile(r"\b(\d{4})[-/](\d{1,2})[-/](\d{1,2})\b"),
]

JUDGE_PATTERNS = [
    re.compile(r"(?:Coram|CORAM)\s*[:\-]\s*(.+?)(?:\n|$)", re.I),
    re.compile(r"(?:Before|BEFORE)\s*[:\-]\s*(.+?)(?:\n|$)", re.I),
    re.compile(r"(?:Hon['']ble|Honorable)\s+(?:Mr\.?\s+)?Justice\s+.+", re.I),
]


def parse_text_date(match: re.Match[str]) -> date | None:
    groups = match.groups()
    try:
        if len(groups) == 3 and (groups[1].isalpha() or groups[1].lower() in MONTHS):
            day = int(groups[0])
            month = MONTHS[groups[1].lower()]
            year = int(groups[2])
            return date(year, month, day)
        if len(groups) == 3 and len(groups[2]) == 4:
            # dd-mm-yyyy
            day, month, year = int(groups[0]), int(groups[1]), int(groups[2])
            return date(year, month, day)
        if len(groups) == 3 and len(groups[0]) == 4:
            # yyyy-mm-dd
            year, month, day = int(groups[0]), int(groups[1]), int(groups[2])
            return date(year, month, day)
    except ValueError:
        return None
    return None


def extract_date(text: str) -> date | None:
    head = text[:3000]
    for pattern in DATE_PATTERNS:
        match = pattern.search(head)
        if match:
            parsed = parse_text_date(match)
            if parsed and 1950 <= parsed.year <= datetime.now().year:
                return parsed
    return None


def extract_court(text: str, court_hint: str | None = None) -> str | None:
    if court_hint:
        return court_hint
    head = text[:5000]
    for pattern, court_name in COURT_PATTERNS:
        if pattern.search(head):
            return court_name
    return None


def extract_case_type(text: str) -> str | None:
    sample = text[:15000].lower()
    scores: dict[str, int] = {}
    for case_type, keywords in CASE_TYPE_KEYWORDS.items():
        score = sum(sample.count(keyword) for keyword in keywords)
        if score:
            scores[case_type] = score
    if not scores:
        return None
    return max(scores, key=scores.get)


def extract_outcome(text: str) -> str | None:
    tail = text[-5000:]
    for pattern, outcome in OUTCOME_PATTERNS:
        if pattern.search(tail):
            return outcome
    return None


def extract_judges(text: str) -> list[str]:
    head = text[:5000]
    judges: list[str] = []

    for pattern in JUDGE_PATTERNS[:2]:
        match = pattern.search(head)
        if match:
            segment = match.group(1)
            parts = re.split(r",|\band\b|;", segment)
            for part in parts:
                name = re.sub(r"\s+", " ", part).strip(" .")
                if name and len(name) > 3:
                    judges.append(name[:200])

    if not judges:
        for match in JUDGE_PATTERNS[2].finditer(head):
            judges.append(match.group(0).strip()[:200])

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: list[str] = []
    for judge in judges:
        key = judge.lower()
        if key not in seen:
            seen.add(key)
            unique.append(judge)
    return unique[:10]


def extract_metadata(document: RawDocument, cleaned_text: str) -> DocumentMetadata:
    return DocumentMetadata(
        court=extract_court(cleaned_text, document.court_hint),
        date=extract_date(cleaned_text),
        case_type=extract_case_type(cleaned_text),
        outcome=extract_outcome(cleaned_text),
        judges=extract_judges(cleaned_text),
    )
