{{
  config(
    materialized='incremental',
    unique_key='date_bucket',
    incremental_strategy='merge'
  )
}}
with daily as (
  select
    date_trunc('day', event_timestamp)::date as date_bucket,
    count(distinct wallet_address) as unique_wallets,
    count(*) as total_swaps,
    sum(amount_usd) as total_volume,
    percentile_cont(0.5) within group (order by amount_usd) as median_swap_size
  from {{ ref('fact_swaps') }}
  group by 1
)
select
  date_bucket,
  unique_wallets,
  total_swaps,
  total_volume,
  median_swap_size
from daily
{% if is_incremental() %}
where date_bucket > (select max(date_bucket) from {{ this }})
{% endif %}
