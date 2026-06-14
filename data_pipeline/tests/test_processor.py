from datetime import date

from data_pipeline.models import ProcessedDocument, RawDocument
from data_pipeline.processor.chunker import chunk_document
from data_pipeline.processor.metadata_extractor import extract_metadata
from data_pipeline.processor.text_cleaner import clean_text


def test_clean_text_removes_artifacts():
    raw = "Hello\x0cworld\n\n\n\nPage 2 of 10\nTest"
    cleaned = clean_text(raw)
    assert "\x0c" not in cleaned
    assert "Page 2 of 10" not in cleaned
    assert "Hello" in cleaned


def test_chunk_document_overlap():
    text = "A" * 500 + ". " + "B" * 500 + ". " + "C" * 500
    doc = ProcessedDocument(id="1", title="Test", full_text=text, url="http://example.com")
    chunks = chunk_document(doc)
    assert len(chunks) >= 2
    assert all(len(chunk.text) <= 900 for chunk in chunks)


def test_extract_metadata():
    raw = RawDocument(
        id="123",
        title="Privacy Case",
        full_text=(
            "IN THE SUPREME COURT OF INDIA\n"
            "Coram: Hon'ble Mr. Justice A, Hon'ble Mr. Justice B\n"
            "24 August, 2017\n"
            "This writ petition under Article 21 concerns fundamental rights.\n"
            "The appeal is dismissed."
        ),
        url="http://example.com/doc/123/",
        court_hint="Supreme Court",
    )
    metadata = extract_metadata(raw, raw.full_text)
    assert metadata.court == "Supreme Court"
    assert metadata.date == date(2017, 8, 24)
    assert metadata.case_type == "Constitutional"
    assert metadata.outcome == "Dismissed"
    assert len(metadata.judges) >= 1
