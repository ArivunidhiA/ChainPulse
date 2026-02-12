{{
  config(
    materialized='view'
  )
}}
with swap_activity as (
  select
    sender_address as wallet_address,
    count(*) as total_swaps,
    sum(coalesce(usd_value, 0)) as total_volume,
    min(event_timestamp) as first_seen,
    max(event_timestamp) as last_seen
  from {{ ref('stg_raw_swaps') }}
  group by 1
),
transfer_wallets as (
  select lower(from_address) as wallet_address from {{ ref('stg_raw_transfers') }}
  union
  select lower(to_address) from {{ ref('stg_raw_transfers') }}
),
all_wallets as (
  select wallet_address from swap_activity
  union
  select wallet_address from transfer_wallets
),
first_last as (
  select
    a.wallet_address,
    min(e.event_timestamp) as first_seen,
    max(e.event_timestamp) as last_seen
  from all_wallets a
  left join (
    select sender_address as wallet_address, event_timestamp from {{ ref('stg_raw_swaps') }}
    union all
    select from_address, event_timestamp from {{ ref('stg_raw_transfers') }}
    union all
    select to_address, event_timestamp from {{ ref('stg_raw_transfers') }}
  ) e on a.wallet_address = e.wallet_address
  group by 1
)
select
  a.wallet_address,
  coalesce(s.total_swaps, 0) as total_swaps,
  coalesce(s.total_volume, 0) as total_volume,
  coalesce(f.first_seen, s.first_seen) as first_seen,
  coalesce(f.last_seen, s.last_seen) as last_seen,
  case when coalesce(s.total_swaps, 0) > 0 then coalesce(s.total_volume, 0) / s.total_swaps else 0 end as avg_swap_size
from all_wallets a
left join swap_activity s on a.wallet_address = s.wallet_address
left join first_last f on a.wallet_address = f.wallet_address
