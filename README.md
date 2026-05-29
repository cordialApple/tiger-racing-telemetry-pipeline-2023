# Tiger Racing Telemetry Pipeline

Offline pipeline that turns 2023 AiM logger exports into a queryable TimescaleDB
and serves them over a REST API for a PowerBI performance dashboard.

Per session file the flow is: clean, validate, parse, load into the schema, then
expose SQL views through the API.

## Layout

```
config.py         centralized paths, API host/port, and DB connection defaults
data/raw/         AiM CSV exports (one file per session)
data/processed/   files move here after a successful load
parser/           CSV cleaner, AiM parser, sensor spec loader, advisory validator
db/               psycopg connection, schema (.sql per table), repository, views/
loader/           ingestion pipeline (per-file error isolation)
dashboard/        FastAPI REST API consumed by PowerBI
docs/             sensorspecs.md (advisory sensor ranges)
main.py           entrypoint (ingest / serve / all)
```

## Setup

```
docker compose up -d            # TimescaleDB on localhost:5432 (waits for healthcheck)
pip install -r requirements.txt
```

Defaults live in `config.py` and are overridable via `PGHOST`, `PGPORT`, `PGUSER`,
`PGPASSWORD`, `PGDATABASE`, `API_HOST`, `API_PORT`.

## Run

```
python main.py ingest    # apply schema, then load every file in data/raw
python main.py serve     # start the REST API
python main.py all       # ingest then serve (default)
```

Loading is idempotent: each file is keyed by a content hash in `ingestion_log`, so
re-running skips files already loaded. A file that fails to parse or load is
reported and left in `data/raw` for retry; the rest of the batch continues.

## Schema

- `sessions` — one row per logger file.
- `sensors` — registry seeded from `docs/sensorspecs.md`.
- `sensor_readings` — long-format hypertable `(ts, session_id, sensor_name, value)`;
  timestamps synthesized from the session start at the file's sample rate. No FK
  constraints (integrity enforced by the pipeline) to keep COPY fast.
- `ingestion_log` — content-hash packet tracking for idempotency.

## Views (PowerBI)

- `v_session_catalog` — session list with reading counts.
- `v_sensor_readings` — raw long-format readings with unit, elapsed seconds, and
  `value` mirrored as `avg_value`/`min_value`/`max_value` so the raw feed shares
  one column set with the 1 Hz feed.
- `v_session_sensor_stats` — per session/sensor count, avg, min, max.
- `v_sensor_1hz` — 1 Hz TimescaleDB continuous aggregate (`bucket`, `avg`/`min`/`max`).
- `v_sensor_1hz_enriched` — `v_sensor_1hz` joined to session and sensor metadata
  (exposes `ts`, `t_seconds`, `unit`, and the same `value`/`avg`/`min`/`max`
  columns as `v_sensor_readings`).
- `v_session_channels` — channel dimension per session: sensor spec metadata
  plus `n`/`avg`/`min`/`max` from the stats view and a `has_signal` flag
  (`false` when both min and max are 0).

## PowerBI connection

Point PowerBI's Web/JSON connector at `http://localhost:8000`. Each endpoint
returns one fixed column set, validated by Pydantic `response_model`:

- `GET /sessions` — Sessions dimension (from `v_session_catalog`).
- `GET /sessions/{session_id}/sensors` — Channel dimension (from
  `v_session_channels`).
- `GET /readings?session_id=&sensor=&start=&end=&downsample=1hz|raw&limit=&offset=` —
  paginated envelope `{session_id, sensor, downsample, limit, offset, total,
  count, rows}`. Omit `sensor` for the full long-format fact feed (all channels);
  supply it to drill into one channel. `raw` and `1hz` rows have the same eight
  columns. `total` enables PowerBI to page deterministically.
- `GET /stats?session_id=&sensor=` — pre-aggregated fact (from
  `v_session_sensor_stats`).

The star-schema mapping in PowerBI:

- `Sessions[session_id]` one-to-many `Readings[session_id]`
- `Channels[session_id, sensor_name]` one-to-many `Readings[sensor_name]`
- `Stats` relates by both keys as a parallel summary fact

The live OpenAPI schema for setting up the connector is served at
`http://localhost:8000/docs`.

## Tests

```
pytest
```

Unit and parser-parity tests run without a database. The repository and DB-backed
parity tests run against a live TimescaleDB and skip when one is not available.

CI (`.github/workflows/tests.yml`) runs the full suite on push and PR against a
`timescale/timescaledb` service container, so the DB-backed tests — including the
hypertable and continuous-aggregate DDL — actually execute there.
