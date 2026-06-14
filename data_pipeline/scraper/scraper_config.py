"""Configuration for Indian Kanoon scraper."""

USER_AGENT = (
    "LexSearchBot/1.0 (+https://github.com/lexsearch; legal research pipeline; "
    "respectful crawl with rate limiting)"
)

# Court doctypes for Indian Kanoon search syntax: doctypes:supremecourt year:2020
SEARCH_DOCTYPES: list[dict[str, str]] = [
    {"court": "Supreme Court", "doctype": "supremecourt"},
    {"court": "Delhi High Court", "doctype": "delhi"},
    {"court": "Bombay High Court", "doctype": "bombay"},
    {"court": "Madras High Court", "doctype": "madras"},
    {"court": "Calcutta High Court", "doctype": "calcutta"},
    {"court": "Karnataka High Court", "doctype": "karnataka"},
    {"court": "Allahabad High Court", "doctype": "allahabad"},
    {"court": "Gujarat High Court", "doctype": "gujarat"},
    {"court": "Punjab and Haryana High Court", "doctype": "punjab"},
    {"court": "Rajasthan High Court", "doctype": "rajasthan"},
]

# Broad legal topics used if year/doctype searches are insufficient.
FALLBACK_SEARCH_TERMS: list[str] = [
    "bail",
    "privacy",
    "writ petition",
    "constitutional",
    "criminal appeal",
    "civil appeal",
    "land acquisition",
    "divorce",
    "income tax",
    "RTI",
    "dowry",
    "NDPS",
    "anticipatory bail",
    "habeas corpus",
]

YEAR_START = 2010
YEAR_END = 2025
MAX_PAGES_PER_QUERY = 50
RESULTS_PER_PAGE = 10
DOC_ID_PATTERN = r"/doc/(\d+)/?"

TITLE_SELECTORS = [".doc_title", "h1.doc_title", "h2.doc_title", "h1"]
CONTENT_SELECTORS = [
    "article.middle_column",
    "div.judgments",
    "div.docsource_main",
    "div.doc_content",
    "div.maindoc",
]

# Elements stripped before extracting judgement text.
NOISE_SELECTORS = [
    ".premium-banner",
    ".ad_doc",
    ".docoptions",
    "aside",
    "nav",
    "script",
    "style",
    "form",
    ".left_column",
    ".right_column",
]

# Skip statute/act pages — Phase 2 targets judgements.
SKIP_TITLE_KEYWORDS = [
    "section ",
    " in the indian penal code",
    " in the constitution of india",
    "entire act",
    "bare act",
]

MIN_JUDGEMENT_TEXT_LENGTH = 500
