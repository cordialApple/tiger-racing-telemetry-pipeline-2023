CREATE OR REPLACE VIEW v_session_channels AS
SELECT st.session_id, st.sensor_name, sn.description, sn.unit,
       sn.data_type, sn.min_range, sn.max_range,
       st.n, st.avg_value, st.min_value, st.max_value,
       NOT (st.min_value = 0 AND st.max_value = 0) AS has_signal
FROM v_session_sensor_stats st
JOIN sensors sn USING (sensor_name);
