{{
  config(
    materialized='view'
  )
}}
select
  a.anomaly_id,
  a.hour_bucket,
  a.token_address,
  a.actual_volume,
  a.expected_volume,
  a.z_score,
  a.severity,
  a.detected_at
from {{ source('analytics_raw', 'analytics_anomalies') }} a
