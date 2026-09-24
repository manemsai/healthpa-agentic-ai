from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    cms_coverage_api_base_url: str = "https://api.coverage.cms.gov"
    cms_request_timeout_seconds: int = 30
    cms_max_ncd_details: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
