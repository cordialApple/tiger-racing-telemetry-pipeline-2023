CREATE OR REPLACE VIEW v_sensor_readings AS
SELECT r.session_id, r.sensor_name, sn.unit, r.ts,
       EXTRACT(EPOCH FROM (r.ts - s.started_at)) AS t_seconds, r.value
FROM sensor_readings r
JOIN sessions s USING (session_id)
JOIN sensors sn USING (sensor_name);
