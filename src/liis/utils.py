from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import re
from pathlib import Path
from typing import Any

import yaml


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_now() -> str:
    return utc_now().isoformat().replace("+00:00", "Z")


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    if not slug:
        raise ValueError("Cannot slugify empty text")
    return slug


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def dump_json(path: Path, payload: Any) -> Path:
    ensure_parent(path)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")
    return path


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def extract_fenced_block(text: str, language: str) -> str | None:
    pattern = rf"```{re.escape(language)}\s*(.*?)```"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


def parse_yaml_block(text: str) -> dict[str, Any]:
    block = extract_fenced_block(text, "yaml")
    if not block:
        raise ValueError("No fenced yaml block found")
    parsed = yaml.safe_load(block)
    if isinstance(parsed, dict):
        return parsed  # type: ignore[return-value]
    raise ValueError("Fenced yaml block must parse to a mapping")


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        raise ValueError("Missing YAML frontmatter")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("Malformed YAML frontmatter")
    yaml_parsed = yaml.safe_load(parts[1])
    if not isinstance(yaml_parsed, dict):
        raise ValueError("Frontmatter must parse to a mapping")
    frontmatter: dict[str, Any] = yaml_parsed  # type: ignore[assignment]
    body = parts[2].lstrip("\n")
    return frontmatter, body.strip()


def parse_metadata_field(text: str, field: str) -> str | None:
    pattern = rf"\*\*{re.escape(field)}:\*\*\s*(.+)"
    match = re.search(pattern, text)
    if match:
        return match.group(1).strip()
    return None


def parse_literal_list(text: str) -> list[str]:
    try:
        parsed = yaml.safe_load(text)
        if isinstance(parsed, list):
            return [str(item) for item in parsed]  # type: ignore[misc]
    except Exception:
        raise ValueError("Literal list could not be parsed")
    raise ValueError("Literal list must parse to a list")


@dataclass(slots=True)
class MarkdownDocument:
    frontmatter: dict[str, Any]
    body: str
