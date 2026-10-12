# agents/nodes/development.py
from typing import Dict, Any
from pydantic import BaseModel, Field
from langchain_google_vertexai import ChatVertexAI
from agents.state import IncidentState

class PatchSchema(BaseModel):
    target_file: str = Field(description="File to patch, e.g. backend/app/proxy.py")
    patch_explanation: str = Field(description="Brief overview of why this patch fixes the issue")
    proposed_changes: str = Field(description="Concrete configuration/code parameter updates to apply")

async def development_node(state: IncidentState) -> Dict[str, Any]:
    print("[Development Agent (Vertex AI)] Constructing targeted patch...")
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

    prompt = f"""You are a Backend Software Engineer Agent. Generate a code fix for this incident.

Root Cause:
{root_cause}

Attempt Number: {retries + 1}
(If attempt > 1, increase pool sizes or timeouts significantly beyond standard values.)

Provide the target file path, explanation, and precise proposed parameter updates."""

    patch: PatchSchema = await structured_llm.ainvoke(prompt)
    patch_summary = f"{patch.target_file} -> {patch.proposed_changes}"

    return {
        "proposed_patch": patch_summary,
        "history": [f"Development Agent (Vertex AI): Attempt {retries + 1} generated patch for {patch.target_file}"]
    }