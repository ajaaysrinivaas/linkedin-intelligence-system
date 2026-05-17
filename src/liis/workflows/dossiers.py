from __future__ import annotations

from pathlib import Path
from typing import Any

from ..index import Catalog, IndexEntry
from ..models import Artifact, RunRecord
from ..normalization.dossiers import normalize_dossier_payload
from ..storage import RepositoryStore
from ..utils import iso_now, load_json, slugify
from .dossier import build_dossier_prompt, render_generic_dossier, render_people_dossier, render_people_search


def ingest_dossier(
    store: RepositoryStore,
    *,
    kind: str,
    raw_payload: dict[str, Any],
    source_name: str,
    captured_at: str | None = None,
) -> tuple[Path, dict[str, Any]]:
    store.ensure_layout()
    captured_at = captured_at or iso_now()
    normalized = normalize_dossier_payload(kind, raw_payload)
    prompt_template_name, prompt = build_dossier_prompt(root=store.paths.root, normalized=normalized)
    summary = normalized.get("summary", {})
    title = summary.get("name") or source_name
    if kind == "jobs":
        entries_val = normalized.get("entries")
        entries: list[Any] = entries_val if isinstance(entries_val, list) else []  # type: ignore[assignment]
        if entries:
            first_entry: Any = entries[0]
            if isinstance(first_entry, dict):
                first_entry_dict: dict[str, Any] = first_entry  # type: ignore[assignment]
                title = str(first_entry_dict.get("title") or title)
    elif kind == "companies":
        title = str(summary.get("name") or source_name)
    artifact = Artifact(
        id=f"{kind}-{slugify(source_name)}-{captured_at.replace(':', '').replace('-', '')[:15]}",
        kind=f"dossier:{kind}",
        title=title,
        captured_at=captured_at,
        source={"tool": raw_payload.get("tool"), "config_file": raw_payload.get("config_file"), "source_name": source_name},
        summary=summary.get("description", "") or summary.get("headline", "") or summary.get("query", "") or "",
        tags=[kind],
        related=[],
        raw={"input": raw_payload, "normalized": normalized, "prompt_template": prompt_template_name, "prompt": prompt},
    )
    relative_dir = f"dossiers/active/{kind}"
    if kind == "people" and "intelligence" in normalized:
        markdown = render_people_dossier(artifact, normalized)
    elif kind == "people" and normalized.get("summary", {}).get("match_found"):
        markdown = render_people_search(artifact, normalized)
    else:
        markdown = render_generic_dossier(artifact, normalized)
    path = store.save_markdown(f"{relative_dir}/{artifact.id}.md", markdown)
    Catalog(store).upsert(
        IndexEntry(
            id=artifact.id,
            kind=artifact.kind,
            title=artifact.title,
            captured_at=artifact.captured_at,
            source_path=str(path.relative_to(store.paths.root)),
            tags=artifact.tags,
            related=artifact.related,
            summary=artifact.summary or artifact.title,
        )
    )
    return path, {**normalized, "prompt_template": prompt_template_name, "prompt": prompt}


def ingest_dossier_file(
    store: RepositoryStore,
    *,
    kind: str,
    path: Path,
    source_name: str,
) -> tuple[Path, dict[str, Any]]:
    payload = load_json(path)
    if not isinstance(payload, dict):
        raise ValueError("Expected a JSON object")
    payload_dict: dict[str, Any] = payload  # type: ignore[assignment]
    timestamp_val = payload_dict.get("timestamp")
    return ingest_dossier(
        store,
        kind=kind,
        raw_payload=payload_dict,
        source_name=source_name,
        captured_at=str(timestamp_val) if timestamp_val else None,  # type: ignore[arg-type]
    )


def record_run(
    store: RepositoryStore,
    *,
    workflow: str,
    inputs: dict[str, Any],
    outputs: list[dict[str, Any]],
    notes: list[str] | None = None,
) -> Path:
    record = RunRecord(
        id=f"{workflow}-{iso_now().replace(':', '').replace('-', '')[:15]}",
        workflow=workflow,
        captured_at=iso_now(),
        inputs=inputs,
        outputs=outputs,
        notes=notes or [],
    )
    return store.save_run_record(record)
