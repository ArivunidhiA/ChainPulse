-- Raw event tables

CREATE TABLE IF NOT EXISTS raw_events (
    id              BIGSERIAL PRIMARY KEY,
    block_number    BIGINT NOT NULL,
    tx_hash         TEXT NOT NULL,
    log_index       INTEGER NOT NULL,
    contract_address TEXT NOT NULL,
    event_name      TEXT NOT NULL,
    event_params    JSONB NOT NULL,
    event_timestamp TIMESTAMPTZ NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (tx_hash, log_index)
);

CREATE TABLE IF NOT EXISTS raw_swaps (
    id               BIGSERIAL PRIMARY KEY,
    block_number     BIGINT NOT NULL,
    tx_hash          TEXT NOT NULL,
    log_index        INTEGER NOT NULL,
    pool_address     TEXT NOT NULL,
    sender_address   TEXT NOT NULL,
    recipient_address TEXT NOT NULL,
    token0_address   TEXT NOT NULL,
    token1_address   TEXT NOT NULL,
    amount0          NUMERIC NOT NULL,
    amount1          NUMERIC NOT NULL,
    sqrt_price_x96   NUMERIC,
    liquidity        NUMERIC,
    tick             INTEGER,
    usd_value        NUMERIC,
    event_timestamp  TIMESTAMPTZ NOT NULL,
    size_bucket      TEXT,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (tx_hash, log_index)
);

CREATE TABLE IF NOT EXISTS raw_transfers (
    id               BIGSERIAL PRIMARY KEY,
    block_number     BIGINT NOT NULL,
    tx_hash          TEXT NOT NULL,
    log_index        INTEGER NOT NULL,
    token_address    TEXT NOT NULL,
    from_address     TEXT NOT NULL,
    to_address       TEXT NOT NULL,
    amount_raw       NUMERIC NOT NULL,
    amount           NUMERIC,
    usd_value        NUMERIC,
    direction        TEXT,
    is_exchange      BOOLEAN DEFAULT FALSE,
    event_timestamp  TIMESTAMPTZ NOT NULL,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (tx_hash, log_index)
);

-- Token prices cache

CREATE TABLE IF NOT EXISTS token_prices (
    token_address   TEXT PRIMARY KEY,
    coingecko_id    TEXT NOT NULL,
    price_usd       NUMERIC NOT NULL,
    fetched_at      TIMESTAMPTZ NOT NULL,
    source          TEXT DEFAULT 'coingecko'
);

-- Block processing checkpoints

CREATE TABLE IF NOT EXISTS block_checkpoints (
    id              BIGSERIAL PRIMARY KEY,
    contract_address TEXT NOT NULL,
    last_block      BIGINT NOT NULL,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (contract_address)
);

-- Analytics output tables (written by Python analysis scripts)

CREATE TABLE IF NOT EXISTS analytics_wallet_segments (
    wallet_address  TEXT PRIMARY KEY,
    segment         TEXT NOT NULL,
    cluster_id      INTEGER NOT NULL,
    rfm_recency     NUMERIC NOT NULL,
    rfm_frequency   INTEGER NOT NULL,
    rfm_volume      NUMERIC NOT NULL,
    computed_at     TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS analytics_anomalies (
    anomaly_id      UUID PRIMARY KEY,
    hour_bucket     TIMESTAMPTZ NOT NULL,
    token_address   TEXT NOT NULL,
    actual_volume   NUMERIC NOT NULL,
    expected_volume NUMERIC NOT NULL,
    z_score         NUMERIC NOT NULL,
    severity        TEXT NOT NULL,
    detected_at     TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS analytics_token_flows (
    id              BIGSERIAL PRIMARY KEY,
    hour_bucket     TIMESTAMPTZ NOT NULL,
    token_address   TEXT NOT NULL,
    inflow_usd      NUMERIC NOT NULL,
    outflow_usd     NUMERIC NOT NULL,
    net_flow_usd    NUMERIC NOT NULL,
    unique_senders  INTEGER NOT NULL,
    unique_receivers INTEGER NOT NULL,
    flow_direction  TEXT NOT NULL,
    UNIQUE (hour_bucket, token_address)
);

CREATE TABLE IF NOT EXISTS analytics_protocol_health (
    date_bucket           DATE PRIMARY KEY,
    unique_active_wallets INTEGER NOT NULL,
    total_swaps           INTEGER NOT NULL,
    total_volume_usd      NUMERIC NOT NULL,
    median_swap_size      NUMERIC NOT NULL,
    gini_coefficient      NUMERIC NOT NULL,
    whale_share_pct       NUMERIC NOT NULL,
    health_score          NUMERIC NOT NULL
);

