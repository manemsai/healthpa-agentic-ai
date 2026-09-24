from __future__ import annotations

from typing import Any

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from src.config.settings import settings


class CMSCoverageClient:
    """Small client for the public CMS Medicare Coverage API.

    We deliberately start with National Coverage Determinations (NCDs)
    because the NCD report and NCD detail endpoints do not require the
    local-document license token used by many LCD/Article endpoints.
    """

    def __init__(self) -> None:
        self.base_url = settings.cms_coverage_api_base_url.rstrip("/")
        self.timeout = settings.cms_request_timeout_seconds

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.TransportError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        reraise=True,
    )
    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            return response.json()

    def list_ncds(self) -> dict[str, Any]:
        return self._get("/v1/reports/national-coverage-ncd/")

    def get_ncd(self, ncd_id: int | str, ncd_version: int | str | None = None) -> dict[str, Any]:
        params: dict[str, Any] = {"ncdid": ncd_id}
        if ncd_version is not None:
            params["ncdver"] = ncd_version
        return self._get("/v1/data/ncd/", params=params)
