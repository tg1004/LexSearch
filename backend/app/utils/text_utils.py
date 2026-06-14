import re


def clean_query_text(query: str) -> str:
    cleaned = query.strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned
