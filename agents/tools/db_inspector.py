# agents/tools/db_inspector.py
import asyncpg
import os

DB_URI = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/http_analytics")

async def get_postgres_connection_stats() -> dict:
    """Queries pg_stat_activity to collect live connection counts."""
    try:
        conn = await asyncpg.connect(DB_URI)
        rows = await conn.fetch(
            "SELECT state, count(*) FROM pg_stat_activity GROUP BY state;"
        )
        max_conns = await conn.fetchval("SHOW max_connections;")
        await conn.close()

        stats = {row["state"] or "unknown": row["count"] for row in rows}
        return {
            "active_connections": stats.get("active", 0),
            "idle_connections": stats.get("idle", 0),
            "total_open": sum(stats.values()),
            "max_allowed": int(max_conns)
        }
    except Exception as e:
        return {"error": f"Failed to inspect DB: {str(e)}"}