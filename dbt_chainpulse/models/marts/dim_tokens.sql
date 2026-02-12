{{
  config(
    materialized='table',
    unique_key='token_address'
  )
}}
with token_first_seen as (
  select
    lower(token_address) as token_address,
    min(event_timestamp) as first_seen
  from (
    select token0_address as token_address, event_timestamp from {{ ref('stg_raw_swaps') }}
    union all
    select token1_address, event_timestamp from {{ ref('stg_raw_swaps') }}
    union all
    select token_address, event_timestamp from {{ ref('stg_raw_transfers') }}
  ) t
  group by 1
),
seed as (
  select
    lower(token_address) as token_address,
    symbol,
    name,
    decimals,
    coingecko_id
  from {{ ref('known_tokens') }}
)
select
  coalesce(s.token_address, f.token_address) as token_address,
  s.symbol,
  s.name,
  s.decimals,
  s.coingecko_id,
  f.first_seen
from seed s
left join token_first_seen f on s.token_address = f.token_address
