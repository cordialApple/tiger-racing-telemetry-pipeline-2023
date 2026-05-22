CREATE TABLE IF NOT EXISTS sensor_readings (
    ts          TIMESTAMPTZ NOT NULL,
    session_id  TEXT NOT NULL,
    sensor_name TEXT NOT NULL,
    value       DOUBLE PRECISION,
    PRIMARY KEY (session_id, sensor_name, ts)
);

SELECT create_hypertable('sensor_readings', 'ts', if_not_exists => TRUE, chunk_time_interval => INTERVAL '1 day');

CREATE INDEX IF NOT EXISTS idx_readings_sensor_ts ON sensor_readings (sensor_name, ts DESC);
