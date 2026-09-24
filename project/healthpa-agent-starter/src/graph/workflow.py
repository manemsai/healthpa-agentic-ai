from __future__ import annotations

from langgraph.graph import (
    END,
    START,
    StateGraph,
)

from src.graph.nodes import (
    final_response_node,
    generation_node,
    grounding_node,
    human_review_node,
    retrieval_node,
    review_decision_node,
    router_node,
)

from src.graph.routing import (
    route_after_review,
    route_after_router,
)

from src.graph.state import HealthPAState


def unsupported_node(
    state: HealthPAState,
) -> HealthPAState:

    return {
        "answer": (
            "This workflow currently supports "
            "CMS coverage-related questions only."
        ),
        "final_status": "UNSUPPORTED",
    }


def build_graph():

    workflow = StateGraph(
        HealthPAState
    )

    workflow.add_node(
        "router",
        router_node,
    )

    workflow.add_node(
        "retrieve",
        retrieval_node,
    )

    workflow.add_node(
        "generate",
        generation_node,
    )

    workflow.add_node(
        "grounding",
        grounding_node,
    )

    workflow.add_node(
        "review_decision",
        review_decision_node,
    )

    workflow.add_node(
        "human_review",
        human_review_node,
    )

    workflow.add_node(
        "final_response",
        final_response_node,
    )

    workflow.add_node(
        "unsupported",
        unsupported_node,
    )

    workflow.add_edge(
        START,
        "router",
    )

    workflow.add_conditional_edges(
        "router",
        route_after_router,
        {
            "retrieve": "retrieve",
            "unsupported": "unsupported",
        },
    )

    workflow.add_edge(
        "retrieve",
        "generate",
    )

    workflow.add_edge(
        "generate",
        "grounding",
    )

    workflow.add_edge(
        "grounding",
        "review_decision",
    )

    workflow.add_conditional_edges(
        "review_decision",
        route_after_review,
        {
            "human_review": (
                "human_review"
            ),
            "final_response": (
                "final_response"
            ),
        },
    )

    workflow.add_edge(
        "human_review",
        END,
    )

    workflow.add_edge(
        "final_response",
        END,
    )

    workflow.add_edge(
        "unsupported",
        END,
    )

    return workflow.compile()