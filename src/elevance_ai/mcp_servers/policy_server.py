"""MCP server entrypoint for policy tools.

This module intentionally keeps the MCP implementation optional. The core
policy search logic lives in ``elevance_ai.tools.policy_tools`` so the API,
CLI, and tests can run without starting an MCP process.
"""

from __future__ import annotations

from elevance_ai import get_settings
from elevance_ai.tools.policy_tools import PolicySearchTool


def build_policy_tool() -> PolicySearchTool:
    """Build the policy tool used by a future MCP server wrapper."""

    return PolicySearchTool.from_settings(get_settings())
