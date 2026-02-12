select block_number, tx_hash, event_timestamp
from {{ ref('stg_raw_swaps') }}
where event_timestamp > current_timestamp
