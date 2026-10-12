# agents/nodes/deployment.py
from typing import Dict, Any
from langchain_google_vertexai import ChatVertexAI
from agents.state import IncidentState

async def deployment_node(state: IncidentState) -> Dict[str, Any]:
    print("[Deployment Agent (Vertex AI)] Summarizing and finalizing release...")
    patch = state.get("proposed_patch", "")
    root_cause = state.get("root_cause", "")

    # Initialize Google Vertex AI Model
    llm = ChatVertexAI(
        model="gemini-2.5-flash",
        temperature=0,
        project="your-gcp-project-id",  # <-- Pass your Project ID here
        location="us-central1"           # <-- Pass your Region here
    )
    prompt = f"""Write a concise post-mortem release note (2 lines) for an auto-applied patch.
Root Cause: {root_cause}
Applied Patch: {patch}"""

    response = await llm.ainvoke(prompt)
    release_note = response.content.strip()

    return {
        "history": [f"Deployment Agent (Vertex AI): Hot reload executed. {release_note}"]
    }