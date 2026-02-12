{{
  config(
    materialized='view'
  )
}}
select
  hour_bucket,
  token_address,
  inflow_usd,
  outflow_usd,
  net_flow_usd,
  unique_senders,
  unique_receivers,
  flow_direction
from {{ source('analytics_raw', 'analytics_token_flows') }}
