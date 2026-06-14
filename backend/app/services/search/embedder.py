"""sentence-transformers wrapper for query embeddings."""

from __future__ import annotations

import asyncio
import logging
from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)


class Embedder:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._model: SentenceTransformer | None = None

    def load(self) -> None:
        if self._model is None:
            logger.info("Loading embedding model %s ...", self.settings.embedding_model)
            self._model = SentenceTransformer(self.settings.embedding_model)
            logger.info("Embedding model loaded")

    def _encode(self, text: str) -> list[float]:
        if self._model is None:
            self.load()
        assert self._model is not None
        vector = self._model.encode(text, normalize_embeddings=True)
        return vector.tolist()

    async def embed_query(self, text: str) -> list[float]:
        return await asyncio.to_thread(self._encode, text)


@lru_cache
def get_embedder() -> Embedder:
    return Embedder()
