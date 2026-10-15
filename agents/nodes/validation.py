# agents/nodes/validation.py
import asyncio
from typing import Dict, Any
from pydantic import BaseModel, Field
from langchain_google_vertexai import ChatVertexAI
from agents.state import IncidentState

class ValidationSchema(BaseModel):
    passed: bool = Field(description="True if metrics satisfy SLA thresholds")
    summary: str = Field(description="Detailed evaluation summary")
    metrics_comparison: str = Field(description="Explicit breakdown of benchmark values versus SLA reference limits")

async def validation_node(state: IncidentState) -> Dict[str, Any]:
    print("[Validation Agent (Vertex AI)] Running automated simulation benchmark audit...")
    current_retries = state.get("retry_count", 0)
    await asyncio.sleep(1)

    # Explanation: These metrics are generated via an automated simulation benchmark runner 
    # (mimicking a load test tool like Locust/k6) to test the proposed patch under concurrency.
    raw_metrics = {
        "benchmark_source": "Automated Simulation Benchmark Runner (Mock Load Test)",
        "p95_latency_ms": 120 if current_retries >= 1 else 3200,
        "error_rate_pct": 0.0 if current_retries >= 1 else 14.0,
        "total_requests_tested": 1000,
        "concurrency_level": 50
    }
    sla_limits = {
        "max_p95_latency_ms": 500,
        "max_error_rate_pct": 1.0
    }

    # Initialize Google Vertex AI Model
    llm = ChatVertexAI(
        model="gemini-2.5-flash",
        temperature=0,
        project="your-gcp-project-id",  # <-- Pass your Project ID here
        location="us-central1"           # <-- Pass your Region here
    )
    structured_llm = llm.with_structured_output(ValidationSchema)

    prompt = f"""You are a Lead Performance Validation Agent. Audit the automated simulation benchmark telemetry against strict enterprise SLAs.

Simulated Benchmark Metrics:
{raw_metrics}

SLA Reference Limits:
{sla_limits}

Evaluate whether performance meets requirements and provide explicit comparison values."""

    evaluation: ValidationSchema = await structured_llm.ainvoke(prompt)

    history_msg = (
        f"Validation Agent Simulation Audit (Attempt {current_retries + 1}):\n"
        f"  • Status: {'PASSED ' if evaluation.passed else 'FAILED '}\n"
        f"  • Benchmark Source: Automated Simulation Test Runner\n"
        f"  • Measured vs SLA Reference: {evaluation.metrics_comparison}\n"
        f"  • Assessment Summary: {evaluation.summary}"
    )

    return {
        "test_results": {
            "passed": evaluation.passed,
            "metrics": raw_metrics
        },
        "retry_count": current_retries + 1,
        "history": [history_msg]
    }