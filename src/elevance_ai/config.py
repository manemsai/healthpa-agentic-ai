"""Application configuration for Elevance AI."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Centralized environment-backed configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="ELEVANCE_",
        extra="ignore",
    )

    app_name: str = "Elevance AI"
    environment: Literal["local", "dev", "test", "prod"] = "local"
    debug: bool = False
    api_prefix: str = "/api/v1"

    aws_region: str = "us-east-1"
    bedrock_model_id: str = "amazon.nova-lite-v1:0"
    embedding_model_id: str = "amazon.titan-embed-text-v2:0"

    payer_name: str = "Anthem"
    payer_market: str = "IN"
    line_of_business: str = "COMMERCIAL"
    anthem_policy_index_url: str | None = None
    anthem_policy_base_url: str | None = None
    anthem_policy_listing_url: str = "https://www.anthem.com/provider/policies/clinical-guidelines/?cnslocale=en_US_in"
    anthem_policy_search_url: str = "https://www.anthem.com/provider/policies/clinical-guidelines/search/?cnslocale=en_US_in"

    policy_index_path: str = "data/indexes/policies.faiss"
    policy_metadata_path: str = "data/indexes/policies.parquet"
    policy_raw_output_path: str = "data/raw/anthem_policies.jsonl"
    pricing_data_path: str = "data/silver/pricing"

    policy_mcp_url: str | None = None
    cms_mcp_url: str | None = None
    pricing_mcp_url: str | None = None

    request_timeout_seconds: float = Field(default=20.0, ge=1.0, le=120.0)


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """Return a cached application settings object."""

    return AppSettings()
