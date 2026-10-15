# agents/nodes/investigation.py
from typing import Dict, Any
from pydantic import BaseModel, Field
from langchain_google_vertexai import ChatVertexAI
from agents.state import IncidentState
from agents.tools.db_inspector import get_postgres_connection_stats

class InvestigationSchema(BaseModel):
    fault_type: str = Field(description="Category of failure: HTTP_TIMEOUT, DB_POOL_EXHAUSTION, etc.")
    faulty_file: str = Field(description="Path to the file responsible for the failure")
    root_cause: str = Field(description="Detailed technical root cause explanation")
    metrics_considered: str = Field(description="Exact log snippets, stack trace lines, or database telemetry values analyzed")
    reference_standard: str = Field(description="The architectural reference, error pattern, or baseline matched")

async def investigation_node(state: IncidentState) -> Dict[str, Any]:
    print("[Investigation Agent (Vertex AI)] Performing deep telemetry & log analysis...")
    raw_log = state.get("raw_log", "")
    db_stats = await get_postgres_connection_stats()

    # Initialize Google Vertex AI Model
    llm = ChatVertexAI(
        model="gemini-2.5-flash",
        temperature=0,
        project="your-gcp-project-id",  # <-- Pass your Project ID here
        location="us-central1"           # <-- Pass your Region here
    )
    structured_llm = llm.with_structured_output(InvestigationSchema)

    prompt = f"""You are an Expert SRE Diagnostic Agent. Analyze the telemetry and logs with maximum granularity.

Stack Trace / Log:
{raw_log}

Live Database Telemetry:
{db_stats}

Provide a rigorous breakdown including fault type, exact code file, root cause, specific metrics/lines considered, and reference standards."""

    analysis: InvestigationSchema = await structured_llm.ainvoke(prompt)

    history_msg = (
        f"Investigation Agent Analysis:\n"
        f"  • Fault Type: {analysis.fault_type}\n"
        f"  • Target File: {analysis.faulty_file}\n"
        f"  • Metrics Considered: {analysis.metrics_considered}\n"
        f"  • Reference Standard: {analysis.reference_standard}\n"
        f"  • Root Cause: {analysis.root_cause}"
    )

    return {
        "root_cause": f"[{analysis.fault_type}] {analysis.root_cause} (File: {analysis.faulty_file} | Telemetry: {analysis.metrics_considered})",
        "history": [history_msg]
    }