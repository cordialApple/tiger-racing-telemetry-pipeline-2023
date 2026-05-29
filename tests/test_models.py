from dashboard.models import Reading, ReadingPage, Channel, SessionCatalog, SensorStat


def test_reading_fields():
    assert set(Reading.model_fields) == {
        "session_id", "sensor_name", "ts", "t_seconds",
        "value", "avg_value", "min_value", "max_value",
    }


def test_reading_page_wraps_rows():
    assert set(ReadingPage.model_fields) == {
        "session_id", "sensor", "downsample", "limit",
        "offset", "total", "count", "rows",
    }


def test_channel_carries_metadata():
    assert {"unit", "min_range", "max_range", "has_signal"} <= set(Channel.model_fields)
