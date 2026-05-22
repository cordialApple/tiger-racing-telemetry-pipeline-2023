CREATE OR REPLACE VIEW v_session_sensor_stats AS
SELECT session_id, sensor_name, count(*) AS n,
       avg(value) AS avg_value, min(value) AS min_value, max(value) AS max_value
FROM sensor_readings
GROUP BY session_id, sensor_name;
