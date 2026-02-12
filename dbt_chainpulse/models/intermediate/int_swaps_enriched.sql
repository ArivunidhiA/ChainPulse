{{
  config(
    materialized='view'
  )
}}
with swaps as (
  select * from {{ ref('stg_raw_swaps') }}
),
tokens as (
  select * from {{ ref('dim_tokens') }}
)
select
  s.id,
  s.block_number,
  s.tx_hash,
  s.log_index,
  s.pool_address,
  s.sender_address as wallet_address,
  s.token0_address,
  s.token1_address,
  s.amount0,
  s.amount1,
  coalesce(s.usd_value, 0) as amount_usd,
  s.event_timestamp,
  date_trunc('hour', s.event_timestamp) as hour_bucket,
  date_trunc('day', s.event_timestamp)::date as day_bucket,
  date_trunc('week', s.event_timestamp)::date as week_bucket,
  s.size_bucket,
  case when coalesce(s.usd_value, 0) >= 50000 then true else false end as is_whale
from swaps s
