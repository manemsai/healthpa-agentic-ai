from __future__ import annotations

import json
from pathlib import Path
from typing import Any


RAW_DIR = Path("data/raw/cms")


def summarize(value: Any, depth: int = 0) -> Any:
    if depth >= 2:
        return type(value).__name__

    if isinstance(value, dict):
        return {k: summarize(v, depth + 1) for k, v in list(value.items())[:30]}

    if isinstance(value, list):
        if not value:
            return []
        return [summarize(value[0], depth + 1)]

    return type(value).__name__


def main() -> None:
    files = sorted(RAW_DIR.rglob("*.json"))

    if not files:
        print("No CMS JSON files found. Run download_cms_ncds.py first.")
        return

    print(f"Found {len(files)} JSON files.\n")

    for path in files[:5]:
        payload = json.loads(path.read_text(encoding="utf-8"))
        print("=" * 80)
        print(path)
        print(json.dumps(summarize(payload), indent=2))


if __name__ == "__main__":
    main()
