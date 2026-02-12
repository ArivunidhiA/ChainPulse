{{
  config(
    materialized='view'
  )
}}
with transfers as (
  select * from {{ ref('stg_raw_transfers') }}
)
select
  t.id,
  t.block_number,
  t.tx_hash,
  t.log_index,
  t.token_address,
  t.from_address,
  t.to_address,
  t.amount_raw,
  t.amount,
  coalesce(t.usd_value, 0) as amount_usd,
  t.direction,
  t.is_exchange,
  t.event_timestamp,
  case
    when coalesce(t.usd_value, 0) >= 50000 then 'whale'
    when t.is_exchange then 'exchange'
    else 'standard'
  end as transfer_type
from transfers t
