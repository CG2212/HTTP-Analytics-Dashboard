import uvicorn
from app import create_app
from app.middleware import AutonomousIncidentMiddleware

app = create_app()
app.add_middleware(AutonomousIncidentMiddleware)

if __name__ == "__main__":
    uvicorn.run("run:app", host="0.0.0.0", port=8000, reload=True)