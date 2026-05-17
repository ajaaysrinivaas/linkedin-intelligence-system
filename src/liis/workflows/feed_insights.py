from __future__ import annotations

from pathlib import Path
from typing import Any

from ..index import Catalog, IndexEntry
from ..models import Artifact
from ..normalization.feed import normalize_feed_payload
from ..storage import RepositoryStore
from ..utils import iso_now, load_json, slugify
from .feed import build_feed_prompt, collect_signals, render_markdown


def build_feed_insights(store: RepositoryStore, *, raw_feed: dict[str, Any], title: str | None = None) -> tuple[Path, dict[str, Any]]:
    store.ensure_layout()
    captured_at = iso_now()
    normalized = normalize_feed_payload(raw_feed)
    signals = collect_signals(normalized.get("posts", []))
    prompt_template_name, prompt = build_feed_prompt(
        root=store.paths.root,
        normalized=normalized,
        signals=signals,
    )
    resolved_title = title or f"Feed insights ({normalized['total_posts']} posts)"
    artifact_id = f"feed-insights-{slugify(resolved_title)}-{captured_at.replace(':', '').replace('-', '')[:15]}"

    artifact = Artifact(
        id=artifact_id,
        kind="feed-insights",
        title=resolved_title,
        captured_at=captured_at,
        source={
            "tool": raw_feed.get("tool"),
            "config_file": raw_feed.get("config_file"),
            "prompt_template": prompt_template_name,
        },
        summary=f"{normalized['total_posts']} feed posts analyzed",
        tags=["feed", "insights"],
        raw={
            "input": raw_feed,
            "normalized": normalized,
            "signals": signals,
            "prompt": prompt,
        },
    )
    body = render_markdown(artifact, normalized, signals)
    path = store.save_markdown(f"data/feed_insights/{artifact_id}.md", body)

    Catalog(store).upsert(
        IndexEntry(
            id=artifact_id,
            kind="feed-insights",
            title=resolved_title,
            captured_at=captured_at,
            source_path=str(path.relative_to(store.paths.root)),
            tags=["feed", "insights"],
            related=[],
            summary=f"{normalized['total_posts']} feed posts analyzed",
        )
    )
    return path, {**normalized, "signals": signals, "prompt": prompt}


def build_feed_insights_from_file(store: RepositoryStore, *, path: Path, title: str | None = None) -> tuple[Path, dict[str, Any]]:
    payload = load_json(path)
    if not isinstance(payload, dict):
        raise ValueError("Expected a JSON object")
    payload_dict: dict[str, Any] = payload  # type: ignore[assignment]
    return build_feed_insights(store, raw_feed=payload_dict, title=title)
