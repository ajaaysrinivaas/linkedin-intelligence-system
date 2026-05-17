from __future__ import annotations

from typing import Any

from .normalization.dossiers import normalize_dossier_payload
from .normalization.feed import normalize_feed_payload

Payload = dict[str, Any]

__all__ = ["normalize_dossier_payload", "normalize_feed_payload", "Payload"]
