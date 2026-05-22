from datetime import timedelta


def test_session_meta(parsed):
    meta = parsed.session
    assert meta.session_id == "1"
    assert meta.source_file == "1.csv"
    assert meta.sample_rate_hz == 20
    assert meta.started_at.date().isoformat() == "2023-10-07"


def test_time_column_dropped(parsed):
    assert "Time" not in parsed.units


def test_readings_are_floats(parsed):
    assert all(isinstance(value, float) for _ts, _name, value in parsed.readings[:100])


def test_consecutive_samples_spaced_50ms(parsed):
    rpm_ts = [ts for ts, name, _v in parsed.readings if name == "ECU RPM"]
    assert rpm_ts[1] - rpm_ts[0] == timedelta(milliseconds=50)


def test_reading_count_matches_rows_times_sensors(parsed):
    assert len(parsed.readings) <= parsed.row_count * len(parsed.units)
    assert parsed.row_count == 1800
