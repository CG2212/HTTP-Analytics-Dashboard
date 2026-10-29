# agents/run_orchestrator.py
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import asyncio
from agents.graph import compile_incident_graph
from agents.tools.log_parser import extract_latest_failure  # <-- Import parser tool
from agents.tools.incident_queue_parser import get_next_unresolved_incident

async def main():
    print("[Orchestrator] Initializing LangGraph Self-Healing Incident Pipeline...")
    
    # 1. Check the queue first instead of blindly reading raw logs
    next_incident = get_next_unresolved_incident()
    
    if not next_incident:
        print("[Orchestrator] No unresolved incidents found in queue. System is healthy. Exiting pipeline.")
        return

    print(f"[Orchestrator] Found unresolved incident: {next_incident.get('error_fingerprint')}")
    incident_graph = compile_incident_graph()

    initial_state = {
        "raw_log": next_incident.get('error_message'),
        "root_cause": "",
        "proposed_patch": "",
        "test_results": {},
        "retry_count": 0,
        "history": []
    }

    print("[Orchestrator] Triggering graph execution for detected incident...\n")
    final_state = await incident_graph.ainvoke(initial_state)

    print("\n" + "="*50)
    print("--- INCIDENT EXECUTION SUMMARY ---")
    for event in final_state.get("history", []):
        print(f"• {event}")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(main())