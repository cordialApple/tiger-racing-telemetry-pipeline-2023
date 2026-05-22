# Tiger Racing Telemetry Pipeline — Agent Context

Reference for agents working on `feat/pipeline`. Keep current as features land.

## Repository

- **Repo:** `cordialApple/tiger-racing-telemetry-pipeline-2023`
- **Active branch:** `feat/pipeline` (clean rebuild, cut from `main`)
- **Reference branch:** `claude/fsae-telemetry-pipeline-gjvgF` (the prior iterative
  build; behavior frozen as `tests/golden/session_1.json` for parity)

## Folder structure

```
config.py                 paths + API host/port + DB connection defaults (single source)
data/raw/, data/processed/
parser/
  models.py               SensorSpec, SessionMeta, ParsedSession(readings: list)
  cleaner.py              strip_leading_comma(line)  (function, not class)
  aim_parser.py           AimParser.parse(path) -> ParsedSession
  specs.py                SpecLoader.load() -> list[SensorSpec]
  validator.py            SensorValidator + ValidationReport(out_of_range, unknown_sensors)
db/
  connection.py           TimescaleConfig (config-driven) + Database (pool)
  schema_manager.py       SchemaManager.apply() + refresh_views(); split_statements()
  repository.py           ReadingRepository (conn-only methods, no Database field)
  00_extension..04_ingestion_log.sql
  views/10..13.sql
loader/
  pipeline.py             Pipeline + FileResult (per-file error isolation)
dashboard/
  api.py                  FastAPI; _1hz_query/_raw_query builders
docs/sensorspecs.md
tests/
  conftest.py             session-scoped `parsed` fixture (1.csv)
  test_*.py               unit tests incl. test_pipeline.py
  test_parity.py          parser + DB parity vs golden snapshot
  golden/session_1.json   frozen reference behavior
main.py                   ingest / serve / all
docker-compose.yml        timescaledb + pg_isready healthcheck
```

## Completed features (commit per feature, Conventional Commits)

| Feature | Files | Commit type |
|---|---|---|
| Scaffold: layout, config, deps, compose healthcheck | `config.py`, `requirements.txt`, `docker-compose.yml` | `chore` |
| AiM cleaner, models, parser, spec loader | `parser/*` | `feat(parser)` |
| FSAE sensor specifications | `docs/sensorspecs.md` | `docs` |
| Advisory sensor validator | `parser/validator.py` | `feat(parser)` |
| TimescaleDB schema + connection + manager | `db/connection.py`, `schema_manager.py`, `*.sql` | `feat(db)` |
| PowerBI views + continuous aggregate | `db/views/*` | `feat(db)` |
| Idempotent reading repository | `db/repository.py` | `feat(db)` |
| REST API over views | `dashboard/api.py` | `feat(dashboard)` |
| Ingestion pipeline + per-file error handling | `loader/pipeline.py` | `feat(loader)` |
| Pipeline entrypoint | `main.py` | `feat` |
| Parity tests + golden snapshot | `tests/test_parity.py`, `tests/golden/` | `test` |
| README + context | `README.md`, `context.md` | `docs` |

## Design invariants (baked in from commit 1)

- `sensor_readings`: PK `(session_id, sensor_name, ts)`, hypertable on `ts`, one
  secondary index `(sensor_name, ts DESC)`, **no FK constraints**.
- `ingestion_log` has no `status` column; the row's existence is the signal.
- `parser/cleaner.py` is a function; `ParsedSession.readings` is a `list`.
- `ValidationReport` carries only `out_of_range` + `unknown_sensors`.
- `SchemaManager.refresh_views()` owns the continuous-aggregate refresh; the
  repository takes a `conn` and owns no `Database`.
- `dashboard/api.py` builds `/readings` SQL via `_1hz_query`/`_raw_query` — no
  f-string SQL; all user values parameterized with `%s`.
- Bulk load via psycopg3 `COPY`; schema DDL applied per-statement under autocommit.
- Pipeline isolates failures per file (`FileResult(status="error")`) and continues.

## Data contract (parser/models.py)

- `SensorSpec(name, description, unit, data_type, min_range, max_range)`
- `SessionMeta(session_id, source_file, vehicle, racer, championship, session_name,
  comment, started_at: tz-aware America/Chicago, sample_rate_hz, duration_s,
  segment_times)`
- `ParsedSession(session, units: dict, readings: list[(ts, sensor_name, value)],
  packet_id: sha256, row_count)`

## Conventions

- **Branch:** `feat/pipeline`. One feature per commit, Conventional Commits
  (`feat`/`fix`/`refactor`/`test`/`docs`/`chore`, scopes `parser`/`db`/`loader`/
  `dashboard`). Commit only after the relevant tests pass.
- **Push:** `git push -u origin feat/pipeline`; retry on network error with backoff.
- **Code:** no emojis, no decorative prints, minimal comments, succinct names,
  single responsibility, no god classes. psycopg v3 only. No f-string SQL over user
  input. API reads views only, never base tables.
- **Tests:** unit + parser-parity run without a DB; DB-backed tests skip when
  TimescaleDB is absent (check `pg_available_extensions`).
