# agents/edges.py
from agents.state import IncidentState

def route_after_validation(state: IncidentState) -> str:
    """Decides next graph destination based on validation test metrics."""
    test_results = state.get("test_results", {})
    passed = test_results.get("passed", False)
    retries = state.get("retry_count", 0)
    
    if passed:
        return "deploy"
    elif retries >= 3:
        return "escalate"
    else:
        return "dev"  # Loop back to Development Agent for another iteration