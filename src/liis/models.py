from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass(slots=True)
class Artifact:
    id: str
    kind: str
    title: str
    captured_at: str
    source: dict[str, Any]
    summary: str = ""
    tags: list[str] = field(default_factory=lambda: [])  # type: ignore[assignment]
    related: list[str] = field(default_factory=lambda: [])  # type: ignore[assignment]
    raw: dict[str, Any] = field(default_factory=lambda: {})  # type: ignore[assignment]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class RunRecord:
    id: str
    workflow: str
    captured_at: str
    inputs: dict[str, Any]
    outputs: list[dict[str, Any]] = field(default_factory=lambda: [])  # type: ignore[assignment]
    status: str = "ok"
    notes: list[str] = field(default_factory=lambda: [])  # type: ignore[assignment]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

