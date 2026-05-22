import csv
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from parser.cleaner import strip_leading_comma
from parser.models import ParsedSession, SessionMeta

_TZ = ZoneInfo("America/Chicago")
_DATETIME_FORMAT = "%A, %B %d, %Y %I:%M %p"
_META_ROWS = 13


class AimParser:
    def parse(self, path) -> ParsedSession:
        path = Path(path)
        raw = path.read_bytes()
        packet_id = hashlib.sha256(raw).hexdigest()

        lines = raw.decode("utf-8").splitlines()
        meta = self._read_meta(lines)
        header_idx = self._find_header(lines)
        sensors = self._row(lines[header_idx])[1:]
        units = dict(zip(sensors, self._row(lines[header_idx + 1])[1:]))

        session = self._build_session(path, meta)
        data_lines = [line for line in lines[header_idx + 2:] if line.strip()]
        period = timedelta(seconds=1 / session.sample_rate_hz)

        return ParsedSession(
            session=session,
            units=units,
            readings=self._readings(data_lines, sensors, session.started_at, period),
            packet_id=packet_id,
            row_count=len(data_lines),
        )

    def _read_meta(self, lines: list[str]) -> dict[str, str]:
        meta = {}
        for line in lines[:_META_ROWS]:
            row = self._row(line)
            if len(row) >= 2:
                meta[row[0]] = row[1]
        return meta

    def _find_header(self, lines: list[str]) -> int:
        for i, line in enumerate(lines):
            row = self._row(line)
            if row and row[0] == "Time" and len(row) > 2:
                return i
        raise ValueError("column-name row not found")

    def _build_session(self, path: Path, meta: dict[str, str]) -> SessionMeta:
        started_at = datetime.strptime(
            f"{meta['Date']} {meta['Time']}", _DATETIME_FORMAT
        ).replace(tzinfo=_TZ)
        return SessionMeta(
            session_id=path.stem,
            source_file=path.name,
            vehicle=meta.get("Vehicle"),
            racer=meta.get("Racer"),
            championship=meta.get("Championship"),
            session_name=meta.get("Session"),
            comment=meta.get("Comment") or None,
            started_at=started_at,
            sample_rate_hz=int(meta["Sample Rate"]),
            duration_s=int(meta["Duration"]) if meta.get("Duration") else None,
            segment_times=meta.get("Segment Times") or None,
        )

    def _readings(self, data_lines, sensors, started_at, period):
        rows = []
        for index, line in enumerate(data_lines):
            ts = started_at + index * period
            for name, value in zip(sensors, self._row(strip_leading_comma(line))):
                if value:
                    rows.append((ts, name, float(value)))
        return rows

    @staticmethod
    def _row(line: str) -> list[str]:
        return next(csv.reader([line]))
