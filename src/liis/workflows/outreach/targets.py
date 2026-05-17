from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ...utils import parse_yaml_block, slugify


@dataclass(slots=True)
class OutreachTarget:
    name: str
    username: str
    role: str | None = None


def load_targets(path: Path) -> list[OutreachTarget]:
    data = parse_yaml_block(path.read_text(encoding="utf-8"))
    targets: list[OutreachTarget] = []
    entries_val = data.get("people", [])
    entries: list[Any] = entries_val if isinstance(entries_val, list) else []  # type: ignore[assignment]
    for entry in entries:  # type: ignore[union-attr]
        if not isinstance(entry, dict):
            raise ValueError(f"Invalid outreach target in {path}: expected mapping")
        entry_dict: dict[str, Any] = entry  # type: ignore[assignment]
        username_val: str = entry_dict.get("username", "")  # type: ignore[assignment]
        username = str(username_val).strip() if username_val else ""
        if not username:
            raise ValueError(f"Outreach target in {path} is missing username")
        name_val: str = entry_dict.get("name", username)  # type: ignore[assignment]
        name = str(name_val).strip() if name_val else ""
        if not name:
            raise ValueError(f"Outreach target '{username}' in {path} is missing name")
        role_val: str | None = entry_dict.get("role")  # type: ignore[assignment]
        targets.append(
            OutreachTarget(
                name=name,
                username=username,
                role=str(role_val).strip() if isinstance(role_val, (str, int, float)) else None,
            )
        )
    if not targets:
        raise ValueError(f"No outreach targets found in {path}")
    return targets


def find_target(targets: list[OutreachTarget], identifier: str) -> OutreachTarget:
    normalized = identifier.strip().lower()
    for target in targets:
        if target.username.lower() == normalized or target.name.lower() == normalized:
            return target
        if slugify(target.name) == slugify(identifier):
            return target
    raise ValueError(f"Target not found: {identifier}")


def prepare_message(target: OutreachTarget, message: str) -> dict[str, Any]:
    from ...utils import iso_now

    return {
        "recipient": {
            "name": target.name,
            "username": target.username,
            "role": target.role,
        },
        "message": message.strip(),
        "confirm_required": True,
        "prepared_at": iso_now(),
    }
