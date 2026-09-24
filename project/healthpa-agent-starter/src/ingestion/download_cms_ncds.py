from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.config.settings import settings
from src.ingestion.cms_client import CMSCoverageClient


OUTPUT_DIR = Path("data/raw/cms")


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def pick_value(record: dict[str, Any], *possible_keys: str) -> Any:
    """Tolerates minor API field-name differences across releases."""
    lowered = {str(k).lower(): v for k, v in record.items()}
    for key in possible_keys:
        if key in record:
            return record[key]
        if key.lower() in lowered:
            return lowered[key.lower()]
    return None


def main() -> None:
    client = CMSCoverageClient()

    print("1) Downloading CMS National Coverage Determination index...")
    report = client.list_ncds()

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report_path = OUTPUT_DIR / f"ncd_report_{stamp}.json"
    save_json(report_path, report)

    rows = report.get("data", [])
    print(f"   Received {len(rows)} NCD report rows.")
    print(f"   Saved: {report_path}")

    if not rows:
        print("No NCD rows returned. Inspect the saved response before continuing.")
        return

    max_details = min(settings.cms_max_ncd_details, len(rows))
    details_dir = OUTPUT_DIR / "ncd_details"

    print(f"2) Downloading details for the first {max_details} NCDs...")

    downloaded = 0
    skipped = 0

    for row in rows[:max_details]:
        if not isinstance(row, dict):
            skipped += 1
            continue

        ncd_id = pick_value(
            row,
            "document_id",
            "ncd_id",
            "ncdid",
            "NCD_ID",
            "id",
        )
        ncd_ver = pick_value(
            row,
            "document_version",
            "ncd_version",
            "ncd_ver",
            "ncdver",
            "version",
        )

        if ncd_id is None:
            print(f"   Skipping row because NCD id was not found: {row}")
            skipped += 1
            continue

        detail = client.get_ncd(ncd_id, ncd_ver)
        filename = f"ncd_{ncd_id}"
        if ncd_ver is not None:
            filename += f"_v{ncd_ver}"
        filename += ".json"

        save_json(details_dir / filename, detail)
        downloaded += 1
        print(f"   Downloaded NCD {ncd_id}")

    manifest = {
        "source": "CMS Medicare Coverage API",
        "api_base_url": settings.cms_coverage_api_base_url,
        "downloaded_at_utc": stamp,
        "report_rows": len(rows),
        "detail_documents_downloaded": downloaded,
        "detail_documents_skipped": skipped,
    }
    save_json(OUTPUT_DIR / f"manifest_{stamp}.json", manifest)

    print("\nDone.")
    print("Next step: inspect the returned schema and normalize the NCD fields before chunking.")


if __name__ == "__main__":
    main()
