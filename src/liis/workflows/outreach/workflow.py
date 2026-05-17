from __future__ import annotations

from pathlib import Path
from typing import Any

from ...index import Catalog, IndexEntry
from ...storage import RepositoryStore
from ...utils import slugify
from .targets import OutreachTarget, prepare_message


def build_outreach_brief(
    store: RepositoryStore,
    *,
    target: OutreachTarget,
    message: str,
    context: dict[str, Any] | None = None,
) -> tuple[Path, dict[str, Any]]:
    store.ensure_layout()
    payload = prepare_message(target, message)
    payload["context"] = context or {}
    filename = f"{slugify(target.username)}-{payload['prepared_at'].replace(':', '').replace('-', '')[:15]}.json"
    path = store.save_json(f"data/outreach/{filename}", payload)
    Catalog(store).upsert(
        IndexEntry(
            id=f"outreach-{slugify(target.username)}-{payload['prepared_at'].replace(':', '').replace('-', '')[:15]}",
            kind="outreach",
            title=f"Outreach to {target.name}",
            captured_at=payload["prepared_at"],
            source_path=str(path.relative_to(store.paths.root)),
            tags=["outreach", target.username],
            related=[target.username],
            summary=message[:120],
        )
    )
    return path, payload
