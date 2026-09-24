from __future__ import annotations

from typing import Any

from src.rag.cleaner import clean_html_text
from src.rag.models import CoveragePolicy


def normalize_ncd(record: dict[str, Any]) -> CoveragePolicy:

    document_id = int(record["document_id"])

    source_url = (
        "https://www.cms.gov/medicare-coverage-database/"
        f"view/ncd.aspx?ncdid={document_id}"
    )

    return CoveragePolicy(
        document_id=document_id,
        document_version=record.get("document_version"),
        display_id=record.get("document_display_id"),
        document_type="NCD",

        title=record.get("title", ""),

        publication_number=record.get("publication_number"),
        benefit_category=record.get("benefit_category"),

        effective_date=record.get("effective_date"),
        effective_end_date=record.get("effective_end_date"),
        implementation_date=record.get("implementation_date"),

        service_description=clean_html_text(
            record.get("item_service_description")
        ),

        indications_limitations=clean_html_text(
            record.get("indications_limitations")
        ),

        cross_reference=clean_html_text(
            record.get("cross_reference")
        ),

        transmittal_number=record.get("transmittal_number"),
        transmittal_url=record.get("transmittal_url"),

        revision_history=clean_html_text(
            record.get("revision_history")
        ),

        other_text=clean_html_text(
            record.get("other_text")
        ),

        reasons_for_denial=clean_html_text(
            record.get("reasons_for_denial")
        ),

        source_url=source_url,

        raw_metadata={
            "qr_modifier_date": record.get("qr_modifier_date"),
            "ama_statement": record.get("ama_statement"),
        },
    )