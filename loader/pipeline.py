import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass
class FileResult:
    source_file: str
    status: str
    readings: int = 0
    out_of_range: int = 0
    error: str | None = None


class Pipeline:
    def __init__(self, db, source_dir, processed_dir, parser, validator, repo, specs):
        self.db = db
        self.source_dir = Path(source_dir)
        self.processed_dir = Path(processed_dir)
        self.parser = parser
        self.validator = validator
        self.repo = repo
        self.specs = specs

    def run(self) -> list[FileResult]:
        with self.db.connection() as conn:
            self.repo.upsert_sensors(conn, self.specs)
        return [self.process(p) for p in sorted(self.source_dir.glob("*.csv"))]

    def process(self, path: Path) -> FileResult:
        try:
            return self._load(path)
        except Exception as e:
            return FileResult(path.name, "error", error=str(e))

    def _load(self, path: Path) -> FileResult:
        parsed = self.parser.parse(path)
        with self.db.connection() as conn:
            if self.repo.is_loaded(conn, parsed.packet_id):
                return FileResult(parsed.session.source_file, "skipped")
            report = self.validator.validate(parsed.readings)
            self.repo.insert_session(conn, parsed.session)
            written = self.repo.copy_readings(conn, parsed.session.session_id, parsed.readings)
            self.repo.log_ingestion(
                conn, parsed.packet_id, parsed.session.session_id,
                parsed.session.source_file, parsed.row_count, written,
            )
        self._archive(path)
        return FileResult(parsed.session.source_file, "loaded", written, report.out_of_range)

    def _archive(self, path: Path):
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(path), str(self.processed_dir / path.name))
