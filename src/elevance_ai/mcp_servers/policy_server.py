"""MCP server exposing the local policy-search capability."""
from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from elevance_ai import get_settings
from elevance_ai.tools.policy_tools import PolicySearchTool

mcp = FastMCP("healthpa-policy")


def build_policy_tool() -> PolicySearchTool:
    """Build the configured local policy retrieval tool."""
    return PolicySearchTool.from_settings(get_settings())


@mcp.tool()
def search_policy(question: str, market: str | None = None, line_of_business: str | None = None, top_k: int = 5) -> dict:
    """Search indexed public policy evidence without making a member-specific determination."""
    settings = get_settings()
    evidence = build_policy_tool().search(
        question,
        market=market or settings.payer_market,
        line_of_business=line_of_business or settings.line_of_business,
        top_k=max(1, min(top_k, 10)),
    )
    return {
        "evidence": [item.model_dump(mode="json") for item in evidence],
        "warning": "Public policy evidence is not a final member-specific benefit or authorization determination.",
    }


def main() -> None:
    """Run the policy MCP server over stdio."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
