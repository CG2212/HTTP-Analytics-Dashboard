# agents/tools/incident_queue_parser.py
import json
from pathlib import Path

QUEUE_FILE = Path(__file__).resolve().parents[2] / "backend" / "incidents_queue.json"

def get_next_unresolved_incident() -> dict | None:
    if not QUEUE_FILE.exists():
        return None
    
    try:
        queue = json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
        for incident in queue:
            if incident.get("status") == "unresolved":
                return incident
    except Exception:
        return None
    return None

def mark_incident_resolved(error_message: str):
    if not QUEUE_FILE.exists():
        return
    queue = json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
    for incident in queue:
        if incident.get("error_message") == error_message:
            incident["status"] = "resolved"
    QUEUE_FILE.write_text(json.dumps(queue, indent=2), encoding="utf-8")