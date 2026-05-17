from __future__ import annotations

from typing import Any

import yaml

from ...models import Artifact


def excerpt(text: str, max_length: int = 160) -> str:
    compact = " ".join(text.split())
    return compact if len(compact) <= max_length else compact[: max_length - 1].rstrip() + "…"


def render_markdown(artifact: Artifact, normalized: dict[str, Any], signals: dict[str, Any]) -> str:
    posts = normalized.get("posts", [])
    top_posts: list[Any] = (posts[:5] if isinstance(posts, list) else [])  # type: ignore[assignment]
    frontmatter: dict[str, Any] = {
        "id": artifact.id,
        "kind": artifact.kind,
        "title": artifact.title,
        "captured_at": artifact.captured_at,
        "source": artifact.source,
        "tags": artifact.tags,
        "post_count": normalized.get("total_posts", 0),
        "author_count": normalized.get("unique_authors", 0),
        "company_count": normalized.get("unique_companies", 0),
    }

    lines = ["---", yaml.safe_dump(frontmatter, sort_keys=False).strip(), "---", ""]
    lines.append(f"# {artifact.title}")
    lines.append("")
    lines.append("## Executive Summary")
    lines.append(f"- {normalized.get('total_posts', 0)} posts analyzed.")
    lines.append(f"- {normalized.get('unique_authors', 0)} authors and {normalized.get('unique_companies', 0)} companies observed.")
    lines.append("- The brief emphasizes what to do next, not the raw feed dump.")
    lines.append("")

    lines.append("## What Changed")
    if signals.get("hiring_posts"):
        lines.append("- Hiring activity is visible in the feed.")
    if signals.get("launch_posts"):
        lines.append("- Product launch or shipping activity is visible in the feed.")
    if signals.get("partnership_posts"):
        lines.append("- Partnership or integration activity is visible in the feed.")
    if not any([signals.get("hiring_posts"), signals.get("launch_posts"), signals.get("partnership_posts")]):
        lines.append("- No obvious directional change detected from the current feed sample.")
    lines.append("")

    _append_bullets(lines, "Key Themes", signals.get("themes", []), "theme")
    _append_bullets(lines, "Hot Keywords", signals.get("top_keywords", []), "keyword")

    lines.append("## Actionable Signals")
    if signals.get("hiring_posts"):
        lines.append("- Hiring signals found. Worth reviewing for warm outreach or job-market positioning.")
    if signals.get("launch_posts"):
        lines.append("- Product launch / shipping activity found. Good source for competitive intel.")
    if signals.get("partnership_posts"):
        lines.append("- Partnership / integration signals found. Good source for relationship mapping.")
    if not any([signals.get("hiring_posts"), signals.get("launch_posts"), signals.get("partnership_posts")]):
        lines.append("- No obvious action signals found in the current feed sample.")
    lines.append("")

    _append_bullets(lines, "People to Watch", signals.get("follow_up_people", []), "name")
    _append_bullets(lines, "Companies to Watch", signals.get("follow_up_companies", []), "company")

    lines.append("## Notable Posts")
    if top_posts:
        for post in top_posts:
            if not isinstance(post, dict):
                continue
            post_dict: dict[str, Any] = post  # type: ignore[assignment]
            author = str(post_dict.get("author") or post_dict.get("name") or "Unknown").strip()
            company = str(post_dict.get("company") or post_dict.get("author_company") or "").strip()
            label = author if not company else f"{author} | {company}"
            lines.append(f"- {label}: {excerpt(str(post_dict.get('excerpt') or post_dict.get('text') or ''))}")
    else:
        lines.append("- No posts available.")
    lines.append("")

    lines.append("## Next Actions")
    lines.append("- Review the highest-signal people and companies for outreach.")
    lines.append("- If hiring signals dominate, pivot to job-search / warm intro actions.")
    lines.append("- If launches dominate, track the companies for competitive updates.")
    return "\n".join(lines).strip() + "\n"


def _append_bullets(lines: list[str], title: str, items: list[dict[str, Any]], item_key: str) -> None:
    lines.append(f"## {title}")
    if not items:
        lines.append("- None found.")
        lines.append("")
        return
    for item in items:
        value = item.get(item_key, "Unknown")
        count = item.get("count")
        if count is not None:
            lines.append(f"- {value}: {count}")
        else:
            signals = "; ".join(item.get("signals", [])) or "Relevant source"
            lines.append(f"- {value}: {signals}")
    lines.append("")
