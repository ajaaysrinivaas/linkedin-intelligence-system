from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from ..index import Catalog, IndexEntry
from ..models import Artifact
from ..storage import RepositoryStore
from ..utils import iso_now, parse_frontmatter, slugify
from .post import render_post_prompt


def build_post_draft(
    store: RepositoryStore,
    *,
    raw_path: Path,
    raw_text: str,
    body: str | None = None,
) -> tuple[Path, dict[str, Any]]:
    store.ensure_layout()
    meta, content = parse_frontmatter(raw_text)
    meta = meta  # type: ignore[assignment]
    if "template" not in meta:
        raise ValueError(f"Missing 'template' in post frontmatter: {raw_path}")
    if "title" not in meta:
        raise ValueError(f"Missing 'title' in post frontmatter: {raw_path}")
    template_name = str(meta["template"])
    title = str(meta["title"])
    tags_val = meta.get("tags", [])
    if not isinstance(tags_val, list):
        raise ValueError(f"Post frontmatter 'tags' must be a list: {raw_path}")
    tags: list[str] = [str(tag) for tag in tags_val]  # type: ignore[misc]
    prompt = render_post_prompt(content, template_name, tags=tags, root=store.paths.root)
    captured_at = iso_now()
    draft_body = body or prompt
    artifact = Artifact(
        id=f"post-{slugify(title)}-{captured_at.replace(':', '').replace('-', '')[:15]}",
        kind="post-draft",
        title=title,
        captured_at=captured_at,
        source={"template": template_name, "source_file": str(raw_path)},
        summary="Post draft prepared from raw idea",
        tags=tags,
        raw={
            "frontmatter": meta,
            "raw_content": content,
            "prompt": prompt,
            "body": draft_body,
        },
    )
    frontmatter: dict[str, Any] = {  # type: ignore[assignment]
        "id": artifact.id,
        "title": artifact.title,
        "status": "draft",
        "tags": tags,
        "image": {"enabled": False, "path": None, "alt": None},
        "created_at": artifact.captured_at,
        "source_file": artifact.source["source_file"],
    }
    markdown = "---\n" + yaml.safe_dump(frontmatter, sort_keys=False).strip() + "\n---\n\n" + draft_body.strip() + "\n"
    filename = f"{artifact.id}.md"
    path = store.save_text(f"data/posts/curated/{filename}", markdown)
    Catalog(store).upsert(
        IndexEntry(
            id=artifact.id,
            kind=artifact.kind,
            title=artifact.title,
            captured_at=artifact.captured_at,
            source_path=str(path.relative_to(store.paths.root)),
            tags=artifact.tags,
            related=[],
            summary=artifact.summary,
        )
    )
    return path, {"prompt": prompt, "frontmatter": meta, "body": draft_body}
