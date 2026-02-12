{{
  config(
    materialized='view'
  )
}}
with source as (
  select * from {{ source('raw', 'raw_events') }}
),
cleaned as (
  select
    id,
    block_number::integer as block_number,
    tx_hash,
    log_index::integer as log_index,
    lower(contract_address) as contract_address,
    event_name,
    event_params,
    (event_timestamp at time zone 'UTC')::timestamp as event_timestamp,
    created_at
  from source
  where tx_hash is not null
    and log_index is not null
    and block_number is not null
    and event_timestamp is not null
    and event_timestamp <= current_timestamp
),
deduped as (
  select * from (
    select
      *,
      row_number() over (partition by tx_hash, log_index order by id) as rn
    from cleaned
  ) t
  where rn = 1
)
select id, block_number, tx_hash, log_index, contract_address, event_name, event_params, event_timestamp, created_at
from deduped
