CREATE TABLE IF NOT EXISTS sessions (
    session_id     TEXT PRIMARY KEY,
    source_file    TEXT UNIQUE NOT NULL,
    vehicle        TEXT,
    racer          TEXT,
    championship   TEXT,
    session_name   TEXT,
    comment        TEXT,
    started_at     TIMESTAMPTZ NOT NULL,
    sample_rate_hz INTEGER NOT NULL,
    duration_s     INTEGER,
    segment_times  TEXT,
    created_at     TIMESTAMPTZ DEFAULT now()
);
