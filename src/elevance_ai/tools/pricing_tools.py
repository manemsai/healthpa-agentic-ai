"""Tool wrappers for pricing-related operations."""

from __future__ import annotations

import csv
from pathlib import Path

from elevance_ai.domain.pricing import PricingObservation, PricingQuery


def read_pricing_csv(path: str | Path, query: PricingQuery) -> list[PricingObservation]:
    """Read a small normalized pricing CSV and filter it by billing code."""

    observations: list[PricingObservation] = []
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if row.get("billing_code", "").strip().upper() != query.billing_code.upper():
                continue
            observations.append(PricingObservation.model_validate(row))
            if len(observations) >= query.limit:
                break
    return observations
