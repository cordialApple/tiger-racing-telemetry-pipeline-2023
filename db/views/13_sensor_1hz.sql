CREATE MATERIALIZED VIEW IF NOT EXISTS v_sensor_1hz
WITH (timescaledb.continuous) AS
SELECT session_id, sensor_name, time_bucket('1 second', ts) AS bucket,
       avg(value) AS avg_value, min(value) AS min_value, max(value) AS max_value
FROM sensor_readings
GROUP BY session_id, sensor_name, time_bucket('1 second', ts)
WITH NO DATA;
