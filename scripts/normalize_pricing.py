"""Normalize a local CMS transparency-style pricing file for HealthPA."""
from __future__ import annotations

import argparse
from pathlib import Path

from elevance_ai.ingestion.anthem_mrf import normalize_mrf_to_csv


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize JSON/JSON.GZ negotiated-rate data into HealthPA CSV format.")
    parser.add_argument("source", type=Path, help="Local machine-readable JSON or JSON.GZ file")
    parser.add_argument("output", type=Path, help="Destination normalized CSV")
    args = parser.parse_args()
    count = normalize_mrf_to_csv(args.source, args.output)
    print(f"Wrote {count} normalized pricing observation(s) to {args.output}")


if __name__ == "__main__":
    main()
