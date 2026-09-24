"""Domain models for provider data."""

from pydantic import BaseModel, Field


class ProviderDirectoryQuery(BaseModel):
    """Structured request for provider directory searches."""

    specialty: str
    city: str | None = None
    state: str = "IN"
    postal_code: str | None = None
    radius_miles: int = Field(default=25, ge=1, le=100)
    limit: int = Field(default=10, ge=1, le=50)


class ProviderRecord(BaseModel):
    """Normalized provider record from CMS or payer directories."""

    npi: str
    name: str
    specialty: str | None = None
    organization_name: str | None = None
    address_line_1: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    phone: str | None = None
    accepting_new_patients: bool | None = None
