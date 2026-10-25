import json
import traceback
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import threading  # Added for thread-safe file writing
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

INCIDENT_QUEUE_FILE = Path(__file__).resolve().parents[1] / "incidents_queue.json"
IST = ZoneInfo("Asia/Kolkata")
file_lock = threading.Lock()  # Prevents concurrent write race conditions

def upsert_incident(exc: Exception):
    """Standalone utility function to record or update any exception in incidents_queue.json using IST time safely."""
    now_iso = datetime.now(IST).isoformat()
    stack_trace = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    
    # Create a unique fingerprint based on exception type and message prefix
    fingerprint = f"{type(exc).__name__}:{str(exc).split(':')[0]}"

    # Use a thread lock so concurrent requests don't corrupt the JSON file
    with file_lock:
        queue = []
        if INCIDENT_QUEUE_FILE.exists():
            try:
                queue = json.loads(INCIDENT_QUEUE_FILE.read_text(encoding="utf-8"))
            except Exception:
                queue = []

        # Check if an unresolved incident with this fingerprint already exists
        existing_incident = next((i for i in queue if i.get("error_fingerprint") == fingerprint and i.get("status") == "unresolved"), None)

        if existing_incident:
            existing_incident["occurrences"] += 1
            existing_incident["last_seen"] = now_iso
            existing_incident["stack_trace"] = stack_trace  
            print(f"[Incident Updated] Fingerprint '{fingerprint}' occurrence count: {existing_incident['occurrences']}")
        else:
            new_incident = {
                "error_fingerprint": fingerprint,
                "error_message": str(exc),
                "stack_trace": stack_trace,
                "status": "unresolved",
                "occurrences": 1,
                "first_seen": now_iso,
                "last_seen": now_iso
            }
            queue.append(new_incident)
            print(f"[New Incident Alarmed] Fingerprint '{fingerprint}' registered.")

        INCIDENT_QUEUE_FILE.write_text(json.dumps(queue, indent=2), encoding="utf-8")

class AutonomousIncidentMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            # Ignore client disconnects and low-severity HTTP exceptions (< 500)
            if isinstance(exc, (ClientDisconnect, HTTPException)) and (isinstance(exc, ClientDisconnect) or exc.status_code < 500):
                raise exc

            # Call the standalone utility function directly for 500s and unhandled crashes
            upsert_incident(exc)
            
            raise exc