# agents/tools/log_parser.py
from pathlib import Path

# Points to backend/app.log from the root directory
LOG_FILE_PATH = Path(__file__).resolve().parents[2] / "backend" / "app.log"

def extract_latest_failure() -> str:
    """Reads the application log and extracts the most recent error or traceback block."""
    if not LOG_FILE_PATH.exists():
        return "2026-10-02 23:28:17,894 | ERROR | app.proxy:66 - Proxy request error: httpcore.ConnectTimeout (Mock fallback)"
    
    try:
        content = LOG_FILE_PATH.read_text(encoding="utf-8")
        if not content.strip():
            return "Log file is currently empty."
            
        # Split log by entries or grab the tail chunk containing the latest traceback
        chunks = content.split("ERROR")
        if len(chunks) > 1:
            # Return the latest error block
            return "ERROR" + chunks[-1]
        
        return content[-2000:]  # Fallback to last 2000 characters
    except Exception as e:
        return f"Error reading log file: {e}"