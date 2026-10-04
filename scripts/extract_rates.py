"""Extract normalized pricing rows from a CSV file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from elevance_ai.domain.pricing import PricingQuery
from elevance_ai.tools.pricing_tools import read_pricing_csv


def main() -> None:
    parser = argparse.ArgumentParser(description="Filter normalized pricing CSV rows by billing code.")
    parser.add_argument("csv_path", type=Path, help="CSV with pricing columns")
    parser.add_argument("--billing-code", required=True, help="Billing code to filter")
    parser.add_argument("--billing-code-type", default="CPT", help="Billing code type")
    parser.add_argument("--limit", type=int, default=20, help="Maximum rows to emit")
    args = parser.parse_args()

    query = PricingQuery(
        billing_code=args.billing_code,
        billing_code_type=args.billing_code_type,
        limit=args.limit,
    )
    observations = read_pricing_csv(args.csv_path, query)
    print(json.dumps([item.model_dump(mode="json") for item in observations], indent=2))


if __name__ == "__main__":
    main()
