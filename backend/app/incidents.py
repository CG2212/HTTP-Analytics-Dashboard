from fastapi import APIRouter
import os
import json
from app.logging_config import get_logger

logger = get_logger("app.incidents")
router = APIRouter(prefix="/api/incidents", tags=["Incidents"])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INCIDENTS_FILE = os.path.abspath(os.path.join(BASE_DIR, "..", "incidents_queue.json"))

@router.get("/")
async def get_incidents_data():
    logger.debug(f"Attempting to read incidents from: {INCIDENTS_FILE}")
    if os.path.exists(INCIDENTS_FILE):
        try:
            with open(INCIDENTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read incidents_queue.json: {e}", exc_info=True)
            return []
    else:
        logger.warning(f"incidents_queue.json not found at path: {INCIDENTS_FILE}")
        return []