# agents/tools/incident_queue_parser.py
import json
from pathlib import Path
import threading

QUEUE_FILE = Path(__file__).resolve().parents[2] / "backend" / "incidents_queue.json"
file_lock = threading.Lock()

def get_next_unresolved_incident() -> dict | None:
    """Returns the first unresolved incident in the queue."""
    if not QUEUE_FILE.exists():
        return None
    
    with file_lock:
        try:
            queue = json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
            for incident in queue:
                if incident.get("status") == "unresolved":
                    return incident
        except Exception:
            return None
    return None

def get_all_unresolved_incidents() -> list:
    """Returns a list of all unresolved incidents."""
    if not QUEUE_FILE.exists():
        return []
    
    with file_lock:
        try:
            queue = json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
            return [i for i in queue if i.get("status") == "unresolved"]
        except Exception:
            return []

def mark_incident_resolved(error_fingerprint: str):
    """Marks an incident as resolved using its unique fingerprint."""
    if not QUEUE_FILE.exists():
        return
    
    with file_lock:
        try:
            queue = json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
            updated = False
            for incident in queue:
                if incident.get("error_fingerprint") == error_fingerprint:
                    incident["status"] = "resolved"
                    updated = True
            
            if updated:
                QUEUE_FILE.write_text(json.dumps(queue, indent=2), encoding="utf-8")
        except Exception as e:
            print(f"[Error marking incident resolved]: {e}")