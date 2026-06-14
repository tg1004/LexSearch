"""Split documents into semantic chunks with overlap."""

from __future__ import annotations

from langchain_text_splitters import RecursiveCharacterTextSplitter

from data_pipeline.models import DocumentChunk, ProcessedDocument

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
SEPARATORS = ["\n\n", "\n", ". ", " "]


def build_splitter(chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP) -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=SEPARATORS,
        length_function=len,
    )


def chunk_document(document: ProcessedDocument, splitter: RecursiveCharacterTextSplitter | None = None) -> list[DocumentChunk]:
    splitter = splitter or build_splitter()
    text = document.full_text
    if not text:
        return []

    chunks: list[DocumentChunk] = []
    search_start = 0

    for index, chunk_text in enumerate(splitter.split_text(text)):
        if not chunk_text.strip():
            continue

        char_start = text.find(chunk_text, search_start)
        if char_start == -1:
            char_start = search_start
        char_end = char_start + len(chunk_text)
        search_start = max(0, char_end - CHUNK_OVERLAP)

        chunks.append(
            DocumentChunk(
                document_id=document.id,
                chunk_index=index,
                text=chunk_text,
                title=document.title,
                court=document.court,
                date=document.date,
                case_type=document.case_type,
                char_start=char_start,
                char_end=char_end,
            )
        )

    return chunks


def chunk_documents(documents: list[ProcessedDocument]) -> list[DocumentChunk]:
    splitter = build_splitter()
    all_chunks: list[DocumentChunk] = []
    for document in documents:
        all_chunks.extend(chunk_document(document, splitter=splitter))
    return all_chunks
