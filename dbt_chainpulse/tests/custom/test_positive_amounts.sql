select tx_hash, log_index, amount_usd
from {{ ref('fact_swaps') }}
where amount_usd < 0
