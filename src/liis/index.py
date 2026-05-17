from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .storage import RepositoryStore
from .utils import dump_json, load_json


@dataclass(slots=True)
class IndexEntry:
    id: str
    kind: str
    title: str
    captured_at: str
    source_path: str
    tags: list[str]
    related: list[str]
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "title": self.title,
            "captured_at": self.captured_at,
            "source_path": self.source_path,
            "tags": self.tags,
            "related": self.related,
            "summary": self.summary,
        }


class Catalog:
    def __init__(self, store: RepositoryStore) -> None:
        self.store = store
        self.path = store.paths.index_dir / "catalog.json"
        self._cache: list[dict[str, Any]] | None = None

    def load(self) -> list[dict[str, Any]]:
        if self._cache is not None:
            return self._cache
        if not self.path.exists():
            self._cache = []
            return self._cache
        data = load_json(self.path)
        self._cache = data if isinstance(data, list) else []
        return self._cache  # type: ignore[return-value]

    def upsert(self, entry: IndexEntry) -> None:
        entries = self.load()
        self._cache = [item for item in entries if item.get("id") != entry.id]
        self._cache.append(entry.to_dict())
        dump_json(self.path, self._cache)

