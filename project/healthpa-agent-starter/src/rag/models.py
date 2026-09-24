from typing import Optional

from pydantic import BaseModel, Field


class CoveragePolicy(BaseModel):
    document_id: int
    document_version: Optional[int] = None
    display_id: Optional[str] = None
    document_type: str = "NCD"

    title: str

    publication_number: Optional[str] = None
    benefit_category: Optional[str] = None

    effective_date: Optional[str] = None
    effective_end_date: Optional[str] = None
    implementation_date: Optional[str] = None

    service_description: Optional[str] = None
    indications_limitations: Optional[str] = None

    cross_reference: Optional[str] = None

    transmittal_number: Optional[str] = None
    transmittal_url: Optional[str] = None

    revision_history: Optional[str] = None
    other_text: Optional[str] = None
    reasons_for_denial: Optional[str] = None

    source: str = "CMS Medicare Coverage Database"
    source_url: Optional[str] = None

    raw_metadata: dict = Field(default_factory=dict)