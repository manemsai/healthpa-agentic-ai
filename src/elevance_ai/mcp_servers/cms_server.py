"""MCP server for CMS/public-source scope evidence."""
from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from elevance_ai.tools.cms_tools import cms_disclaimer_evidence

mcp = FastMCP("healthpa-cms")


@mcp.tool()
def cms_public_scope() -> dict:
    """Return the evidence boundary for CMS/public coverage references."""
    return cms_disclaimer_evidence().model_dump(mode="json")


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
