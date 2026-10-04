"""Command-line entrypoints for Elevance AI."""

from __future__ import annotations

import argparse
import json

from elevance_ai import get_settings
from elevance_ai.agents.graph import build_graph
from elevance_ai.tools.policy_tools import PolicySearchTool


def main() -> None:
    """Run a local policy question through the HealthPA graph."""

    parser = argparse.ArgumentParser(description="Ask the local HealthPA policy assistant a question.")
    parser.add_argument("question", nargs="?", help="Policy, coverage, or cost question")
    parser.add_argument("--market", default=None, help="Payer market filter, for example IN")
    parser.add_argument("--line-of-business", default=None, help="Line of business filter, for example COMMERCIAL")
    parser.add_argument("--top-k", type=int, default=5, help="Number of evidence chunks to retrieve")
    args = parser.parse_args()

    if not args.question:
        print("Start the API with: uvicorn apps.api.main:app --reload")
        print("Or ask locally with: elevance-poc 'Is prior authorization required for knee arthroscopy?'")
        return

    settings = get_settings()
    tool = PolicySearchTool.from_settings(settings)
    decision = build_graph(tool).invoke(
        args.question,
        market=args.market or settings.payer_market,
        line_of_business=args.line_of_business or settings.line_of_business,
        top_k=args.top_k,
    )
    print(json.dumps(decision.model_dump(mode="json"), indent=2))
