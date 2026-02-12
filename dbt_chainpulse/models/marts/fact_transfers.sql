{{
  config(
    materialized='incremental',
    unique_key='transfer_id',
    incremental_strategy='merge',
    merge_update_columns=['amount_usd', 'direction']
  )
}}
with enriched as (
  select * from {{ ref('int_transfers_enriched') }}
)
select
  {{ dbt_utils.generate_surrogate_key(['tx_hash', 'log_index']) }} as transfer_id,
  block_number,
  tx_hash,
  from_address,
  to_address,
  token_address,
  amount,
  amount_usd,
  coalesce(direction, 'unknown') as direction,
  event_timestamp
from enriched
{% if is_incremental() %}
where event_timestamp > (select max(event_timestamp) from {{ this }})
{% endif %}
