from fastapi import WebSocket
import json
from typing import List
from app.logging_config import setup_logging, get_logger

logger = get_logger("app.websocket")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket client connected. Total active: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        logger.debug(f"Broadcasting websocket payload to {len(self.active_connections)} client(s)...")
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.warning(f"Error sending message to websocket client: {e}")
                pass

manager = ConnectionManager()