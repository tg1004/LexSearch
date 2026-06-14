"""Scrape judgements from indiankanoon.org with rate limiting and checkpointing."""

from __future__ import annotations

import logging
import re
import time
from pathlib import Path
from urllib.parse import quote, urljoin

import requests
from bs4 import BeautifulSoup, Tag
from tqdm import tqdm

from data_pipeline.config import RAW_DIR, PipelineSettings, ensure_data_dirs
from data_pipeline.models import RawDocument
from data_pipeline.scraper.scraper_config import (
    CONTENT_SELECTORS,
    DOC_ID_PATTERN,
    FALLBACK_SEARCH_TERMS,
    MAX_PAGES_PER_QUERY,
    MIN_JUDGEMENT_TEXT_LENGTH,
    NOISE_SELECTORS,
    SEARCH_DOCTYPES,
    SKIP_TITLE_KEYWORDS,
    TITLE_SELECTORS,
    USER_AGENT,
    YEAR_END,
    YEAR_START,
)
from data_pipeline.utils import append_jsonl, load_existing_ids

logger = logging.getLogger(__name__)
DOC_LINK_RE = re.compile(DOC_ID_PATTERN)


class IndianKanoonScraper:
    def __init__(self, settings: PipelineSettings | None = None) -> None:
        self.settings = settings or PipelineSettings.from_env()
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "en-IN,en;q=0.9",
            }
        )
        self.output_path = RAW_DIR / "documents.jsonl"
        self.failed_path = RAW_DIR / "failed_ids.txt"

    def _get(self, url: str) -> requests.Response:
        response = self.session.get(url, timeout=self.settings.scrape_timeout_seconds)
        response.raise_for_status()
        time.sleep(self.settings.scrape_delay_seconds)
        return response

    def _search_url(self, query: str, pagenum: int) -> str:
        encoded = quote(query, safe="")
        return urljoin(
            self.settings.indiankanoon_base_url,
            f"/search/?formInput={encoded}&pagenum={pagenum}",
        )

    def discover_doc_ids(self, limit: int) -> list[tuple[str, str]]:
        """Discover document IDs via doctype+year search, then fallback keyword search."""
        discovered: list[tuple[str, str]] = []
        seen: set[str] = set()

        def add_ids(ids: list[str], court: str) -> None:
            for doc_id in ids:
                if doc_id in seen:
                    continue
                seen.add(doc_id)
                discovered.append((doc_id, court))
                if len(discovered) >= limit:
                    return

        # Primary: court doctype + year queries (returns real judgements).
        for source in SEARCH_DOCTYPES:
            court = source["court"]
            doctype = source["doctype"]
            for year in range(YEAR_START, YEAR_END + 1):
                query = f"doctypes:{doctype} year:{year}"
                ids = self._search_doc_ids(query)
                add_ids(ids, court)
                if len(discovered) >= limit:
                    return discovered
                logger.info("Search '%s': +%s IDs (total %s)", query, len(ids), len(discovered))

        # Fallback: keyword + doctype queries.
        for term in FALLBACK_SEARCH_TERMS:
            for source in SEARCH_DOCTYPES[:3]:  # top courts first
                query = f"doctypes:{source['doctype']} {term}"
                ids = self._search_doc_ids(query)
                add_ids(ids, source["court"])
                if len(discovered) >= limit:
                    return discovered

        return discovered

    def _search_doc_ids(self, query: str) -> list[str]:
        ids: list[str] = []
        seen: set[str] = set()

        for pagenum in range(MAX_PAGES_PER_QUERY):
            url = self._search_url(query, pagenum)
            try:
                response = self._get(url)
            except requests.RequestException as exc:
                logger.warning("Search failed for '%s' page %s: %s", query, pagenum, exc)
                break

            page_ids = self._extract_doc_ids_from_search(response.text)
            if not page_ids:
                break

            new_ids = [doc_id for doc_id in page_ids if doc_id not in seen]
            if not new_ids:
                break

            for doc_id in new_ids:
                seen.add(doc_id)
                ids.append(doc_id)

        return ids

    def _extract_doc_ids_from_search(self, html: str) -> list[str]:
        soup = BeautifulSoup(html, "lxml")
        ids: list[str] = []
        seen: set[str] = set()
        for anchor in soup.find_all("a", href=True):
            match = DOC_LINK_RE.search(anchor["href"])
            if not match:
                continue
            doc_id = match.group(1)
            if doc_id not in seen:
                seen.add(doc_id)
                ids.append(doc_id)
        return ids

    def fetch_document(self, doc_id: str, court_hint: str | None = None) -> RawDocument | None:
        url = urljoin(self.settings.indiankanoon_base_url, f"/doc/{doc_id}/")
        try:
            response = self._get(url)
        except requests.RequestException as exc:
            logger.warning("Failed to fetch doc %s: %s", doc_id, exc)
            self._record_failure(doc_id)
            return None

        return self._parse_document_page(doc_id=doc_id, url=url, html=response.text, court_hint=court_hint)

    def _parse_document_page(
        self,
        doc_id: str,
        url: str,
        html: str,
        court_hint: str | None,
    ) -> RawDocument | None:
        soup = BeautifulSoup(html, "lxml")

        title = self._extract_title(soup)
        if self._should_skip_title(title):
            logger.info("Skipping non-judgement doc %s: %s", doc_id, title)
            self._record_failure(doc_id)
            return None

        full_text = self._extract_content(soup)
        if not full_text or len(full_text.strip()) < MIN_JUDGEMENT_TEXT_LENGTH:
            logger.warning("Doc %s has insufficient text (%s chars)", doc_id, len(full_text or ""))
            self._record_failure(doc_id)
            return None

        if not title:
            title = f"Judgement {doc_id}"

        return RawDocument(
            id=doc_id,
            title=title[:500],
            full_text=full_text,
            url=url,
            court_hint=court_hint,
        )

    def _should_skip_title(self, title: str) -> bool:
        lowered = title.lower()
        return any(keyword in lowered for keyword in SKIP_TITLE_KEYWORDS)

    def _extract_title(self, soup: BeautifulSoup) -> str:
        for selector in TITLE_SELECTORS:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(" ", strip=True)
                if text and text.lower() not in {"indiankanoon", "indian kanoon"}:
                    return text
        return ""

    def _extract_content(self, soup: BeautifulSoup) -> str:
        for selector in CONTENT_SELECTORS:
            element = soup.select_one(selector)
            if element:
                text = self._clean_content_element(element)
                if len(text) >= MIN_JUDGEMENT_TEXT_LENGTH:
                    return text

        candidates = soup.find_all(["article", "div", "section"])
        best = ""
        for candidate in candidates:
            text = self._clean_content_element(candidate)
            if len(text) > len(best):
                best = text
        return best

    def _clean_content_element(self, element: Tag) -> str:
        fragment = BeautifulSoup(str(element), "lxml")
        root = fragment.find(element.name) or fragment

        for selector in NOISE_SELECTORS:
            for node in root.select(selector):
                node.decompose()

        return root.get_text("\n", strip=True)

    def _record_failure(self, doc_id: str) -> None:
        self.failed_path.parent.mkdir(parents=True, exist_ok=True)
        with self.failed_path.open("a", encoding="utf-8") as handle:
            handle.write(f"{doc_id}\n")

    def scrape(self, limit: int | None = None) -> Path:
        ensure_data_dirs()
        target = limit or self.settings.scrape_target_count
        existing_ids = load_existing_ids(self.output_path)
        logger.info("Resuming scrape: %s documents already saved", len(existing_ids))

        if len(existing_ids) >= target:
            logger.info("Target already met (%s >= %s)", len(existing_ids), target)
            return self.output_path

        needed = target - len(existing_ids)
        candidates = self.discover_doc_ids(limit=needed + len(existing_ids))
        candidates = [(doc_id, court) for doc_id, court in candidates if doc_id not in existing_ids]

        if not candidates:
            raise RuntimeError("No document IDs discovered. Check network access to indiankanoon.org")

        logger.info("Fetching %s documents...", min(needed, len(candidates)))

        saved = 0
        for doc_id, court_hint in tqdm(candidates[:needed], desc="Scraping judgements"):
            document = self.fetch_document(doc_id, court_hint=court_hint)
            if document:
                append_jsonl(self.output_path, document.to_dict())
                saved += 1

        logger.info("Scrape complete: %s new documents saved to %s", saved, self.output_path)
        return self.output_path


def scrape_documents(limit: int | None = None, settings: PipelineSettings | None = None) -> Path:
    scraper = IndianKanoonScraper(settings=settings)
    return scraper.scrape(limit=limit)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    scrape_documents()
