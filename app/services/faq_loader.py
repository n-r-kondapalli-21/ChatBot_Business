"""
FAQ data loader.

Responsible for reading and caching FAQ entries from the configured data source.
The interface is deliberately simple so that the underlying storage (JSON file,
SQL database, NoSQL store, etc.) can be swapped without touching any other module.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import List

from app.models.schemas import FAQItem

logger = logging.getLogger(__name__)


class FAQLoader:
    """
    Loads FAQ data from a JSON file and exposes it as a list of FAQItem objects.

    Design note
    -----------
    To swap the storage back-end (e.g., switch to a PostgreSQL table), subclass
    this class and override `_load_raw()`.  Everything else stays the same.
    """

    def __init__(self, file_path: str) -> None:
        self._file_path = Path(file_path)
        self._faqs: List[FAQItem] = []

    # ── Public interface ──────────────────────────────────────────────────────

    def load(self) -> None:
        """Read the data source and populate the in-memory FAQ list."""
        raw = self._load_raw()
        self._faqs = [FAQItem(**item) for item in raw]
        logger.info("Loaded %d FAQ entries from '%s'.", len(self._faqs), self._file_path)

    def get_all(self) -> List[FAQItem]:
        """Return all FAQ entries."""
        return list(self._faqs)

    def count(self) -> int:
        """Return the total number of loaded FAQ entries."""
        return len(self._faqs)

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _load_raw(self) -> List[dict]:
        """Read the JSON file and return the raw list of dictionaries."""
        if not self._file_path.exists():
            raise FileNotFoundError(
                f"FAQ file not found at path: {self._file_path}"
            )

        with self._file_path.open(encoding="utf-8") as fh:
            data = json.load(fh)

        if not isinstance(data, list):
            raise ValueError(
                f"Expected a JSON array in '{self._file_path}', got {type(data).__name__}."
            )

        return data
