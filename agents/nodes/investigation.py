# agents/nodes/investigation.py
from typing import Dict, Any
from pydantic import BaseModel, Field
from langchain_google_vertexai import ChatVertexAI
from agents.state import IncidentState
from agents.tools.db_inspector import get_postgres_connection_stats
from agents.tools.incident_queue_parser import get_next_unresolved_incident, mark_incident_resolved

class InvestigationSchema(BaseModel):
    fault_type: str = Field(description="Category of failure: HTTP_TIMEOUT, DB_POOL_EXHAUSTION, etc.")
    faulty_file: str = Field(description="Path to the file responsible for the failure")
    root_cause: str = Field(description="Detailed technical root cause explanation")
    metrics_considered: str = Field(description="Exact error fingerprint, stack trace lines, occurrences, or database telemetry values analyzed")
    reference_standard: str = Field(description="The architectural reference, error pattern, or baseline matched")

async def investigation_node(state: IncidentState) -> Dict[str, Any]:
    print("[Investigation Agent (Vertex AI)] Fetching unresolved incident from queue JSON...")
    
    # 1. Pull the structured incident JSON from our queue file
    incident = get_next_unresolved_incident()
    
    if not incident:
        # Fallback if queue is empty or clean
        raw_log = state.get("raw_log", "No active incidents found in queue.")
        incident_context = {"error_message": raw_log, "stack_trace": raw_log, "occurrences": 1}
    else:
        incident_context = incident
        print(f"Analyzing Incident: {incident.get('error_fingerprint')} (Occurrences: {incident.get('occurrences')})")
        
        # OPTIONAL: Mark it resolved immediately so it moves to next incident.
        mark_incident_resolved(incident.get('error_fingerprint'))

    db_stats = await get_postgres_connection_stats()

    # Initialize Google Vertex AI Model
    llm = ChatVertexAI(
        model="gemini-2.5-flash",
        temperature=0,
        project="your-gcp-project-id",  # <-- Pass your Project ID here
        location="us-central1"           # <-- Pass your Region here
    )
    structured_llm = llm.with_structured_output(InvestigationSchema)

    prompt = f"""You are an Expert SRE Diagnostic Agent. Analyze the structured incident queue data and telemetry with maximum granularity.

Structured Incident Queue Payload:
- Fingerprint: {incident_context.get('error_fingerprint', 'N/A')}
- Error Message: {incident_context.get('error_message', 'N/A')}
- Occurrences: {incident_context.get('occurrences', 1)}
- First Seen: {incident_context.get('first_seen', 'N/A')}
- Last Seen: {incident_context.get('last_seen', 'N/A')}
- Stack Trace: 
{incident_context.get('stack_trace', 'N/A')}

Live Database Telemetry:
{db_stats}

Provide a rigorous breakdown including fault type, exact code file, root cause, specific metrics/lines considered, and reference standards."""

    analysis: InvestigationSchema = await structured_llm.ainvoke(prompt)

    history_msg = (
        f"Investigation Agent Analysis (Queue Fingerprint: {incident_context.get('error_fingerprint', 'Manual')}):\n"
        f"  • Fault Type: {analysis.fault_type}\n"
        f"  • Target File: {analysis.faulty_file}\n"
        f"  • Occurrences Count: {incident_context.get('occurrences', 1)}\n"
        f"  • Metrics Considered: {analysis.metrics_considered}\n"
        f"  • Reference Standard: {analysis.reference_standard}\n"
        f"  • Root Cause: {analysis.root_cause}"
    )

    return {
        "root_cause": f"[{analysis.fault_type}] {analysis.root_cause} (File: {analysis.faulty_file} | Fingerprint: {incident_context.get('error_fingerprint')})",
        "history": [history_msg]
    }