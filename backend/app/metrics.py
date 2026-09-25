from sqlalchemy.future import select
from sqlalchemy import func
from app.database import AsyncSessionLocal, HTTPSessionModel

from app.logging_config import setup_logging, get_logger

logger = get_logger("app.metrics")

async def save_session_to_db(session_data: dict):
    """Persists a proxy HTTP request/response directly to PostgreSQL."""
    logger.debug("Attempting to persist session to database...")
    async with AsyncSessionLocal() as session:
        try:
            db_entry = HTTPSessionModel(
                method=session_data["request"]["method"],
                url=session_data["request"]["url"],
                status_code=session_data["response"].get("statusCode", 500),
                user_agent=session_data["request"]["headers"].get("user-agent", "Unknown"),
                client_ip=session_data["request"]["client_ip"],
                request_headers=session_data["request"]["headers"],
                response_headers=session_data["response"].get("headers", {})
            )
            session.add(db_entry)
            await session.commit()
            logger.debug(f"Successfully saved session ID: {db_entry.id}")
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to save session to DB: {e}", exc_info=True)

async def get_dashboard_data_from_db(limit: int = 50):
    """Calculates all metrics and fetches recent sessions directly from PostgreSQL."""
    logger.debug(f"Fetching dashboard metrics and last {limit} sessions from DB...")
    async with AsyncSessionLocal() as session:
        try:
            # 1. Query Total Requests Count
            total_req_res = await session.execute(select(func.count(HTTPSessionModel.id)))
            total_requests = total_req_res.scalar() or 0

            # 2. Query HTTP Methods Breakdown (GET, POST, etc.)
            methods_res = await session.execute(
                select(HTTPSessionModel.method, func.count(HTTPSessionModel.id))
                .group_by(HTTPSessionModel.method)
            )
            methods_counts = dict(methods_res.all())

            # 3. Query Status Codes Breakdown (200, 404, 500, etc.)
            status_res = await session.execute(
                select(HTTPSessionModel.status_code, func.count(HTTPSessionModel.id))
                .group_by(HTTPSessionModel.status_code)
            )
            status_counts = {str(code): count for code, count in status_res.all() if code is not None}

            # 4. Query User Agents Breakdown
            agent_res = await session.execute(
                select(HTTPSessionModel.user_agent, func.count(HTTPSessionModel.id))
                .group_by(HTTPSessionModel.user_agent)
                .limit(10)
            )
            user_agents_counts = dict(agent_res.all())

            # 5. Query Recent Session Logs
            sessions_res = await session.execute(
                select(HTTPSessionModel)
                .order_by(HTTPSessionModel.timestamp.desc())
                .limit(limit)
            )
            recent_sessions = [
                {
                    "id": s.id,
                    "timestamp": s.timestamp.strftime("%H:%M:%S") if s.timestamp else "",
                    "request": {
                        "method": s.method,
                        "url": s.url,
                        "headers": s.request_headers or {},
                        "client_ip": s.client_ip or "unknown"
                    },
                    "response": {
                        "statusCode": s.status_code,
                        "headers": s.response_headers or {}
                    }
                }
                for s in sessions_res.scalars().all()
            ]

            logger.debug(f"Dashboard query succeeded. Total requests logged: {total_requests}")
            return {
                "metrics": {
                    "total_requests": total_requests,
                    "total_responses": total_requests,
                    "status_codes": status_counts,
                    "methods": methods_counts,
                    "user_agents": user_agents_counts
                },
                "sessions": recent_sessions
            }

        except Exception as e:
            logger.error("Failed to query dashboard metrics from DB", exc_info=True)
            return {
                "metrics": {
                    "total_requests": 0,
                    "total_responses": 0,
                    "status_codes": {},
                    "methods": {},
                    "user_agents": {}
                },
                "sessions": []
            }