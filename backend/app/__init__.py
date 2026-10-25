from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.websocket import manager
from app.metrics import get_dashboard_data_from_db  # Updated import
from app.proxy import router as proxy_router
from app.database import init_db
from app.logging_config import setup_logging, get_logger
from app.middleware import AutonomousIncidentMiddleware, upsert_incident

logger = get_logger("app.main")

def create_app():
    setup_logging()  # Initialize log handlers on app creation
    app = FastAPI()
    
    # Register middleware for all regular HTTP requests
    app.add_middleware(AutonomousIncidentMiddleware)
    logger.info("FastAPI application initialized.")

    @app.on_event("startup")
    async def startup_event():
        await init_db()

    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend"))

    app.mount("/css", StaticFiles(directory=os.path.join(frontend_dir, "css")), name="css")
    app.mount("/js", StaticFiles(directory=os.path.join(frontend_dir, "js")), name="js")

    app.include_router(proxy_router)

    @app.get("/")
    async def serve_index():
        logger.debug("Serving dashboard index page")
        return FileResponse(os.path.join(frontend_dir, "index.html"))

    # Fetch complete metrics & sessions from PostgreSQL on page load
    @app.get("/api/dashboard-data")
    async def get_dashboard_data():
        logger.debug("API GET /api/dashboard-data requested")
        return await get_dashboard_data_from_db(limit=50)

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await manager.connect(websocket)
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect as e:
            logger.error(f"Unexpected WebSocket error: {e}", exc_info=True)
            manager.disconnect(websocket)
            upsert_incident(e)

    return app