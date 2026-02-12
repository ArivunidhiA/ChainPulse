{{
  config(
    materialized='incremental',
    unique_key=['hour_bucket', 'token_address'],
    incremental_strategy='merge'
  )
}}
with swaps as (
  select
    date_trunc('hour', event_timestamp) as hour_bucket,
    token_in_address as token_address,
    count(*) as swap_count,
    sum(amount_usd) as volume_usd,
    count(distinct wallet_address) as unique_wallets,
    avg(amount_usd) as avg_size,
    max(amount_usd) as max_size
  from {{ ref('fact_swaps') }}
  group by 1, 2
)
select
  hour_bucket,
  token_address,
  swap_count,
  volume_usd,
  unique_wallets,
  avg_size,
  max_size
from swaps
{% if is_incremental() %}
where hour_bucket > (select max(hour_bucket) from {{ this }})
{% endif %}
