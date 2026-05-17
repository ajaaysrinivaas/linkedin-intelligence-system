from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .utils import parse_literal_list, parse_yaml_block


@dataclass(slots=True)
class WatchItem:
    name: str
    query: str
    location: str | None = None
    username: str | None = None


@dataclass(slots=True)
class PromptTemplate:
    name: str
    prompt: str
    tags: list[str]
    tone: str | None = None
    length: str | None = None


def config_path(*parts: str, root: Path) -> Path:
    return root.joinpath("config", *parts)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_watchlist(kind: str, *, root: Path) -> list[WatchItem]:
    path = config_path("dossier-gather", f"{kind}.md", root=root)
    content = _read_text(path)
    data = parse_yaml_block(content)
    items: list[WatchItem] = []
    entries = data.get(kind, [])
    if not isinstance(entries, list):
        raise ValueError(f"Expected '{kind}' to map to a list of watch items")
    for entry in entries:  # type: ignore[union-attr]
        if not isinstance(entry, dict):
            raise ValueError(f"Invalid watch item in {path}: expected mapping")
        entry_dict: dict[str, Any] = entry  # type: ignore[assignment]
        name_val = entry_dict.get("name") or entry_dict.get("title") or entry_dict.get("username") or ""  # type: ignore[union-attr]
        name = str(name_val).strip()  # type: ignore[arg-type]
        query_val = entry_dict.get("search_terms") or entry_dict.get("keywords") or entry_dict.get("query") or entry_dict.get("username") or ""  # type: ignore[union-attr]
        query = str(query_val).strip()  # type: ignore[arg-type]
        if not name:
            raise ValueError(f"Watch item in {path} is missing a name/title/username")
        if not query:
            raise ValueError(f"Watch item '{name}' in {path} is missing search terms")
        items.append(
            WatchItem(
                name=name,
                query=query,
                location=str(entry_dict.get("location")).strip() if entry_dict.get("location") else None,  # type: ignore[union-attr, arg-type]
                username=str(entry_dict.get("username")).strip() if entry_dict.get("username") else None,  # type: ignore[union-attr, arg-type]
            )
        )
    if not items:
        raise ValueError(f"No watch items found in {path}")
    return items


def load_prompt_template(name: str, *, root: Path) -> PromptTemplate:
    return _load_prompt_template("content-draft", name, root=root)


def load_dossier_prompt_template(name: str = "default", *, root: Path) -> PromptTemplate:
    return _load_prompt_template("dossier-gather", name, root=root)


def load_feed_prompt_template(name: str = "default", *, root: Path) -> PromptTemplate:
    return _load_prompt_template("feed-insights", name, root=root)


def _load_prompt_template(kind: str, name: str, *, root: Path) -> PromptTemplate:
    path = config_path(kind, f"{name}.md", root=root)
    if not path.exists():
        raise FileNotFoundError(path)
    content = _read_text(path)
    template_name = _extract_field(content, "Name") or name
    prompt = _extract_prompt(content)
    tags = parse_literal_list(_extract_field(content, "Tags") or "[]")
    tone = _extract_field(content, "Tone")
    length = _extract_field(content, "Length")
    return PromptTemplate(name=template_name, prompt=prompt, tags=tags, tone=tone, length=length)


def _extract_field(text: str, field: str) -> str | None:
    pattern = rf"\*\*{re.escape(field)}:\*\*\s*(.+)"
    match = re.search(pattern, text)
    if match:
        return match.group(1).strip()
    return None


def _extract_prompt(text: str) -> str:
    match = re.search(r"\*\*Prompt Template:\*\*\s*```(?:text)?\s*(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    raise ValueError("Prompt template section missing")
