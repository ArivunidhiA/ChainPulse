-- ChainPulse Demo Data Seed
-- Compact version for fast remote DB insertion

-- Clean existing demo data
TRUNCATE raw_events, raw_swaps, raw_transfers, token_prices, block_checkpoints,
         analytics_wallet_segments, analytics_anomalies, analytics_token_flows, analytics_protocol_health
         CASCADE;

-- Token prices
INSERT INTO token_prices (token_address, coingecko_id, price_usd, fetched_at, source) VALUES
('0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48', 'usd-coin', 1.00, NOW(), 'coingecko'),
('0xdac17f958d2ee523a2206206994597c13d831ec7', 'tether', 1.00, NOW(), 'coingecko'),
('0x2260fac5e5542a773aa44fbcfedf7c193bc2c599', 'wrapped-bitcoin', 97450, NOW(), 'coingecko'),
('0x6b175474e89094c44da98b954eedeac495271d0f', 'dai', 1.00, NOW(), 'coingecko'),
('0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2', 'weth', 3285, NOW(), 'coingecko')
ON CONFLICT (token_address) DO UPDATE SET price_usd = EXCLUDED.price_usd, fetched_at = EXCLUDED.fetched_at;

-- Generate raw_swaps (using generate_series for speed)
INSERT INTO raw_swaps (block_number, tx_hash, log_index, pool_address, sender_address, recipient_address,
    token0_address, token1_address, amount0, amount1, usd_value, event_timestamp, size_bucket)
SELECT
    24440000 + (s * 5),
    '0x' || md5(random()::text || s::text),
    s,
    '0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8',
    '0x' || md5('wallet' || (s % 120)::text),
    '0x' || md5('recip' || (s % 80)::text),
    '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',
    '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2',
    ROUND((random() * 50000 + 500)::numeric, 2),
    ROUND(((random() * 50000 + 500) / 3285)::numeric, 6),
    ROUND((random() * 50000 + 500)::numeric, 2),
    NOW() - ((1680 - s) || ' minutes')::interval,
    CASE
        WHEN random() < 0.05 THEN 'whale'
        WHEN random() < 0.25 THEN 'large'
        ELSE 'standard'
    END
FROM generate_series(1, 1680) s;

-- Generate raw_events from swaps
INSERT INTO raw_events (block_number, tx_hash, log_index, contract_address, event_name, event_params, event_timestamp)
SELECT block_number, tx_hash, log_index,
    '0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8',
    'Swap',
    json_build_object('sender', sender_address, 'amount0', amount0::text, 'amount1', amount1::text)::jsonb,
    event_timestamp
FROM raw_swaps
ON CONFLICT (tx_hash, log_index) DO NOTHING;

-- Generate raw_transfers
INSERT INTO raw_transfers (block_number, tx_hash, log_index, token_address, from_address, to_address,
    amount_raw, amount, usd_value, direction, is_exchange, event_timestamp)
SELECT
    24440000 + (s * 3),
    '0x' || md5('xfer' || random()::text || s::text),
    100000 + s,
    CASE (s % 5)
        WHEN 0 THEN '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'
        WHEN 1 THEN '0xdac17f958d2ee523a2206206994597c13d831ec7'
        WHEN 2 THEN '0x2260fac5e5542a773aa44fbcfedf7c193bc2c599'
        WHEN 3 THEN '0x6b175474e89094c44da98b954eedeac495271d0f'
        ELSE '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'
    END,
    '0x' || md5('from' || (s % 100)::text),
    '0x' || md5('to' || (s % 100)::text),
    ROUND((random() * 1000000)::numeric, 0),
    ROUND((random() * 5000 + 100)::numeric, 4),
    ROUND((random() * 5000 + 100)::numeric, 2),
    CASE WHEN random() < 0.5 THEN 'inflow' ELSE 'outflow' END,
    random() < 0.1,
    NOW() - ((1000 - s) || ' minutes')::interval
FROM generate_series(1, 1000) s
ON CONFLICT (tx_hash, log_index) DO NOTHING;

-- Wallet segments (120 wallets)
INSERT INTO analytics_wallet_segments (wallet_address, segment, cluster_id, rfm_recency, rfm_frequency, rfm_volume, computed_at)
SELECT
    '0x' || md5('wallet' || s::text),
    CASE
        WHEN s <= 8 THEN 'whale'
        WHEN s <= 15 THEN 'bot'
        WHEN s <= 50 THEN 'active'
        WHEN s <= 90 THEN 'casual'
        ELSE 'dormant'
    END,
    CASE WHEN s <= 8 THEN 0 WHEN s <= 15 THEN 1 WHEN s <= 50 THEN 2 WHEN s <= 90 THEN 3 ELSE 4 END,
    ROUND((random() * 30)::numeric, 2),
    (random() * 200 + 1)::int,
    ROUND(CASE
        WHEN s <= 8 THEN (random() * 1500000 + 100000)
        WHEN s <= 15 THEN (random() * 40000 + 5000)
        ELSE (random() * 15000 + 100)
    END::numeric, 2),
    NOW()
FROM generate_series(1, 120) s
ON CONFLICT (wallet_address) DO UPDATE SET
    segment = EXCLUDED.segment, rfm_recency = EXCLUDED.rfm_recency,
    rfm_frequency = EXCLUDED.rfm_frequency, rfm_volume = EXCLUDED.rfm_volume;

-- Anomalies (30 anomalies)
INSERT INTO analytics_anomalies (anomaly_id, hour_bucket, token_address, actual_volume, expected_volume, z_score, severity, detected_at)
SELECT
    gen_random_uuid(),
    NOW() - ((s * 6) || ' hours')::interval,
    CASE (s % 3)
        WHEN 0 THEN '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'
        WHEN 1 THEN '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'
        ELSE '0x2260fac5e5542a773aa44fbcfedf7c193bc2c599'
    END,
    ROUND((random() * 400000 + 50000)::numeric, 2),
    ROUND((random() * 100000 + 20000)::numeric, 2),
    ROUND((random() * 5 + 1.5)::numeric, 2),
    CASE
        WHEN random() < 0.15 THEN 'critical'
        WHEN random() < 0.35 THEN 'high'
        WHEN random() < 0.65 THEN 'medium'
        ELSE 'low'
    END,
    NOW() - ((s * 6) || ' hours')::interval
FROM generate_series(1, 30) s;

-- Token flows (hourly, 168 hours × 3 tokens)
INSERT INTO analytics_token_flows (hour_bucket, token_address, inflow_usd, outflow_usd, net_flow_usd, unique_senders, unique_receivers, flow_direction)
SELECT
    NOW() - ((h) || ' hours')::interval,
    t.addr,
    ROUND((random() * 80000 + 10000)::numeric, 2) AS inflow,
    ROUND((random() * 80000 + 10000)::numeric, 2) AS outflow,
    ROUND((random() * 40000 - 20000)::numeric, 2) AS net,
    (random() * 30 + 5)::int,
    (random() * 30 + 5)::int,
    CASE WHEN random() < 0.5 THEN 'accumulation' ELSE 'distribution' END
FROM generate_series(1, 168) h
CROSS JOIN (VALUES
    ('0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'),
    ('0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'),
    ('0x2260fac5e5542a773aa44fbcfedf7c193bc2c599')
) t(addr)
ON CONFLICT (hour_bucket, token_address) DO NOTHING;

-- Protocol health (daily, 30 days)
INSERT INTO analytics_protocol_health (date_bucket, unique_active_wallets, total_swaps, total_volume_usd, median_swap_size, gini_coefficient, whale_share_pct, health_score)
SELECT
    (NOW() - ((d) || ' days')::interval)::date,
    (random() * 80 + 40)::int,
    (random() * 170 + 80)::int,
    ROUND((random() * 1500000 + 300000)::numeric, 2),
    ROUND((random() * 8000 + 1000)::numeric, 2),
    ROUND((random() * 0.35 + 0.35)::numeric, 4),
    ROUND((random() * 35 + 15)::numeric, 2),
    ROUND((random() * 30 + 50)::numeric, 2)
FROM generate_series(1, 30) d
ON CONFLICT (date_bucket) DO UPDATE SET
    unique_active_wallets = EXCLUDED.unique_active_wallets,
    total_swaps = EXCLUDED.total_swaps,
    total_volume_usd = EXCLUDED.total_volume_usd;

-- Checkpoint
INSERT INTO block_checkpoints (contract_address, last_block)
VALUES ('0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8', 24448400)
ON CONFLICT (contract_address) DO UPDATE SET last_block = EXCLUDED.last_block;
