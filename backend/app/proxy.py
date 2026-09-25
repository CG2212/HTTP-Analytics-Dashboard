from fastapi import APIRouter, Request, Response
import httpx
import time
from app.config import TARGET_URL
from app.metrics import save_session_to_db, get_dashboard_data_from_db
from app.websocket import manager

from app.logging_config import setup_logging, get_logger

logger = get_logger("app.proxy")
router = APIRouter()

@router.api_route("/proxy/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def proxy_handler(request: Request, path: str):
    logger.debug(f"Proxying request: {request.method} /{path}")
    user_agent = request.headers.get("user-agent", "Unknown Agent")
    client_ip = request.client.host if request.client else "unknown"

    req_body = await request.body()
    req_headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}
    target_full_url = f"{TARGET_URL}/{path}"

    session_data = {
        "id": int(time.time() * 1000),
        "timestamp": time.strftime("%H:%M:%S", time.gmtime()),
        "request": {
            "method": request.method,
            "url": f"/proxy/{path}",
            "headers": dict(request.headers),
            "client_ip": client_ip
        },
        "response": {}
    }

    async with httpx.AsyncClient() as client:
        try:
            proxy_response = await client.request(
                method=request.method,
                url=target_full_url,
                headers=req_headers,
                content=req_body,
                params=request.query_params,
                timeout=1.0
            )

            status_code = proxy_response.status_code
            logger.info(f"Upstream response received: {status_code} for {request.method} /{path}")

            session_data["response"] = {
                "statusCode": status_code,
                "headers": dict(proxy_response.headers)
            }

            res_headers = {
                k: v for k, v in proxy_response.headers.items()
                if k.lower() not in ["content-encoding", "transfer-encoding", "content-length"]
            }

            response_obj = Response(
                content=proxy_response.content,
                status_code=status_code,
                headers=res_headers
            )

        except Exception as e:
            logger.error(f"Proxy request error for target {target_full_url}: {e}", exc_info=True)
            session_data["response"] = {
                "statusCode": 500,
                "headers": {"error": str(e)}
            }
            response_obj = Response(content=f"Proxy Error: {str(e)}", status_code=500)

    # 1. Save session to PostgreSQL
    await save_session_to_db(session_data)

    # 2. Get fresh aggregated metrics from PostgreSQL for live dashboard update
    dashboard_payload = await get_dashboard_data_from_db(limit=50)

    # 3. Broadcast to all active WebSocket clients
    await manager.broadcast({
        "session": session_data,
        "metrics": dashboard_payload["metrics"]
    })

    return response_obj