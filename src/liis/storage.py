from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .models import Artifact, RunRecord
from .utils import dump_json, ensure_parent


@dataclass(slots=True)
class WorkspacePaths:
    root: Path

    @property
    def data(self) -> Path:
        return self.root / "data"

    @property
    def archived(self) -> Path:
        return self.root / "archived"

    @property
    def index_dir(self) -> Path:
        return self.data / "index"


class RepositoryStore:
    def __init__(self, root: Path) -> None:
        self.paths = WorkspacePaths(root=root)
        self._layout_done: bool = False

    def ensure_layout(self) -> None:
        if self._layout_done:
            return
        for rel in [
            self.paths.data / "dossiers" / "active" / "companies",
            self.paths.data / "dossiers" / "active" / "jobs",
            self.paths.data / "dossiers" / "active" / "people",
            self.paths.data / "feed_insights",
            self.paths.data / "posts" / "raw",
            self.paths.data / "posts" / "curated",
            self.paths.data / "outreach",
            self.paths.index_dir,
        ]:
            rel.mkdir(parents=True, exist_ok=True)
        self._layout_done = True

    def save_artifact(self, artifact: Artifact, relative_dir: str, filename: str | None = None) -> Path:
        self.ensure_layout()
        safe_name = filename or f"{artifact.id}.json"
        target = self.paths.data / relative_dir / safe_name
        return dump_json(target, artifact.to_dict())

    def save_markdown(self, relative_path: str, content: str) -> Path:
        return self.save_text(relative_path, content)

    def save_run_record(self, record: RunRecord) -> Path:
        self.ensure_layout()
        target = self.paths.index_dir / "runs" / f"{record.id}.json"
        return dump_json(target, record.to_dict())

    def save_json(self, relative_path: str, payload: Any) -> Path:
        target = self.paths.root / relative_path
        return dump_json(target, payload)

    def save_text(self, relative_path: str, content: str) -> Path:
        target = self.paths.root / relative_path
        ensure_parent(target)
        target.write_text(content, encoding="utf-8")
        return target
