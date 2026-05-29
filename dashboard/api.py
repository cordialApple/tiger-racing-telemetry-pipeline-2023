from typing import Any, Literal

from fastapi import FastAPI, HTTPException, Query
from psycopg.rows import dict_row

from db.connection import Database
from dashboard.models import (
    Channel, ReadingPage, SensorStat, SessionCatalog,
)

app = FastAPI(title="Tiger Racing Telemetry API")
db = Database()

_READING_VIEWS = {"raw": "v_sensor_readings", "1hz": "v_sensor_1hz_enriched"}
_READING_COLUMNS = (
    "session_id, sensor_name, ts, t_seconds, "
    "value, avg_value, min_value, max_value"
)
_DEFAULT_LIMIT = 50000
_MAX_LIMIT = 500000


def run_query(sql: str, params: list[Any] | tuple[Any, ...] = ()) -> list[dict]:
    with db.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            return cur.execute(sql, params).fetchall()


def scalar(sql: str, params: list[Any] | tuple[Any, ...] = ()) -> Any:
    with db.connection() as conn:
        return conn.execute(sql, params).fetchone()[0]


def _filters(sensor, start, end) -> tuple[str, list]:
    clause, params = "WHERE session_id = %s", []
    if sensor is not None:
        clause += " AND sensor_name = %s"
        params.append(sensor)
    if start is not None:
        clause += " AND ts >= %s"
        params.append(start)
    if end is not None:
        clause += " AND ts <= %s"
        params.append(end)
    return clause, params


@app.get("/health")
def health():
    try:
        run_query("SELECT 1")
    except Exception:
        raise HTTPException(status_code=503, detail="database unavailable")
    return {"status": "ok"}


@app.get("/sessions", response_model=list[SessionCatalog])
def sessions():
    return run_query("SELECT * FROM v_session_catalog ORDER BY started_at")


@app.get("/sessions/{session_id}/sensors", response_model=list[Channel])
def session_sensors(session_id: str):
    return run_query(
        "SELECT * FROM v_session_channels WHERE session_id = %s ORDER BY sensor_name",
        [session_id],
    )


@app.get("/readings", response_model=ReadingPage)
def readings(
    session_id: str = Query(...),
    sensor: str | None = None,
    start: str | None = None,
    end: str | None = None,
    downsample: Literal["1hz", "raw"] = "1hz",
    limit: int = Query(_DEFAULT_LIMIT, ge=1, le=_MAX_LIMIT),
    offset: int = Query(0, ge=0),
):
    view = _READING_VIEWS[downsample]
    clause, filters = _filters(sensor, start, end)
    base = [session_id, *filters]

    total = scalar(f"SELECT count(*) FROM {view} {clause}", base)
    rows = run_query(
        f"SELECT {_READING_COLUMNS} FROM {view} {clause} "
        "ORDER BY sensor_name, ts LIMIT %s OFFSET %s",
        base + [limit, offset],
    )
    return {
        "session_id": session_id, "sensor": sensor, "downsample": downsample,
        "limit": limit, "offset": offset, "total": total,
        "count": len(rows), "rows": rows,
    }


@app.get("/stats", response_model=list[SensorStat])
def stats(session_id: str = Query(...), sensor: str | None = None):
    sql = "SELECT * FROM v_session_sensor_stats WHERE session_id = %s"
    params: list[Any] = [session_id]
    if sensor is not None:
        sql += " AND sensor_name = %s"
        params.append(sensor)
    sql += " ORDER BY sensor_name"
    return run_query(sql, params)
