from __future__ import annotations

from pathlib import Path
from typing import Any

from ...config import load_feed_prompt_template
from .signals import rank_posts


def build_feed_prompt(
    *,
    root: Path,
    normalized: dict[str, Any],
    signals: dict[str, Any],
) -> tuple[str, str]:
    template = load_feed_prompt_template(root=root)
    posts = normalized.get("posts", [])
    top_posts: list[dict[str, Any]] = rank_posts([post for post in posts if isinstance(post, dict)], limit=8)
    feed_summary = "\n".join(
        [
            f"- Posts analyzed: {normalized.get('total_posts', 0)}",
            f"- Unique authors: {normalized.get('unique_authors', 0)}",
            f"- Unique companies: {normalized.get('unique_companies', 0)}",
        ]
    )
    top_posts_text = "\n".join(
        f"- {post.get('author') or 'Unknown'}"
        + (f" | {post.get('company')}" if post.get("company") else "")
        + (f" | {post.get('timestamp')}" if post.get("timestamp") else "")
        + f": {post.get('excerpt') or post.get('text') or ''}"
        for post in top_posts
    ) or "- None"
    signals_text = "\n".join(
        [
            f"- Themes: {', '.join(item['theme'] for item in signals.get('themes', [])) or 'None'}",
            f"- People: {', '.join(item['name'] for item in signals.get('follow_up_people', [])) or 'None'}",
            f"- Companies: {', '.join(item['company'] for item in signals.get('follow_up_companies', [])) or 'None'}",
        ]
    )
    prompt = template.prompt.format(feed_summary=feed_summary, top_posts=top_posts_text, signals=signals_text)
    return template.name, prompt
