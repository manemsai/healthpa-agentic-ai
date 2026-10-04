"""Anthem-compatible machine-readable pricing ingestion helpers."""
from __future__ import annotations

import csv
import gzip
import json
from pathlib import Path
from typing import IO, Any


def _open_json(path: str | Path) -> IO[str]:
    source = Path(path)
    if source.suffix == ".gz":
        return gzip.open(source, "rt", encoding="utf-8")
    return source.open(encoding="utf-8")


def iter_normalized_rates(path: str | Path):
    """Yield normalized negotiated rates from a CMS transparency-style in-network file."""
    with _open_json(path) as handle:
        payload: dict[str, Any] = json.load(handle)
    last_updated = payload.get("last_updated_on")
    provider_references = {str(item.get("provider_group_id")): item for item in payload.get("provider_references", [])}
    for item in payload.get("in_network", []):
        code = str(item.get("billing_code", "")).strip()
        if not code:
            continue
        code_type = str(item.get("billing_code_type", "CPT"))
        description = item.get("description") or item.get("name")
        for negotiated in item.get("negotiated_rates", []):
            provider_names: list[tuple[str, str | None]] = []
            for ref in negotiated.get("provider_references", []):
                group = provider_references.get(str(ref), {})
                for provider in group.get("provider_groups", []):
                    npis = provider.get("npi") or []
                    name = provider.get("provider_name") or group.get("provider_name") or f"Provider group {ref}"
                    provider_names.append((str(name), str(npis[0]) if npis else None))
            if not provider_names:
                provider_names = [("Provider not specified", None)]
            for price in negotiated.get("negotiated_prices", []):
                rate = price.get("negotiated_rate")
                if rate is None:
                    continue
                for provider_name, npi in provider_names:
                    yield {
                        "billing_code": code,
                        "billing_code_type": code_type,
                        "provider_name": provider_name,
                        "provider_npi": npi or "",
                        "negotiated_rate": rate,
                        "negotiated_type": price.get("negotiated_type") or "",
                        "service_description": description or "",
                        "file_last_updated": last_updated or "",
                    }


def normalize_mrf_to_csv(source: str | Path, output: str | Path) -> int:
    """Normalize a local MRF fixture/file into the compact pricing CSV used by HealthPA."""
    rows = list(iter_normalized_rates(source))
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fields = ["billing_code", "billing_code_type", "provider_name", "provider_npi", "negotiated_rate", "negotiated_type", "service_description", "file_last_updated"]
    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)
