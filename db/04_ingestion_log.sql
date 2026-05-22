CREATE TABLE IF NOT EXISTS ingestion_log (
    packet_id     TEXT PRIMARY KEY,
    session_id    TEXT NOT NULL REFERENCES sessions(session_id),
    source_file   TEXT NOT NULL,
    row_count     INTEGER NOT NULL,
    reading_count BIGINT NOT NULL,
    loaded_at     TIMESTAMPTZ DEFAULT now()
);
