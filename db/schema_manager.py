from pathlib import Path

from db.connection import Database

_DB_DIR = Path(__file__).parent
_VIEWS_DIR = _DB_DIR / "views"


def split_statements(sql: str) -> list[str]:
    statements = []
    for fragment in sql.split(";"):
        lines = [
            line for line in fragment.splitlines()
            if line.strip() and not line.strip().startswith("--")
        ]
        statement = "\n".join(lines).strip()
        if statement:
            statements.append(statement)
    return statements


class SchemaManager:
    def __init__(self, database: Database):
        self.database = database

    def apply(self):
        with self.database.connection() as conn:
            conn.autocommit = True
            for path in self._ordered_files():
                for statement in split_statements(path.read_text()):
                    conn.execute(statement)

    def refresh_views(self):
        with self.database.connection() as conn:
            conn.autocommit = True
            conn.execute("CALL refresh_continuous_aggregate('v_sensor_1hz', NULL, NULL)")

    def _ordered_files(self) -> list[Path]:
        tables = sorted(_DB_DIR.glob("*.sql"), key=lambda p: p.name)
        views = sorted(_VIEWS_DIR.glob("*.sql"), key=lambda p: p.name)
        return tables + views
