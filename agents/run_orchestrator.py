# agents/run_orchestrator.py
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import asyncio
from agents.graph import compile_incident_graph
from agents.tools.log_parser import extract_latest_failure  # <-- Import parser tool

async def main():
    print("[Orchestrator] Initializing LangGraph Self-Healing Incident Pipeline...")
    incident_graph = compile_incident_graph()

    # Automatically read the latest live failure from backend/app.log
    live_crash_log = extract_latest_failure()

    initial_state = {
        "raw_log": live_crash_log,
        "root_cause": "",
        "proposed_patch": "",
        "test_results": {},
        "retry_count": 0,
        "history": []
    }

    print("\n[Orchestrator] Triggering graph execution for detected incident...\n")
    final_state = await incident_graph.ainvoke(initial_state)

    print("\n" + "="*50)
    print("--- INCIDENT EXECUTION SUMMARY ---")
    for event in final_state.get("history", []):
        print(f"• {event}")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(main())