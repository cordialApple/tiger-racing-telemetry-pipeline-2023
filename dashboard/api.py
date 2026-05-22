from typing import Any

from fastapi import FastAPI, HTTPException, Query
from psycopg.rows import dict_row

from db.connection import Database

app = FastAPI(title="Tiger Racing Telemetry API")
db = Database()


def run_query(sql: str, params: list[Any] | tuple[Any, ...] = ()) -> list[dict]:
    with db.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            return cur.execute(sql, params).fetchall()


def _1hz_query(start, end, limit) -> tuple[str, list]:
    sql = (
        "SELECT bucket, avg_value, min_value, max_value FROM v_sensor_1hz "
        "WHERE session_id = %s AND sensor_name = %s"
    )
    params: list[Any] = []
    if start is not None:
        sql += " AND bucket >= %s"
        params.append(start)
    if end is not None:
        sql += " AND bucket <= %s"
        params.append(end)
    sql += " ORDER BY bucket"
    if limit is not None:
        sql += " LIMIT %s"
        params.append(limit)
    return sql, params


def _raw_query(start, end, limit) -> tuple[str, list]:
    sql = (
        "SELECT ts, t_seconds, value FROM v_sensor_readings "
        "WHERE session_id = %s AND sensor_name = %s"
    )
    params: list[Any] = []
    if start is not None:
        sql += " AND ts >= %s"
        params.append(start)
    if end is not None:
        sql += " AND ts <= %s"
        params.append(end)
    sql += " ORDER BY ts"
    if limit is not None:
        sql += " LIMIT %s"
        params.append(limit)
    return sql, params


@app.get("/health")
def health():
    try:
        run_query("SELECT 1")
    except Exception:
        raise HTTPException(status_code=503, detail="database unavailable")
    return {"status": "ok"}


@app.get("/sessions")
def sessions():
    return run_query("SELECT * FROM v_session_catalog ORDER BY started_at")


@app.get("/sessions/{session_id}/sensors")
def session_sensors(session_id: str):
    return run_query(
        "SELECT DISTINCT sensor_name FROM v_session_sensor_stats "
        "WHERE session_id = %s ORDER BY sensor_name",
        [session_id],
    )


@app.get("/readings")
def readings(
    session_id: str = Query(...),
    sensor: str = Query(...),
    start: str | None = None,
    end: str | None = None,
    downsample: str = "1hz",
    limit: int | None = None,
):
    build = _raw_query if downsample == "raw" else _1hz_query
    sql, extra = build(start, end, limit)
    return run_query(sql, [session_id, sensor] + extra)


@app.get("/stats")
def stats(session_id: str = Query(...), sensor: str | None = None):
    sql = "SELECT * FROM v_session_sensor_stats WHERE session_id = %s"
    params: list[Any] = [session_id]
    if sensor is not None:
        sql += " AND sensor_name = %s"
        params.append(sensor)
    sql += " ORDER BY sensor_name"
    return run_query(sql, params)
