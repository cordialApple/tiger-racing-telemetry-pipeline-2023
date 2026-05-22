from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class SensorSpec:
    name: str
    description: str
    unit: str | None
    data_type: str
    min_range: float | None
    max_range: float | None


@dataclass(frozen=True)
class SessionMeta:
    session_id: str
    source_file: str
    vehicle: str | None
    racer: str | None
    championship: str | None
    session_name: str | None
    comment: str | None
    started_at: datetime
    sample_rate_hz: int
    duration_s: int | None
    segment_times: str | None


@dataclass
class ParsedSession:
    session: SessionMeta
    units: dict[str, str]
    readings: list[tuple[datetime, str, float]]
    packet_id: str
    row_count: int
