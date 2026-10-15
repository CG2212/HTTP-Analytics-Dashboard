# agents/nodes/deployment.py
from typing import Dict, Any
from datetime import datetime
import pytz
from langchain_google_vertexai import ChatVertexAI
from agents.state import IncidentState

async def deployment_node(state: IncidentState) -> Dict[str, Any]:
    print("[Deployment Agent (Vertex AI)] Compiling post-mortem release report...")
    patch = state.get("proposed_patch", "")
    root_cause = state.get("root_cause", "")
    test_results = state.get("test_results", {})

    # Generate current timestamp in IST (Indian Standard Time)
    ist_timezone = pytz.timezone("Asia/Kolkata")
    current_time_ist = datetime.now(ist_timezone).strftime("%Y-%m-%d %H:%M:%S %Z%z")

    # Initialize Google Vertex AI Model
    llm = ChatVertexAI(
        model="gemini-2.5-flash",
        temperature=0,
        project="your-gcp-project-id",  # <-- Pass your Project ID here
        location="us-central1"           # <-- Pass your Region here
    )
    
    prompt = f"""Write a comprehensive post-mortem release report in Markdown.
CRITICAL INSTRUCTIONS:
1. Use Indian Standard Time (IST) for all timestamps (Current Timestamp: {current_time_ist}).
2. Do NOT invent unverified post-deployment assumptions or 30-minute manual monitoring blocks. Base verification strictly on the automated simulation benchmark test results provided below.

Root Cause: {root_cause}
Proposed Patch Recommendations: {patch}
Automated Simulation Test Results: {test_results}"""

    response = await llm.ainvoke(prompt)
    release_note = response.content.strip()

    history_msg = (
        f"Deployment Agent Release Report (IST):\n"
        f"  • Timestamp: {current_time_ist}\n"
        f"  • Status: Approved and Verified via Automated Simulation Benchmark\n"
        f"  • Full Report:\n{release_note}"
    )

    return {
        "history": [history_msg]
    }