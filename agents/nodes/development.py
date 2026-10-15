# agents/nodes/development.py
from typing import Dict, Any
from pydantic import BaseModel, Field
from langchain_google_vertexai import ChatVertexAI
from agents.state import IncidentState

class PatchSchema(BaseModel):
    target_file: str = Field(description="File to patch, e.g. backend/app/metrics.py")
    suggestion_rationale: str = Field(description="Detailed engineering rationale behind the suggested configuration changes")
    proposed_parameter_suggestions: str = Field(description="Exact parameter updates suggested for review/application")
    scaling_parameters: str = Field(description="Explicit values suggested (e.g. pool_size=20, max_overflow=10)")

async def development_node(state: IncidentState) -> Dict[str, Any]:
    print("[Development Agent (Vertex AI)] Formulating proposed configuration recommendations...")
    root_cause = state.get("root_cause", "")
    retries = state.get("retry_count", 0)

    # Initialize Google Vertex AI Model
    llm = ChatVertexAI(
        model="gemini-2.5-flash",
        temperature=0,
        project="your-gcp-project-id",  # <-- Pass your Project ID here
        location="us-central1"           # <-- Pass your Region here
    )
    structured_llm = llm.with_structured_output(PatchSchema)

    prompt = f"""You are a Principal Backend Engineer Agent. Formulate precise configuration tuning recommendations to resolve the incident. 

IMPORTANT: Frame your response as a **proposed configuration suggestion** for review, outlining exact parameter changes needed.

Diagnosis & Root Cause:
{root_cause}

Current Attempt: {retries + 1}
(Rule: Scale up values proportionally based on attempt number if previous attempts failed validation).

Provide explicit parameter suggestions, detailed rationale, and exact scaling values."""

    patch: PatchSchema = await structured_llm.ainvoke(prompt)
    patch_summary = f"{patch.target_file} -> {patch.proposed_parameter_suggestions} (Scaling: {patch.scaling_parameters})"

    history_msg = (
        f"Development Agent Proposed Configuration (Attempt {retries + 1}):\n"
        f"  • Target File: {patch.target_file}\n"
        f"  • Engineering Rationale: {patch.suggestion_rationale}\n"
        f"  • Proposed Parameter Suggestions: {patch.proposed_parameter_suggestions}\n"
        f"  • Explicit Scaling Values: {patch.scaling_parameters}"
    )

    return {
        "proposed_patch": patch_summary,
        "history": [history_msg]
    }