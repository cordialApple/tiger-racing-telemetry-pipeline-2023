from fastapi.testclient import TestClient

from dashboard import api

client = TestClient(api.app)

CATALOG = [
    {"session_id": "s1", "source_file": "1.csv", "vehicle": "TR23", "racer": "A",
     "championship": None, "session_name": None,
     "started_at": "2023-01-01T00:00:00", "duration_s": None, "sample_rate_hz": 20,
     "reading_count": None, "loaded_at": None},
    {"session_id": "s2", "source_file": "2.csv", "vehicle": "TR23", "racer": "B",
     "championship": None, "session_name": None,
     "started_at": "2023-02-01T00:00:00", "duration_s": None, "sample_rate_hz": 20,
     "reading_count": None, "loaded_at": None},
]

STATS = [
    {"session_id": "s1", "sensor_name": "rpm", "n": 100, "avg_value": 5000.0,
     "min_value": 800.0, "max_value": 12000.0},
]

CHANNELS = [{
    "session_id": "s1", "sensor_name": "ECU RPM", "description": "Engine RPM",
    "unit": "rpm", "data_type": "integer", "min_range": 0, "max_range": 14000,
    "n": 1800, "avg_value": 3003.0, "min_value": 363.8, "max_value": 6860.6,
    "has_signal": True,
}]

ROW = {"session_id": "s1", "sensor_name": "rpm", "ts": "2023-01-01T00:00:00Z",
       "t_seconds": 0.0, "value": 800.0, "avg_value": 800.0,
       "min_value": 800.0, "max_value": 800.0}


def patch_query(monkeypatch, rows, capture=None):
    def fake(sql, params=()):
        if capture is not None:
            capture.append((sql, params))
        return rows
    monkeypatch.setattr(api, "run_query", fake)


def patch_scalar(monkeypatch, value, capture=None):
    def fake(sql, params=()):
        if capture is not None:
            capture.append((sql, params))
        return value
    monkeypatch.setattr(api, "scalar", fake)


def test_health_ok(monkeypatch):
    patch_query(monkeypatch, [{"?column?": 1}])
    assert client.get("/health").json() == {"status": "ok"}


def test_health_failure(monkeypatch):
    def boom(sql, params=()):
        raise RuntimeError("no db")
    monkeypatch.setattr(api, "run_query", boom)
    assert client.get("/health").status_code == 503


def test_sessions(monkeypatch):
    patch_query(monkeypatch, CATALOG)
    assert client.get("/sessions").json() == CATALOG


def test_session_sensors_returns_channel_dimension(monkeypatch):
    capture = []
    patch_query(monkeypatch, CHANNELS, capture)
    body = client.get("/sessions/s1/sensors").json()
    assert body == CHANNELS
    sql, params = capture[0]
    assert "v_session_channels" in sql and params == ["s1"]


def test_readings_requires_session_id():
    assert client.get("/readings", params={"sensor": "rpm"}).status_code == 422


def test_readings_envelope_shape(monkeypatch):
    patch_scalar(monkeypatch, 1)
    patch_query(monkeypatch, [ROW])
    body = client.get("/readings", params={"session_id": "s1", "sensor": "rpm"}).json()
    assert body["total"] == 1 and body["count"] == 1
    assert body["sensor"] == "rpm" and body["rows"] == [ROW]


def test_readings_same_columns_both_modes(monkeypatch):
    patch_scalar(monkeypatch, 1)
    patch_query(monkeypatch, [ROW])
    for mode in ("1hz", "raw"):
        body = client.get("/readings", params={
            "session_id": "s1", "downsample": mode}).json()
        assert set(body["rows"][0]) == {
            "session_id", "sensor_name", "ts", "t_seconds",
            "value", "avg_value", "min_value", "max_value"}


def test_readings_sensor_optional(monkeypatch):
    capture = []
    patch_scalar(monkeypatch, 0)
    patch_query(monkeypatch, [], capture)
    client.get("/readings", params={"session_id": "s1"})
    sql, params = capture[0]
    assert "sensor_name = %s" not in sql
    assert params[0] == "s1"


def test_readings_sensor_filters_when_supplied(monkeypatch):
    capture = []
    patch_scalar(monkeypatch, 0)
    patch_query(monkeypatch, [], capture)
    client.get("/readings", params={"session_id": "s1", "sensor": "rpm"})
    sql, params = capture[0]
    assert "sensor_name = %s" in sql and params[:2] == ["s1", "rpm"]


def test_readings_defaults_to_1hz(monkeypatch):
    capture = []
    patch_scalar(monkeypatch, 0)
    patch_query(monkeypatch, [], capture)
    client.get("/readings", params={"session_id": "s1"})
    sql, _ = capture[0]
    assert "v_sensor_1hz_enriched" in sql and "v_sensor_readings" not in sql


def test_readings_raw_branch(monkeypatch):
    capture = []
    patch_scalar(monkeypatch, 0)
    patch_query(monkeypatch, [], capture)
    client.get("/readings", params={"session_id": "s1", "downsample": "raw"})
    sql, _ = capture[0]
    assert "v_sensor_readings" in sql and "v_sensor_1hz_enriched" not in sql


def test_readings_rejects_bad_downsample():
    assert client.get("/readings", params={
        "session_id": "s1", "downsample": "5hz"}).status_code == 422


def test_readings_paging_params(monkeypatch):
    capture = []
    patch_scalar(monkeypatch, 0)
    patch_query(monkeypatch, [], capture)
    client.get("/readings", params={
        "session_id": "s1", "sensor": "rpm",
        "start": "2023-01-01", "end": "2023-01-02", "limit": 10, "offset": 20})
    sql, params = capture[0]
    assert "LIMIT %s OFFSET %s" in sql
    assert params == ["s1", "rpm", "2023-01-01", "2023-01-02", 10, 20]


def test_readings_limit_and_offset_bounds():
    assert client.get("/readings", params={
        "session_id": "s1", "limit": 0}).status_code == 422
    assert client.get("/readings", params={
        "session_id": "s1", "offset": -1}).status_code == 422


def test_stats(monkeypatch):
    capture = []
    patch_query(monkeypatch, STATS, capture)
    assert client.get("/stats", params={"session_id": "s1"}).json() == STATS
    sql, params = capture[0]
    assert "v_session_sensor_stats" in sql
    assert params == ["s1"]


def test_stats_requires_session_id():
    assert client.get("/stats").status_code == 422
