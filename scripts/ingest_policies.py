"""Script entrypoint for policy ingestion."""

from __future__ import annotations

import argparse

from elevance_ai.config import get_settings
from elevance_ai.ingestion.anthem_policies import (
    AnthemPolicyIngestionClient,
    write_policy_documents_jsonl,
)


def build_parser() -> argparse.ArgumentParser:
    """Create a CLI parser for policy ingestion."""

    parser = argparse.ArgumentParser(description="Ingest Anthem policy documents into normalized JSONL.")
    parser.add_argument("--index-url", default=None, help="Policy listing page URL.")
    parser.add_argument(
        "--catalog-url",
        action="append",
        default=None,
        help="Catalog or search page URL to crawl for policy links. Can be passed multiple times.",
    )
    parser.add_argument("--output", default=None, help="JSONL output path.")
    parser.add_argument("--limit", type=int, default=25, help="Maximum number of policy pages to ingest.")
    return parser


def main() -> None:
    """Run policy ingestion from a configured or supplied index URL."""

    args = build_parser().parse_args()
    settings = get_settings()
    index_url = args.index_url or settings.anthem_policy_index_url
    output_path = args.output or settings.policy_raw_output_path
    catalog_urls = args.catalog_url or [settings.anthem_policy_listing_url, settings.anthem_policy_search_url]

    if not index_url:
        index_url = catalog_urls[0]

    with AnthemPolicyIngestionClient(
        market=settings.payer_market,
        line_of_business=settings.line_of_business,
        payer=settings.payer_name,
        timeout_seconds=settings.request_timeout_seconds,
        base_url=settings.anthem_policy_base_url,
    ) as client:
        entries = client.fetch_catalog(catalog_urls, max_entries=args.limit)
        if not entries:
            entries = client.fetch_index(index_url)
        limited_entries = entries[: args.limit]
        documents = [client.fetch_policy(entry) for entry in limited_entries]

    written_path = write_policy_documents_jsonl(documents, output_path)
    print(f"Ingested {len(documents)} policy documents to {written_path}")


if __name__ == "__main__":
    main()
