{{
  config(
    materialized='incremental',
    unique_key='swap_id',
    incremental_strategy='merge',
    merge_update_columns=['amount_usd', 'is_whale', 'wallet_segment']
  )
}}
with enriched as (
  select * from {{ ref('int_swaps_enriched') }}
)
select
  {{ dbt_utils.generate_surrogate_key(['tx_hash', 'log_index']) }} as swap_id,
  block_number,
  tx_hash,
  wallet_address,
  token0_address as token_in_address,
  token1_address as token_out_address,
  amount0 as amount_in,
  amount1 as amount_out,
  amount_usd,
  pool_address,
  null::integer as gas_used,
  null::numeric as gas_price_gwei,
  event_timestamp,
  is_whale,
  null::numeric as anomaly_score,
  'retail' as wallet_segment
from enriched
{% if is_incremental() %}
where event_timestamp > (select max(event_timestamp) from {{ this }})
{% endif %}
