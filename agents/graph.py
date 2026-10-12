# agents/graph.py
from langgraph.graph import StateGraph, START, END
from agents.state import IncidentState
from agents.nodes.investigation import investigation_node
from agents.nodes.development import development_node
from agents.nodes.validation import validation_node
from agents.nodes.deployment import deployment_node
from agents.nodes.escalation import escalation_node
from agents.edges import route_after_validation

def compile_incident_graph():
    """Assembles and compiles the self-healing LangGraph incident pipeline."""
    builder = StateGraph(IncidentState)

    # 1. Add Nodes
    builder.add_node("investigate", investigation_node)
    builder.add_node("dev", development_node)
    builder.add_node("validation", validation_node)
    builder.add_node("deploy", deployment_node)
    builder.add_node("escalate", escalation_node)

    # 2. Define Control Flow Edges
    builder.add_edge(START, "investigate")
    builder.add_edge("investigate", "dev")
    builder.add_edge("dev", "validation")

    # 3. Add Conditional Edge for Self-Healing Retry Loop
    builder.add_conditional_edges(
        "validation",
        route_after_validation,
        {
            "deploy": "deploy",
            "escalate": "escalate",
            "dev": "dev"  # Loop back if tests fail
        }
    )

    builder.add_edge("deploy", END)
    builder.add_edge("escalate", END)

    return builder.compile()