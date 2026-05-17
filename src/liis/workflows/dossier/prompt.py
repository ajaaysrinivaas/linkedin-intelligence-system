from __future__ import annotations

from pathlib import Path
from typing import Any

from ...config import load_dossier_prompt_template


def build_dossier_prompt(*, root: Path, normalized: dict[str, Any]) -> tuple[str, str]:
    template = load_dossier_prompt_template(root=root)
    summary: dict[str, Any] = normalized.get("summary", {})  # type: ignore[assignment]
    if isinstance(summary, dict) and summary.get("match_found"):  # type: ignore[union-attr]
        dossier_type = "people search"
    elif normalized.get("kind") == "people":
        dossier_type = "full profile"
    elif normalized.get("kind") == "companies":
        dossier_type = "company dossier"
    elif normalized.get("kind") == "jobs":
        dossier_type = "job dossier"
    else:
        dossier_type = str(normalized.get("kind") or "dossier")
    profile_data = _serialize_dossier_context(normalized)
    prompt = template.prompt.format(dossier_type=dossier_type, profile_data=profile_data)
    return template.name, prompt


def _serialize_dossier_context(normalized: dict[str, Any]) -> str:
    summary: dict[str, Any] = normalized.get("summary", {})  # type: ignore[assignment]
    intelligence: dict[str, Any] = normalized.get("intelligence", {})  # type: ignore[assignment]
    evidence: dict[str, Any] = normalized.get("evidence", {})  # type: ignore[assignment]
    entries: list[Any] = normalized.get("entries", [])  # type: ignore[assignment]
    entities: list[Any] = normalized.get("entities", [])  # type: ignore[assignment]

    lines: list[str] = []
    if summary:
        lines.append("Summary:")
        for key in ("query", "name", "headline", "current_title", "current_company", "location", "profile_url", "degree", "connections", "followers"):
            value: Any = summary.get(key)  # type: ignore[union-attr, assignment]
            if value not in (None, "", []):
                lines.append(f"- {key}: {value}")
    if intelligence:
        lines.append("Intelligence:")
        one_liner: Any = intelligence.get("one_liner")  # type: ignore[union-attr, assignment]
        if one_liner:
            lines.append(f"- one_liner: {one_liner}")
        why: Any = intelligence.get("why_it_matters")  # type: ignore[union-attr, assignment]
        if why:
            lines.append(f"- why_it_matters: {why}")
        fit_signals: Any = intelligence.get("fit_signals", [])  # type: ignore[union-attr, assignment]
        for signal in fit_signals if isinstance(fit_signals, list) else []:  # type: ignore[misc]
            lines.append(f"- inference_signal: {signal}")
        outreach_angles: Any = intelligence.get("outreach_angles", [])  # type: ignore[union-attr, assignment]
        for angle in outreach_angles if isinstance(outreach_angles, list) else []:  # type: ignore[misc]
            lines.append(f"- outreach_angle: {angle}")
    if evidence:
        lines.append("Evidence:")
        for section_name in ("experience", "education", "certifications", "skills", "projects", "activity"):
            section_items: Any = evidence.get(section_name, [])  # type: ignore[union-attr, assignment]
            if isinstance(section_items, list) and section_items:
                lines.append(f"- {section_name}:")
                for item in section_items[:6]:  # type: ignore[misc]
                    lines.append(f"  - {item}")
    if entries:
        lines.append("Entries:")
        for entry in entries[:5]:  # type: ignore[misc]
            if isinstance(entry, dict):
                entry_dict: dict[str, Any] = entry  # type: ignore[assignment]
                title: Any = entry_dict.get("title") or entry_dict.get("company") or entry_dict.get("name") or "Unknown"  # type: ignore[union-attr, assignment]
                lines.append(f"- {title}")
    if entities:
        lines.append("Entities:")
        for entity in entities[:5]:  # type: ignore[misc]
            if isinstance(entity, dict):
                entity_dict: dict[str, Any] = entity  # type: ignore[assignment]
                title = entity_dict.get("name") or entity_dict.get("company") or entity_dict.get("title") or "Unknown"  # type: ignore[union-attr, assignment]
                excerpt: Any = entity_dict.get("excerpt") or entity_dict.get("headline") or entity_dict.get("summary") or ""  # type: ignore[union-attr, assignment]
                if excerpt:
                    lines.append(f"- {title}: {excerpt}")
                else:
                    lines.append(f"- {title}")
    return "\n".join(lines).strip()
