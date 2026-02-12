{{
  config(
    materialized='view'
  )
}}
with source as (
  select * from {{ source('raw', 'raw_transfers') }}
),
cleaned as (
  select
    id,
    block_number::integer as block_number,
    tx_hash,
    log_index::integer as log_index,
    lower(token_address) as token_address,
    lower(from_address) as from_address,
    lower(to_address) as to_address,
    amount_raw::numeric as amount_raw,
    amount::numeric as amount,
    usd_value::numeric as usd_value,
    direction,
    coalesce(is_exchange, false) as is_exchange,
    (event_timestamp at time zone 'UTC')::timestamp as event_timestamp,
    created_at
  from source
  where tx_hash is not null
    and log_index is not null
    and block_number is not null
    and event_timestamp is not null
    and usd_value >= 1000
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
select id, block_number, tx_hash, log_index, token_address, from_address, to_address,
  amount_raw, amount, usd_value, direction, is_exchange, event_timestamp, created_at
from deduped
