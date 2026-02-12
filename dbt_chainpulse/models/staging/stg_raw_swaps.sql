{{
  config(
    materialized='view'
  )
}}
with source as (
  select * from {{ source('raw', 'raw_swaps') }}
),
cleaned as (
  select
    id,
    block_number::integer as block_number,
    tx_hash,
    log_index::integer as log_index,
    lower(pool_address) as pool_address,
    lower(sender_address) as sender_address,
    lower(recipient_address) as recipient_address,
    lower(token0_address) as token0_address,
    lower(token1_address) as token1_address,
    amount0::numeric as amount0,
    amount1::numeric as amount1,
    sqrt_price_x96,
    liquidity,
    tick,
    usd_value::numeric as usd_value,
    (event_timestamp at time zone 'UTC')::timestamp as event_timestamp,
    size_bucket,
    created_at
  from source
  where tx_hash is not null
    and log_index is not null
    and block_number is not null
    and event_timestamp is not null
)
deduped as (
  select * from (
    select
      *,
      row_number() over (partition by tx_hash, log_index order by id) as rn
    from cleaned
  ) t
  where rn = 1
)
select id, block_number, tx_hash, log_index, pool_address, sender_address, recipient_address,
  token0_address, token1_address, amount0, amount1, sqrt_price_x96, liquidity, tick,
  usd_value, event_timestamp, size_bucket, created_at
from deduped
