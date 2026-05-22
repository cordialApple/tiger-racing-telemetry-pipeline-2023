CREATE TABLE IF NOT EXISTS sensors (
    sensor_name TEXT PRIMARY KEY,
    description TEXT,
    unit        TEXT,
    data_type   TEXT NOT NULL CHECK (data_type IN ('integer', 'float', 'boolean')),
    min_range   NUMERIC,
    max_range   NUMERIC,
    CONSTRAINT range_check CHECK (min_range IS NULL OR max_range IS NULL OR max_range > min_range)
);
