# agents/nodes/validation.py
import asyncio
from typing import Dict, Any
from pydantic import BaseModel, Field
from langchain_google_vertexai import ChatVertexAI
from agents.state import IncidentState

class ValidationSchema(BaseModel):
    passed: bool = Field(description="True if latency and error rate meet SLA standards (<500ms p95, <1% errors)")
    summary: str = Field(description="Brief assessment of the load test performance")

async def validation_node(state: IncidentState) -> Dict[str, Any]:
    print("[Validation Agent (Vertex AI)] Evaluating load test metrics...")
    current_retries = state.get("retry_count", 0)
    await asyncio.sleep(1)  # Simulate test run execution

    raw_metrics = {
        "p95_latency_ms": 120 if current_retries >= 1 else 3200,
        "error_rate": 0.0 if current_retries >= 1 else 0.14,
        "total_requests": 1000
    }

    # Initialize Google Vertex AI Model
    llm = ChatVertexAI(
        model="gemini-2.5-flash",
        temperature=0,
        project="your-gcp-project-id",  # <-- Pass your Project ID here
        location="us-central1"           # <-- Pass your Region here
    )
    structured_llm = llm.with_structured_output(ValidationSchema)

    prompt = f"""You are a Performance Testing Agent. Evaluate whether these load test metrics satisfy SLA requirements (SLA: p95 latency < 500ms, error rate < 1%).

Test Metrics:
{raw_metrics}"""

    evaluation: ValidationSchema = await structured_llm.ainvoke(prompt)

    return {
        "test_results": {
            "passed": evaluation.passed,
            "metrics": raw_metrics
        },
        "retry_count": current_retries + 1,
        "history": [f"Validation Agent (Vertex AI): Benchmark evaluated. Passed={evaluation.passed}. {evaluation.summary}"]
    }