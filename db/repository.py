from parser.models import SensorSpec, SessionMeta

_UPSERT_SENSORS = """
INSERT INTO sensors (sensor_name, description, unit, data_type, min_range, max_range)
VALUES (%s, %s, %s, %s, %s, %s)
ON CONFLICT (sensor_name) DO UPDATE SET
    description = EXCLUDED.description,
    unit = EXCLUDED.unit,
    data_type = EXCLUDED.data_type,
    min_range = EXCLUDED.min_range,
    max_range = EXCLUDED.max_range
"""

_INSERT_SESSION = """
INSERT INTO sessions (session_id, source_file, vehicle, racer, championship,
                      session_name, comment, started_at, sample_rate_hz,
                      duration_s, segment_times)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (session_id) DO NOTHING
"""

_INSERT_INGESTION = """
INSERT INTO ingestion_log (packet_id, session_id, source_file, row_count, reading_count)
VALUES (%s, %s, %s, %s, %s)
"""


class ReadingRepository:
    def is_loaded(self, conn, packet_id) -> bool:
        row = conn.execute(
            "SELECT 1 FROM ingestion_log WHERE packet_id = %s", (packet_id,)
        ).fetchone()
        return row is not None

    def upsert_sensors(self, conn, specs: list[SensorSpec]):
        rows = [
            (s.name, s.description, s.unit, s.data_type, s.min_range, s.max_range)
            for s in specs
        ]
        with conn.cursor() as cur:
            cur.executemany(_UPSERT_SENSORS, rows)

    def insert_session(self, conn, meta: SessionMeta):
        conn.execute(_INSERT_SESSION, (
            meta.session_id, meta.source_file, meta.vehicle, meta.racer,
            meta.championship, meta.session_name, meta.comment, meta.started_at,
            meta.sample_rate_hz, meta.duration_s, meta.segment_times,
        ))

    def copy_readings(self, conn, session_id, readings) -> int:
        count = 0
        with conn.cursor().copy(
            "COPY sensor_readings (ts, session_id, sensor_name, value) FROM STDIN"
        ) as cp:
            for ts, name, value in readings:
                cp.write_row((ts, session_id, name, value))
                count += 1
        return count

    def log_ingestion(self, conn, packet_id, session_id, source_file, row_count, reading_count):
        conn.execute(
            _INSERT_INGESTION,
            (packet_id, session_id, source_file, row_count, reading_count),
        )
