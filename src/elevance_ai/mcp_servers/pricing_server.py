"""MCP server for normalized public pricing lookups."""
from __future__ import annotations

from pathlib import Path

from mcp.server.fastmcp import FastMCP

from elevance_ai import get_settings
from elevance_ai.domain.pricing import PricingQuery
from elevance_ai.tools.pricing_tools import read_pricing_csv

mcp = FastMCP("healthpa-pricing")


@mcp.tool()
def lookup_negotiated_rates(billing_code: str, limit: int = 10) -> dict:
    """Look up local normalized public negotiated-rate observations by billing code."""
    settings = get_settings()
    path = Path(settings.pricing_data_path)
    if not path.is_file():
        return {"observations": [], "warning": "Normalized pricing data is not loaded."}
    rows = read_pricing_csv(path, PricingQuery(billing_code=billing_code, market=settings.payer_market, limit=max(1, min(limit, 100))))
    return {"observations": [row.model_dump(mode="json") for row in rows], "warning": "Public negotiated rates are not member-specific out-of-pocket costs."}


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
