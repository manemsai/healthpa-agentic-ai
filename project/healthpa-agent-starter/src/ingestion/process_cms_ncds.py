from __future__ import annotations

import json
from pathlib import Path

from src.rag.cms_normalizer import normalize_ncd


RAW_DIR = Path("data/raw/cms/ncd_details")
OUTPUT_DIR = Path("data/processed/ncd")


def main():

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    files = sorted(RAW_DIR.glob("*.json"))

    print(f"Found {len(files)} raw NCD files.")

    processed = 0

    for file in files:

        payload = json.loads(
            file.read_text(encoding="utf-8")
        )

        records = payload.get("data", [])

        if not records:
            print(f"Skipping {file.name}: no data")
            continue

        record = records[0]

        policy = normalize_ncd(record)

        output_file = (
            OUTPUT_DIR
            / f"ncd_{policy.document_id}_v{policy.document_version}.json"
        )

        output_file.write_text(
            json.dumps(
                policy.model_dump(),
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        processed += 1

        print(
            f"Processed NCD {policy.display_id}: "
            f"{policy.title}"
        )

    print()
    print(f"Processed {processed} policies.")
    print(f"Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()