from datetime import datetime, timezone

import pytest

from db.connection import Database
from db.repository import ReadingRepository
from db.schema_manager import SchemaManager
from parser.models import SensorSpec, SessionMeta

SESSION_ID = "test_session_repo"
PACKET_ID = "test_packet_repo"
SOURCE_FILE = "test_repo_fixture.csv"
STARTED = datetime(2023, 6, 1, 12, 0, 0, tzinfo=timezone.utc)


@pytest.fixture(scope="module")
def database():
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
    yield db
    db.close()


def _cleanup(conn):
    conn.execute("DELETE FROM sensor_readings WHERE session_id = %s", (SESSION_ID,))
    conn.execute("DELETE FROM ingestion_log WHERE packet_id = %s", (PACKET_ID,))
    conn.execute("DELETE FROM sessions WHERE session_id = %s", (SESSION_ID,))


def test_full_ingestion_cycle(database):
    SchemaManager(database).apply()
    repo = ReadingRepository()

    sensors = [
        SensorSpec("rpm", "Engine RPM", "rpm", "float", 0, 15000),
        SensorSpec("speed", "Vehicle speed", "kph", "float", 0, 300),
    ]
    readings = [
        (STARTED, "rpm", 1000.0),
        (STARTED, "speed", 25.0),
        (STARTED.replace(second=1), "rpm", 2000.0),
        (STARTED.replace(second=1), "speed", 40.0),
    ]
    meta = SessionMeta(
        session_id=SESSION_ID, source_file=SOURCE_FILE, vehicle="TR23", racer="Driver",
        championship="FSAE", session_name="Test", comment=None, started_at=STARTED,
        sample_rate_hz=20, duration_s=2, segment_times=None,
    )

    with database.connection() as conn:
        _cleanup(conn)
        repo.upsert_sensors(conn, sensors)
        repo.insert_session(conn, meta)
        assert repo.is_loaded(conn, PACKET_ID) is False

        written = repo.copy_readings(conn, SESSION_ID, readings)
        assert written == len(readings)

        repo.log_ingestion(conn, PACKET_ID, SESSION_ID, SOURCE_FILE, 2, written)
        assert repo.is_loaded(conn, PACKET_ID) is True

        n = conn.execute(
            "SELECT count(*) FROM sensor_readings WHERE session_id = %s", (SESSION_ID,)
        ).fetchone()[0]
        assert n == len(readings)

        _cleanup(conn)
