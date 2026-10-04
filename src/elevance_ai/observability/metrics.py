"""Minimal in-process observability for the local HealthPA MVP."""
from __future__ import annotations

from collections import Counter
from threading import Lock

_counts: Counter[str] = Counter()
_lock = Lock()


def record_query(route: str, status: str) -> None:
    """Record non-sensitive aggregate query outcomes."""
    with _lock:
        _counts["queries_total"] += 1
        _counts[f"route_{route}"] += 1
        _counts[f"status_{status}"] += 1


def snapshot() -> dict[str, int]:
    """Return a copy of aggregate process-local counters."""
    with _lock:
        return dict(_counts)
