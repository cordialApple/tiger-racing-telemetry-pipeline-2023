from fastapi.testclient import TestClient

from dashboard import api

client = TestClient(api.app)

CATALOG = [
    {"session_id": "s1", "vehicle": "TR23", "racer": "A", "started_at": "2023-01-01T00:00:00"},
    {"session_id": "s2", "vehicle": "TR23", "racer": "B", "started_at": "2023-02-01T00:00:00"},
]

STATS = [
    {"session_id": "s1", "sensor_name": "rpm", "n": 100, "avg_value": 5000.0,
     "min_value": 800.0, "max_value": 12000.0},
]


def patch_helper(monkeypatch, rows, capture=None):
    def fake(sql, params=()):
        if capture is not None:
            capture.append((sql, params))
        return rows
    monkeypatch.setattr(api, "run_query", fake)


def test_health_ok(monkeypatch):
    patch_helper(monkeypatch, [{"?column?": 1}])
    assert client.get("/health").json() == {"status": "ok"}


def test_health_failure(monkeypatch):
    def boom(sql, params=()):
        raise RuntimeError("no db")
    monkeypatch.setattr(api, "run_query", boom)
    assert client.get("/health").status_code == 503


def test_sessions(monkeypatch):
    patch_helper(monkeypatch, CATALOG)
    assert client.get("/sessions").json() == CATALOG


def test_session_sensors(monkeypatch):
    patch_helper(monkeypatch, [{"sensor_name": "rpm"}, {"sensor_name": "speed"}])
    assert client.get("/sessions/s1/sensors").json() == [
        {"sensor_name": "rpm"}, {"sensor_name": "speed"}
    ]


def test_readings_requires_session_id():
    assert client.get("/readings", params={"sensor": "rpm"}).status_code == 422


def test_readings_requires_sensor():
    assert client.get("/readings", params={"session_id": "s1"}).status_code == 422


def test_readings_defaults_to_1hz(monkeypatch):
    capture = []
    patch_helper(monkeypatch, [], capture)
    client.get("/readings", params={"session_id": "s1", "sensor": "rpm"})
    sql, params = capture[0]
    assert "v_sensor_1hz" in sql and "v_sensor_readings" not in sql
    assert params[:2] == ["s1", "rpm"]


def test_readings_raw_branch(monkeypatch):
    capture = []
    patch_helper(monkeypatch, [], capture)
    client.get("/readings", params={"session_id": "s1", "sensor": "rpm", "downsample": "raw"})
    sql, _ = capture[0]
    assert "v_sensor_readings" in sql and "v_sensor_1hz" not in sql


def test_readings_applies_range_and_limit(monkeypatch):
    capture = []
    patch_helper(monkeypatch, [], capture)
    client.get("/readings", params={
        "session_id": "s1", "sensor": "rpm",
        "start": "2023-01-01", "end": "2023-01-02", "limit": 10,
    })
    sql, params = capture[0]
    assert "LIMIT" in sql
    assert params == ["s1", "rpm", "2023-01-01", "2023-01-02", 10]


def test_stats(monkeypatch):
    capture = []
    patch_helper(monkeypatch, STATS, capture)
    assert client.get("/stats", params={"session_id": "s1"}).json() == STATS
    sql, params = capture[0]
    assert "v_session_sensor_stats" in sql
    assert params == ["s1"]


def test_stats_requires_session_id():
    assert client.get("/stats").status_code == 422
