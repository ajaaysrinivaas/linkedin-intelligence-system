from __future__ import annotations

from pathlib import Path

from ...config import load_prompt_template


def render_post_prompt(
    raw_body: str,
    template_name: str,
    tags: list[str] | None = None,
    *,
    root: Path,
) -> str:
    template = load_prompt_template(template_name, root=root)
    resolved_tags = tags or template.tags
    return template.prompt.format(raw_content=raw_body.strip(), tags=", ".join(resolved_tags))
