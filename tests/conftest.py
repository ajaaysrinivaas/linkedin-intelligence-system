from __future__ import annotations

import sys
from pathlib import Path
import shutil
import uuid
from collections.abc import Generator

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


@pytest.fixture
def tmp_path(tmp_path_factory: pytest.TempPathFactory) -> Generator[Path, None, None]:  # type: ignore[name-defined]
    """Override tmp_path to use a project-local temp directory on Windows."""
    # Use a local .pytest_tmp directory instead of Windows AppData temp
    base_tmp = ROOT / ".pytest_tmp"
    base_tmp.mkdir(parents=True, exist_ok=True)
    
    # Create a unique temp directory
    test_tmp = base_tmp / f"test_{uuid.uuid4().hex[:8]}"
    test_tmp.mkdir(parents=True, exist_ok=True)
    
    yield test_tmp
    
    # Cleanup
    try:
        shutil.rmtree(test_tmp, ignore_errors=True)
    except Exception:
        pass

