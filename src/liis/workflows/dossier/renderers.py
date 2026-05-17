from __future__ import annotations

import json
from typing import Any

import yaml

from ...models import Artifact


def render_people_dossier(artifact: Artifact, normalized: dict[str, Any]) -> str:
    summary = normalized.get("summary", {})
    intelligence = normalized.get("intelligence", {})
    evidence = normalized.get("evidence", {})
    frontmatter: dict[str, Any] = {
        "id": artifact.id,
        "kind": artifact.kind,
        "title": artifact.title,
        "captured_at": artifact.captured_at,
        "source": artifact.source,
        "tags": artifact.tags,
    }
    lines = ["---", yaml.safe_dump(frontmatter, sort_keys=False).strip(), "---", ""]
    lines.append(f"# {summary.get('name', artifact.title)}")
    if summary.get("headline"):
        lines.append(f"> {summary['headline']}")
    lines.append("")
    lines.append("## Verified Facts")
    for label, value in (
        ("Current Title", summary.get("current_title")),
        ("Current Company", summary.get("current_company")),
        ("Location", summary.get("location")),
        ("Followers", summary.get("followers")),
        ("Connections", summary.get("connections")),
        ("Profile URL", summary.get("profile_url")),
        ("Profile URN", summary.get("profile_urn")),
    ):
        if value not in (None, "", []):
            lines.append(f"- {label}: {value}")
    lines.append("")
    lines.append("## Evidence")
    for section_name in ("experience", "education", "certifications", "skills", "projects", "activity"):
        section_items = evidence.get(section_name, [])
        if not section_items:
            continue
        lines.append(f"### {section_name.title()}")
        for item in section_items[:6]:
            lines.append(f"- {item}")
        lines.append("")
    lines.append("## Grounded Inferences")
    if intelligence.get("one_liner"):
        lines.append(f"- Inference: {intelligence['one_liner']}")
    if intelligence.get("why_it_matters"):
        lines.append(f"- Inference: {intelligence['why_it_matters']}")
    for signal in intelligence.get("fit_signals", []):
        lines.append(f"- Signal: {signal}")
    lines.append("")
    lines.append("## Outreach Readiness")
    if intelligence.get("outreach_angles"):
        for angle in intelligence.get("outreach_angles", []):
            lines.append(f"- Possible angle: {angle}")
    else:
        lines.append("- No grounded outreach angle identified from the available profile data.")
    lines.append("")
    lines.append("## Source")
    if summary.get("profile_url"):
        lines.append(f"- Profile URL: {summary['profile_url']}")
    if summary.get("profile_urn"):
        lines.append(f"- Profile URN: {summary['profile_urn']}")
    lines.append(f"- Captured at: {artifact.captured_at}")
    return "\n".join(lines).strip() + "\n"


def render_people_search(artifact: Artifact, normalized: dict[str, Any]) -> str:
    summary = normalized.get("summary", {})
    entities = normalized.get("entities", [])
    frontmatter: dict[str, Any] = {
        "id": artifact.id,
        "kind": artifact.kind,
        "title": artifact.title,
        "captured_at": artifact.captured_at,
        "source": artifact.source,
        "tags": artifact.tags,
    }
    lines = ["---", yaml.safe_dump(frontmatter, sort_keys=False).strip(), "---", ""]
    lines.append(f"# People Search: {summary.get('query') or artifact.title}")
    lines.append("")
    lines.append("## Best Match")
    lines.append(f"- Name: {summary.get('name', 'Unknown')}")
    if summary.get("headline"):
        lines.append(f"- Snippet: {summary['headline']}")
    if summary.get("profile_url"):
        lines.append(f"- Profile URL: {summary['profile_url']}")
    lines.append(f"- Match found: {'yes' if summary.get('match_found') else 'no'}")
    lines.append("")
    if entities:
        lines.append("## Possible Matches")
        for entity in entities[:5]:
            if not isinstance(entity, dict):
                continue
            name: Any = entity.get("name") or "Unknown"  # type: ignore[assignment]
            profile_url: Any = entity.get("profile_url")  # type: ignore[assignment]
            excerpt: Any = entity.get("excerpt")  # type: ignore[assignment]
            bullet = f"- {name}"
            if profile_url:
                bullet += f" ({profile_url})"
            if excerpt:
                bullet += f": {excerpt}"
            lines.append(bullet)
        lines.append("")
    lines.append("## Recommended Next Step")
    lines.append("- If the match looks right, use `get_person_profile` for a full intelligence brief.")
    lines.append("- If not, refine the search query with a company, title, or location filter.")
    lines.append("- Treat this as a search-result brief, not a full profile dossier.")
    lines.append("")
    lines.append("## Source")
    lines.append(f"- Captured at: {artifact.captured_at}")
    if artifact.source.get("source_name"):
        lines.append(f"- Source name: {artifact.source['source_name']}")
    return "\n".join(lines).strip() + "\n"


def render_generic_dossier(artifact: Artifact, normalized: dict[str, Any]) -> str:
    frontmatter: dict[str, Any] = {
        "id": artifact.id,
        "kind": artifact.kind,
        "title": artifact.title,
        "captured_at": artifact.captured_at,
        "source": artifact.source,
        "tags": artifact.tags,
    }
    lines = ["---", yaml.safe_dump(frontmatter, sort_keys=False).strip(), "---", ""]
    lines.append(f"# {artifact.title}")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- {artifact.summary or 'No summary generated.'}")
    lines.append("")
    lines.append("## Normalized Data")
    lines.append("```json")
    lines.append(json.dumps(normalized, indent=2, ensure_ascii=True))
    lines.append("```")
    return "\n".join(lines).strip() + "\n"
