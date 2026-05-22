from contextlib import contextmanager
from datetime import datetime, timezone

from loader.pipeline import Pipeline
from parser.models import ParsedSession, SessionMeta
from parser.validator import ValidationReport


class FakeDb:
    @contextmanager
    def connection(self):
        yield object()


class FakeRepo:
    def __init__(self, loaded=False):
        self.loaded = loaded
        self.upserts = 0
        self.logged = []

    def is_loaded(self, conn, packet_id):
        return self.loaded

    def upsert_sensors(self, conn, specs):
        self.upserts += 1

    def insert_session(self, conn, meta):
        pass

    def copy_readings(self, conn, session_id, readings):
        return len(readings)

    def log_ingestion(self, conn, *args):
        self.logged.append(args)


class FakeValidator:
    def validate(self, readings):
        return ValidationReport(out_of_range=0)


class FakeParser:
    def __init__(self, fail_on=()):
        self.fail_on = set(fail_on)

    def parse(self, path):
        if path.name in self.fail_on:
            raise ValueError("bad file")
        meta = SessionMeta(
            session_id=path.stem, source_file=path.name, vehicle=None, racer=None,
            championship=None, session_name=None, comment=None,
            started_at=datetime(2023, 10, 7, tzinfo=timezone.utc),
            sample_rate_hz=20, duration_s=1, segment_times=None,
        )
        readings = [(meta.started_at, "ECU RPM", 1000.0), (meta.started_at, "ECU RPM", 2000.0)]
        return ParsedSession(meta, {"ECU RPM": "rpm"}, readings, path.stem, 1)


def make_pipeline(tmp_path, repo, parser):
    raw = tmp_path / "raw"
    raw.mkdir()
    return Pipeline(FakeDb(), raw, tmp_path / "processed", parser, FakeValidator(), repo, [])


def test_loads_and_moves_file(tmp_path):
    repo = FakeRepo(loaded=False)
    pipe = make_pipeline(tmp_path, repo, FakeParser())
    (pipe.source_dir / "1.csv").write_text("x")

    result = pipe.run()[0]

    assert result.status == "loaded"
    assert result.readings == 2
    assert repo.upserts == 1
    assert not (pipe.source_dir / "1.csv").exists()
    assert (pipe.processed_dir / "1.csv").exists()


def test_skips_when_already_loaded(tmp_path):
    repo = FakeRepo(loaded=True)
    pipe = make_pipeline(tmp_path, repo, FakeParser())
    (pipe.source_dir / "1.csv").write_text("x")

    result = pipe.run()[0]

    assert result.status == "skipped"
    assert (pipe.source_dir / "1.csv").exists()
    assert repo.logged == []


def test_error_isolation_continues(tmp_path):
    repo = FakeRepo(loaded=False)
    pipe = make_pipeline(tmp_path, repo, FakeParser(fail_on={"1.csv"}))
    (pipe.source_dir / "1.csv").write_text("x")
    (pipe.source_dir / "2.csv").write_text("x")

    by_file = {r.source_file: r for r in pipe.run()}

    assert by_file["1.csv"].status == "error"
    assert by_file["2.csv"].status == "loaded"
    assert (pipe.source_dir / "1.csv").exists()
    assert (pipe.processed_dir / "2.csv").exists()
