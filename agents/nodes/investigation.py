# agents/nodes/investigation.py
from typing import Dict, Any
from pydantic import BaseModel, Field
from langchain_google_vertexai import ChatVertexAI  # <-- Changed from Anthropic
from agents.state import IncidentState
from agents.tools.db_inspector import get_postgres_connection_stats

class InvestigationSchema(BaseModel):
    fault_type: str = Field(description="Category of failure: HTTP_TIMEOUT, DB_POOL_EXHAUSTION, AUTH_FAILURE, or UNKNOWN")
    faulty_file: str = Field(description="Path to the file responsible for the failure")
    root_cause: str = Field(description="Detailed technical root cause explanation")

async def investigation_node(state: IncidentState) -> Dict[str, Any]:
    print("[Investigation Agent (Vertex AI)] Analyzing stack trace...")
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

    prompt = f"""You are a Site Reliability Engineering Agent. Analyze the following application stack trace and runtime metrics to diagnose the root cause.

Stack Trace:
{raw_log}

Live Database Metrics:
{db_stats}

Identify the root cause, fault type, and responsible source file."""

    analysis: InvestigationSchema = await structured_llm.ainvoke(prompt)

    return {
        "root_cause": f"[{analysis.fault_type}] {analysis.root_cause} (File: {analysis.faulty_file})",
        "history": [f"Investigation Agent (Vertex AI): Diagnosed {analysis.fault_type} in {analysis.faulty_file}"]
    }