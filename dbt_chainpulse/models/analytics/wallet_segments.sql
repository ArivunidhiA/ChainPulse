{{
  config(
    materialized='view'
  )
}}
select
  wallet_address,
  segment,
  cluster_id,
  rfm_recency,
  rfm_frequency,
  rfm_volume,
  computed_at
from {{ source('analytics_raw', 'analytics_wallet_segments') }}
