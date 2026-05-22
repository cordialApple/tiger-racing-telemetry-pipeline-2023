from contextlib import contextmanager
from dataclasses import dataclass

from psycopg_pool import ConnectionPool

import config


@dataclass(frozen=True)
class TimescaleConfig:
    dbname: str = config.DB_NAME
    user: str = config.DB_USER
    password: str = config.DB_PASSWORD
    host: str = config.DB_HOST
    port: int = config.DB_PORT

    def dsn(self) -> str:
        return (
            f"dbname={self.dbname} user={self.user} password={self.password} "
            f"host={self.host} port={self.port}"
        )


class Database:
    def __init__(self, cfg: TimescaleConfig = TimescaleConfig()):
        self.cfg = cfg
        self._pool: ConnectionPool | None = None

    @property
    def pool(self) -> ConnectionPool:
        if self._pool is None:
            self._pool = ConnectionPool(self.cfg.dsn(), open=True)
        return self._pool

    @contextmanager
    def connection(self):
        with self.pool.connection() as conn:
            yield conn

    def close(self):
        if self._pool is not None:
            self._pool.close()
            self._pool = None
