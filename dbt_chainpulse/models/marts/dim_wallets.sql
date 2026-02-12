{{
  config(
    materialized='table',
    unique_key='wallet_address'
  )
}}
select
  wallet_address,
  first_seen,
  last_seen,
  total_swaps,
  total_volume as total_volume_usd,
  'retail' as segment,
  null::numeric as rfm_score,
  null::varchar as label
from {{ ref('int_wallet_activity') }}
