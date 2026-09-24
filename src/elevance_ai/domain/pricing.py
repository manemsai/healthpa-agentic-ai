"""Domain models for pricing data."""

from decimal import Decimal

from pydantic import BaseModel, Field


class PricingQuery(BaseModel):
    """Structured request for negotiated-rate lookups."""

    billing_code: str
    billing_code_type: str = "CPT"
    payer: str = "Anthem"
    market: str = "IN"
    service_description: str | None = None
    limit: int = Field(default=20, ge=1, le=100)


class PricingObservation(BaseModel):
    """Normalized negotiated-rate result."""

    billing_code: str
    billing_code_type: str
    provider_name: str
    provider_npi: str | None = None
    negotiated_rate: Decimal
    negotiated_type: str | None = None
    service_description: str | None = None
    file_last_updated: str | None = None
