CREATE OR REPLACE VIEW v_sensor_1hz_enriched AS
SELECT a.session_id, a.sensor_name, sn.unit, a.bucket AS ts,
       EXTRACT(EPOCH FROM (a.bucket - s.started_at)) AS t_seconds,
       a.avg_value AS value,
       a.avg_value, a.min_value, a.max_value
FROM v_sensor_1hz a
JOIN sessions s USING (session_id)
JOIN sensors sn USING (sensor_name);
