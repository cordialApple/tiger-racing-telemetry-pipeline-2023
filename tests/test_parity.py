import json
import statistics
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import config
from dashboard import api
from db.connection import Database
from db.repository import ReadingRepository
from db.schema_manager import SchemaManager
from parser.aim_parser import AimParser
from parser.specs import SpecLoader

GOLDEN = json.loads((Path(__file__).parent / "golden" / "session_1.json").read_text())


def test_parser_matches_reference(parsed):
    s = parsed.session
    assert s.source_file == GOLDEN["source_file"]
    assert s.session_id == GOLDEN["session_id"]
    assert s.started_at.isoformat() == GOLDEN["started_at"]
    assert s.sample_rate_hz == GOLDEN["sample_rate_hz"]
    assert s.duration_s == GOLDEN["duration_s"]
    assert s.vehicle == GOLDEN["vehicle"]
    assert s.championship == GOLDEN["championship"]
    assert parsed.row_count == GOLDEN["row_count"]
    assert len(parsed.readings) == GOLDEN["reading_count"]
    assert len(parsed.units) == GOLDEN["sensor_count"]
    assert ("Time" in parsed.units) == GOLDEN["time_column_present"]


def test_rpm_series_matches_reference(parsed):
    rpm = [(ts, v) for ts, name, v in parsed.readings if name == "ECU RPM"]
    values = [v for _ts, v in rpm]
    assert len(values) == GOLDEN["rpm_n"]
    assert min(values) == GOLDEN["rpm_min"]
    assert max(values) == GOLDEN["rpm_max"]
    assert round(statistics.fmean(values), 4) == GOLDEN["rpm_avg"]
    assert (rpm[1][0] - rpm[0][0]).total_seconds() * 1000 == GOLDEN["rpm_spacing_ms"]
    assert [[ts.isoformat(), v] for ts, v in rpm[:3]] == GOLDEN["rpm_first3"]


@pytest.fixture(scope="module")
def loaded_db():
    db = Database()
    try:
        with db.connection() as conn:
            available = conn.execute(
                "SELECT 1 FROM pg_available_extensions WHERE name = 'timescaledb'"
            ).fetchone()
    except Exception as e:
        pytest.skip(f"no database available: {e}")
    if available is None:
        pytest.skip("timescaledb extension not available")

    SchemaManager(db).apply()
    repo = ReadingRepository()
    parsed = AimParser().parse(config.RAW_DIR / "1.csv")
    with db.connection() as conn:
        _purge(conn)
        repo.upsert_sensors(conn, SpecLoader().load())
        repo.insert_session(conn, parsed.session)
        n = repo.copy_readings(conn, parsed.session.session_id, parsed.readings)
        repo.log_ingestion(conn, parsed.packet_id, "1", "1.csv", parsed.row_count, n)
    yield db
    with db.connection() as conn:
        _purge(conn)
    db.close()


def _purge(conn):
    conn.execute("DELETE FROM sensor_readings WHERE session_id = '1'")
    conn.execute("DELETE FROM ingestion_log WHERE session_id = '1'")
    conn.execute("DELETE FROM sessions WHERE session_id = '1'")


def test_api_matches_reference(loaded_db):
    client = TestClient(api.app)

    catalog = {s["session_id"]: s for s in client.get("/sessions").json()}
    assert catalog["1"]["reading_count"] == GOLDEN["reading_count"]

    stats = client.get("/stats", params={"session_id": "1", "sensor": "ECU RPM"}).json()[0]
    assert round(stats["min_value"], 4) == GOLDEN["rpm_min"]
    assert round(stats["max_value"], 4) == GOLDEN["rpm_max"]
    assert round(stats["avg_value"], 2) == round(GOLDEN["rpm_avg"], 2)
