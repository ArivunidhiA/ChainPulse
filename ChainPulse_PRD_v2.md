# PRODUCT REQUIREMENTS DOCUMENT — ChainPulse: On-Chain DeFi Analytics Pipeline

---

## 1. PRODUCT OVERVIEW

### Name
**ChainPulse** — Production-Grade On-Chain Analytics Pipeline for DeFi Protocol Monitoring

### One-Liner
End-to-end blockchain data platform that extracts, transforms, and analyzes EVM smart contract events through a modern data stack (dbt, Airflow, PostgreSQL), delivering real-time DeFi insights through statistical analysis and self-serve dashboards.

### Why This Project
| Serotonin JD Requirement | How ChainPulse Delivers |
|---|---|
| Blockchain data extraction, transformation, analysis | Indexes Uniswap/ERC-20 events, decodes ABIs, classifies transaction types |
| Modern data stack (dbt, Airflow, Snowflake) | dbt models with staging → marts → analytics layers, scheduled via APScheduler |
| Data modeling (Kimball, Data Vault) | Star schema: fact_swaps, fact_transfers, dim_tokens, dim_wallets |
| Statistical analysis + data science | Z-score anomaly detection, whale segmentation, volume distribution analysis, token flow metrics |
| Self-serve analytics + dashboards | Curated analytical tables + interactive Streamlit/Next.js dashboard |
| ETL pipelines + database architecture | Python extraction → PostgreSQL staging → dbt transformation → analytics tables |
| A/B testing + experimental design | Before/after analysis on protocol events (fee changes, liquidity shifts) |
| Cloud data platforms (AWS) | Neon PostgreSQL, Vercel deployment, S3-compatible storage |
| Full lifecycle data products | Extraction → modeling → analysis → dashboard → production deployment |

---

## 2. OBJECTIVE

Deliver a **production-ready on-chain analytics platform** usable on the public internet within **48 hours**, demonstrating:

- **Data engineering depth** — multi-source EVM extraction, dbt modeling, orchestrated pipelines
- **Analytical rigor** — statistical methods on blockchain data producing actionable insights
- **Production credibility** — deployed, monitored, documented, not a toy project
- **Modern data stack fluency** — dbt, PostgreSQL, Python, scheduled transformations

---

## 3. TARGET USERS

| Persona | Needs |
|---|---|
| Web3 Protocol Team | Protocol health metrics, user retention, liquidity trends |
| DeFi Analyst | Whale tracking, volume anomalies, token flow patterns |
| Data Team Lead (Hiring Manager) | Clean dbt project, statistical rigor, production deployment |

---

## 4. CONSTRAINTS

| Constraint | Solution |
|---|---|
| Python backend | FastAPI (lightweight, serves analytical results) |
| Neon PostgreSQL | Primary warehouse — stores raw, transformed, and analytical tables |
| Vercel deployment | Frontend dashboard on Vercel |
| Free-tier stability | Render (backend), Alchemy free (RPC), CoinGecko free (prices) |
| 48-hour timeline | Phased delivery prioritizing data work over UI |

---

## 5. ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                   EXTRACTION LAYER (18 hrs)                      │
│                                                                  │
│  EVM Indexer (Python, web3.py)                                   │
│  ├── Uniswap V3 Swap event decoder                              │
│  ├── ERC-20 Transfer event decoder (USDC, USDT, WBTC, DAI)     │
│  ├── Multi-contract ABI registry                                 │
│  ├── Block range processor with checkpoint recovery              │
│  ├── Event classification engine (swap/transfer/mint/burn)       │
│  ├── Price enrichment service (CoinGecko)                        │
│  └── Rate-limited RPC manager (Alchemy free tier)                │
│                                                                  │
│  Output: raw_events, raw_swaps, raw_transfers → Neon           │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                 TRANSFORMATION LAYER (14 hrs)                    │
│                                                                  │
│  dbt Project (dbt-postgres → Neon)                              │
│  ├── staging/                                                    │
│  │   ├── stg_raw_events.sql        (cleaned, typed, deduped)    │
│  │   ├── stg_raw_swaps.sql         (decoded swap params)        │
│  │   └── stg_raw_transfers.sql     (decoded transfer params)    │
│  ├── intermediate/                                               │
│  │   ├── int_swaps_enriched.sql    (USD values, token joins)    │
│  │   ├── int_transfers_enriched.sql(USD values, direction)      │
│  │   └── int_wallet_activity.sql   (per-wallet aggregation)     │
│  ├── marts/                                                      │
│  │   ├── fact_swaps.sql            (production swap facts)       │
│  │   ├── fact_transfers.sql        (production transfer facts)   │
│  │   ├── dim_tokens.sql            (token dimension - SCD1)     │
│  │   └── dim_wallets.sql           (wallet dimension - SCD1)    │
│  └── analytics/                                                  │
│      ├── agg_hourly_volume.sql     (incremental hourly agg)     │
│      ├── agg_daily_protocol.sql    (daily protocol metrics)     │
│      ├── wallet_segments.sql       (whale/retail/bot segments)  │
│      ├── token_flow_summary.sql    (net inflow/outflow/token)   │
│      └── anomaly_flagged.sql       (z-score flagged events)     │
│                                                                  │
│  dbt Tests: unique, not_null, relationships, accepted_values     │
│  dbt Docs: auto-generated lineage + documentation                │
│  Scheduling: APScheduler runs `dbt run` every 30 min             │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                  ANALYSIS LAYER (6 hrs)                           │
│                                                                  │
│  Python Analysis Scripts (write results → Neon)                  │
│  ├── whale_segmentation.py                                       │
│  │   ├── K-means clustering on wallet behavior                   │
│  │   ├── RFM-style scoring (recency, frequency, volume)         │
│  │   └── Output: analytics_wallet_segments table                 │
│  ├── volume_anomaly.py                                           │
│  │   ├── Z-score on rolling 7-day hourly volume                  │
│  │   ├── Volume distribution analysis (skew, kurtosis)           │
│  │   ├── Spike detection with configurable thresholds            │
│  │   └── Output: analytics_anomalies table                       │
│  ├── token_flow_analysis.py                                      │
│  │   ├── Net flow per token per hour (inflow - outflow)          │
│  │   ├── Accumulation/distribution patterns                      │
│  │   ├── Cross-token correlation matrix                          │
│  │   └── Output: analytics_token_flows table                     │
│  └── protocol_health.py                                          │
│      ├── Unique active wallets trend                              │
│      ├── Swap frequency distribution                              │
│      ├── Liquidity concentration (Gini coefficient)               │
│      └── Output: analytics_protocol_health table                  │
│                                                                  │
│  Scheduling: APScheduler runs analysis scripts every hour         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                    API LAYER (4 hrs)                              │
│                                                                  │
│  FastAPI (lightweight, serves pre-computed analytics)             │
│  ├── GET /api/swaps          — filtered swap data                │
│  ├── GET /api/whales         — whale wallet segments             │
│  ├── GET /api/volume         — hourly/daily volume time series   │
│  ├── GET /api/anomalies      — flagged anomalous events          │
│  ├── GET /api/token-flows    — net flow per token                │
│  ├── GET /api/protocol-health— protocol KPIs                     │
│  ├── GET /api/stats          — summary metrics                   │
│  └── GET /api/health         — liveness check                    │
│                                                                  │
│  All endpoints serve pre-computed results from analytics tables   │
│  Response time: <100ms (reads from indexed PostgreSQL)            │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                  DASHBOARD LAYER (4 hrs)                          │
│                                                                  │
│  Next.js on Vercel (simple, reads from API)                      │
│  ├── Protocol Health Cards (volume, wallets, swaps, anomalies)   │
│  ├── Volume Trend Chart (Recharts, token filter)                 │
│  ├── Whale Activity Table (segment, volume, last active)         │
│  ├── Anomaly Feed (flagged transactions, z-scores)               │
│  ├── Token Flow Heatmap (inflow/outflow by token)                │
│  └── CSV Export on all views                                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. DATA MODEL (Kimball Star Schema)

### Fact Tables

**fact_swaps**
| Column | Type | Description |
|---|---|---|
| swap_id | UUID (PK) | Unique identifier |
| block_number | INTEGER | Block number |
| tx_hash | VARCHAR | Transaction hash |
| wallet_address | VARCHAR (FK → dim_wallets) | Swapper address |
| token_in_address | VARCHAR (FK → dim_tokens) | Token sold |
| token_out_address | VARCHAR (FK → dim_tokens) | Token bought |
| amount_in | NUMERIC | Raw amount sold |
| amount_out | NUMERIC | Raw amount bought |
| amount_usd | NUMERIC | USD value at time of swap |
| pool_address | VARCHAR | Uniswap pool contract |
| gas_used | INTEGER | Gas consumed |
| gas_price_gwei | NUMERIC | Gas price |
| event_timestamp | TIMESTAMP | Block timestamp |
| is_whale | BOOLEAN | >$50K flag |
| anomaly_score | NUMERIC | Z-score |
| wallet_segment | VARCHAR | whale/retail/bot |

**fact_transfers**
| Column | Type | Description |
|---|---|---|
| transfer_id | UUID (PK) | Unique identifier |
| block_number | INTEGER | Block number |
| tx_hash | VARCHAR | Transaction hash |
| from_address | VARCHAR (FK → dim_wallets) | Sender |
| to_address | VARCHAR (FK → dim_wallets) | Receiver |
| token_address | VARCHAR (FK → dim_tokens) | Token contract |
| amount | NUMERIC | Transfer amount |
| amount_usd | NUMERIC | USD value |
| direction | VARCHAR | 'in' or 'out' relative to tracked wallets |
| event_timestamp | TIMESTAMP | Block timestamp |

### Dimension Tables

**dim_tokens**
| Column | Type | Description |
|---|---|---|
| token_address | VARCHAR (PK) | Contract address |
| symbol | VARCHAR | ETH, USDC, etc. |
| name | VARCHAR | Full name |
| decimals | INTEGER | Token decimals |
| coingecko_id | VARCHAR | Price lookup key |
| first_seen | TIMESTAMP | First indexed event |

**dim_wallets**
| Column | Type | Description |
|---|---|---|
| wallet_address | VARCHAR (PK) | Address |
| first_seen | TIMESTAMP | First transaction |
| last_seen | TIMESTAMP | Most recent activity |
| total_swaps | INTEGER | Lifetime swaps |
| total_volume_usd | NUMERIC | Lifetime volume |
| segment | VARCHAR | whale / retail / bot |
| rfm_score | NUMERIC | Recency-frequency-volume score |
| label | VARCHAR | Known entity label |

### Analytics Tables (Output of Analysis Scripts)

**analytics_wallet_segments**
| Column | Type | Description |
|---|---|---|
| wallet_address | VARCHAR (PK) | Address |
| segment | VARCHAR | whale / retail / bot |
| cluster_id | INTEGER | K-means cluster |
| rfm_recency | NUMERIC | Days since last swap |
| rfm_frequency | INTEGER | Swaps in last 30d |
| rfm_volume | NUMERIC | Volume in last 30d |
| computed_at | TIMESTAMP | Last computation time |

**analytics_anomalies**
| Column | Type | Description |
|---|---|---|
| anomaly_id | UUID (PK) | Unique identifier |
| hour_bucket | TIMESTAMP | Hour of anomaly |
| token_address | VARCHAR | Affected token |
| actual_volume | NUMERIC | Observed volume |
| expected_volume | NUMERIC | Rolling mean |
| z_score | NUMERIC | Standard deviations from mean |
| severity | VARCHAR | low / medium / high / critical |
| detected_at | TIMESTAMP | Detection time |

**analytics_token_flows**
| Column | Type | Description |
|---|---|---|
| hour_bucket | TIMESTAMP | Hour |
| token_address | VARCHAR | Token |
| inflow_usd | NUMERIC | Total incoming |
| outflow_usd | NUMERIC | Total outgoing |
| net_flow_usd | NUMERIC | inflow - outflow |
| unique_senders | INTEGER | Distinct senders |
| unique_receivers | INTEGER | Distinct receivers |
| flow_direction | VARCHAR | accumulation / distribution / neutral |

**analytics_protocol_health**
| Column | Type | Description |
|---|---|---|
| date_bucket | DATE | Day |
| unique_active_wallets | INTEGER | DAU equivalent |
| total_swaps | INTEGER | Daily swap count |
| total_volume_usd | NUMERIC | Daily volume |
| median_swap_size | NUMERIC | Median transaction |
| gini_coefficient | NUMERIC | Liquidity concentration |
| whale_share_pct | NUMERIC | % volume from whales |
| health_score | NUMERIC | Composite 0-100 score |

---

## 7. SMART CONTRACT EVENTS

### Uniswap V3: Swap Event
```solidity
event Swap(
    address indexed sender,
    address indexed recipient,
    int256 amount0,
    int256 amount1,
    uint160 sqrtPriceX96,
    int128 liquidity,
    int24 tick
)
```
**Extraction logic:**
- Decode amount0/amount1 using token decimals from dim_tokens
- Determine swap direction (token0→token1 or reverse)
- Enrich with USD price from CoinGecko cache
- Classify: whale (>$50K), large ($10K-$50K), standard (<$10K)

### ERC-20: Transfer Event
```solidity
event Transfer(
    address indexed from,
    address indexed to,
    uint256 value
)
```
**Extraction logic:**
- Filter contracts: USDC, USDT, WBTC, DAI, WETH
- Apply minimum threshold ($1K) to reduce noise
- Tag direction relative to tracked wallets
- Flag exchange-associated addresses

### Multi-Contract ABI Registry
```python
ABI_REGISTRY = {
    "uniswap_v3_pool": {"events": ["Swap"], "decoder": UniswapDecoder},
    "erc20": {"events": ["Transfer"], "decoder": ERC20Decoder},
}
# Extensible — add Aave, Curve, etc. by registering new decoders
```

---

## 8. ANALYSIS METHODS (Python Scripts)

### whale_segmentation.py
```python
# RFM-style scoring adapted for DeFi wallets
# Recency: days since last swap (lower = better)
# Frequency: number of swaps in 30d window
# Volume: total USD volume in 30d window

# K-means clustering (k=4): whale, active_trader, retail, bot
# Bot detection: >50 swaps/day AND avg_size < $100
# Whale: top 1% by volume OR any single swap > $50K

# Output → analytics_wallet_segments table
```

### volume_anomaly.py
```python
# Rolling 7-day (168hr) mean and std on hourly volume
# Z-score = (current_hour - rolling_mean) / rolling_std
# Severity classification:
#   |z| > 3.0 → critical
#   |z| > 2.5 → high
#   |z| > 2.0 → medium
#   |z| > 1.5 → low

# Volume distribution stats: skewness, kurtosis per token
# Spike detection: consecutive anomalous hours = sustained event

# Output → analytics_anomalies table
```

### token_flow_analysis.py
```python
# Per token per hour:
#   inflow = SUM(amount_usd) WHERE direction = 'in'
#   outflow = SUM(amount_usd) WHERE direction = 'out'
#   net_flow = inflow - outflow
#
# Classification:
#   net_flow > 0 → accumulation (buying pressure)
#   net_flow < 0 → distribution (selling pressure)
#   abs(net_flow) < threshold → neutral
#
# Cross-token correlation matrix (Pearson) on hourly net flows
# Identifies: tokens moving together, divergence signals

# Output → analytics_token_flows table
```

### protocol_health.py
```python
# Daily protocol KPIs:
#   - DAU (unique active wallets)
#   - Transaction count + volume
#   - Median swap size (retail health indicator)
#   - Gini coefficient on wallet volume (concentration risk)
#   - Whale share: % of volume from whale segment
#   - Composite health score (weighted average, 0-100)
#
# Trend analysis: 7d moving average on all metrics
# Alert: health_score drops >15 points in 24hrs

# Output → analytics_protocol_health table
```

---

## 9. dbt MODEL DETAILS

### Staging Layer
```sql
-- stg_raw_events.sql
-- Cleans raw extracted events: casts types, deduplicates on tx_hash + log_index,
-- filters invalid records, standardizes timestamps to UTC

-- stg_raw_swaps.sql
-- Decodes Uniswap swap params, joins token decimals, calculates human-readable amounts
-- Adds swap_direction, token_in, token_out classification

-- stg_raw_transfers.sql
-- Decodes ERC-20 transfer params, applies decimal conversion,
-- Tags known exchange addresses, filters dust transactions
```

### Intermediate Layer
```sql
-- int_swaps_enriched.sql
-- Joins stg_raw_swaps with dim_tokens for USD enrichment
-- Calculates amount_usd using cached CoinGecko prices
-- Adds time dimensions: hour_bucket, day_bucket, week_bucket

-- int_transfers_enriched.sql
-- Joins with dim_tokens, enriches USD value
-- Determines direction (in/out) relative to wallet universe
-- Tags transfer type: standard, whale, exchange_deposit, exchange_withdrawal

-- int_wallet_activity.sql
-- Aggregates per wallet: total_swaps, total_volume, first_seen, last_seen
-- Calculates activity metrics: avg_swap_size, swap_frequency, active_days
```

### Marts Layer
```sql
-- fact_swaps.sql (incremental)
-- Production-ready swap facts with all enrichments
-- Partitioned by event_timestamp, indexed on wallet_address, token pairs

-- fact_transfers.sql (incremental)
-- Production transfer facts with USD values and direction tags

-- dim_tokens.sql (SCD Type 1)
-- Token reference with metadata, auto-updates on new tokens

-- dim_wallets.sql (SCD Type 1)
-- Wallet dimension with running aggregates, segment assignment
```

### Analytics Layer
```sql
-- agg_hourly_volume.sql (incremental)
-- Hourly aggregation: swap_count, volume, unique_wallets, avg/max size per token

-- agg_daily_protocol.sql (incremental)
-- Daily protocol-level metrics for health scoring

-- wallet_segments.sql
-- Reads from analytics_wallet_segments (Python output), exposes as dbt model
-- Enables downstream joins in SQL

-- token_flow_summary.sql
-- Reads analytics_token_flows, adds 7d moving averages

-- anomaly_flagged.sql
-- Joins analytics_anomalies with fact_swaps for flagged transaction details
```

### dbt Tests
```yaml
# schema.yml
models:
  - name: fact_swaps
    columns:
      - name: swap_id
        tests: [unique, not_null]
      - name: wallet_address
        tests: [not_null, relationships: {to: ref('dim_wallets'), field: wallet_address}]
      - name: amount_usd
        tests: [not_null]
  - name: dim_wallets
    columns:
      - name: wallet_address
        tests: [unique, not_null]
      - name: segment
        tests: [accepted_values: {values: ['whale', 'active_trader', 'retail', 'bot']}]
```

---

## 10. API ENDPOINTS (Lightweight — Serves Pre-Computed Data)

| Method | Endpoint | Source Table | Description |
|---|---|---|---|
| GET | /api/swaps | fact_swaps | Recent swaps, filter by token/wallet/size |
| GET | /api/whales | analytics_wallet_segments | Whale wallets with RFM scores |
| GET | /api/volume | agg_hourly_volume | Time series for charting |
| GET | /api/anomalies | analytics_anomalies | Flagged volume spikes |
| GET | /api/token-flows | analytics_token_flows | Net flow per token |
| GET | /api/protocol-health | analytics_protocol_health | Daily health KPIs |
| GET | /api/stats | Multiple | Summary dashboard metrics |
| GET | /api/health | — | Liveness + DB connectivity |
| GET | /api/data-freshness | raw_events | Seconds since last indexed event |

All endpoints return JSON, support pagination (limit/offset), and respond in <100ms from indexed PostgreSQL.

---

## 11. DASHBOARD (Next.js on Vercel)

| Component | Data Source | Interaction |
|---|---|---|
| Protocol Health Cards | /api/stats | Auto-refresh 60s |
| Volume Trend Chart | /api/volume | Token filter, time range (1h/6h/24h/7d) |
| Whale Activity Table | /api/whales | Sort by volume/recency, wallet search |
| Anomaly Feed | /api/anomalies | Severity filter, token filter |
| Token Flow Heatmap | /api/token-flows | Hourly net flow, accumulation/distribution |
| Data Freshness Indicator | /api/data-freshness | Shows pipeline lag |
| CSV Export | All endpoints | Download filtered data |

Design: Dark theme, minimal, data-dense. No unnecessary animations. Professional analytics tool aesthetic.

---

## 12. 48-HOUR BUILD TIMELINE

| Hours | Phase | Deliverables | Priority |
|---|---|---|---|
| 0-3 | Setup | Repo, Neon schema DDL, dbt project init, FastAPI scaffold | P0 |
| 3-8 | Extraction: Core | web3.py indexer for Uniswap Swap events, raw_events table writes, block checkpoint | P0 |
| 8-12 | Extraction: Multi | ERC-20 Transfer indexer, multi-contract ABI registry, event classification | P0 |
| 12-15 | Extraction: Enrichment | CoinGecko price service, USD value calculation, rate limiting, error handling | P0 |
| 15-18 | Extraction: Hardening | Retry logic, backfill capability, data validation, logging | P1 |
| 18-22 | dbt: Staging + Intermediate | stg models (clean/type/dedup), int models (enrich/join/classify) | P0 |
| 22-26 | dbt: Marts + Analytics | fact tables, dim tables, aggregation models, incremental config | P0 |
| 26-28 | dbt: Tests + Docs | Schema tests, source freshness, generated documentation | P0 |
| 28-30 | dbt: Scheduling | APScheduler running `dbt run` every 30min, `dbt test` on completion | P1 |
| 30-33 | Analysis Scripts | whale_segmentation.py, volume_anomaly.py (Z-score, severity) | P0 |
| 33-36 | Analysis Scripts | token_flow_analysis.py, protocol_health.py (Gini, health score) | P0 |
| 36-40 | API | FastAPI endpoints serving all analytics tables, pagination, filters | P0 |
| 40-44 | Dashboard | Next.js: health cards, volume chart, whale table, anomaly feed, token flows | P0 |
| 44-46 | Dashboard Polish | Filters, CSV export, data freshness indicator, responsive layout | P1 |
| 46-48 | Deploy + Docs | Vercel + Render deployment, README (architecture diagram, screenshots), Docker compose | P0 |

---

## 13. FREE-TIER INFRASTRUCTURE

| Service | Tier | Limits | Usage |
|---|---|---|---|
| Neon | Free | 512MB DB, serverless | PostgreSQL warehouse |
| Vercel | Hobby | 100GB bandwidth | Next.js dashboard |
| Render | Free | 750 hrs/month | FastAPI + indexer |
| Alchemy | Free | 300M CU/month | Ethereum RPC |
| CoinGecko | Free | 30 calls/min | Token prices |
| GitHub Actions | Free | 2000 min/month | Scheduled dbt runs (backup) |

### Staying Within Limits
- Poll every 15s (not WebSocket to RPC) — conserves Alchemy compute units
- Batch inserts (50 events/insert) — reduces Neon API calls
- Incremental dbt models — only processes new data
- Cache prices 5 min — reduces CoinGecko calls
- Render keep-alive ping every 14 min — prevents cold starts
- 30-day data retention — cleanup job prevents hitting 500MB

---

## 14. FILE STRUCTURE

```
chainpulse/
├── backend/
│   ├── main.py                         # FastAPI server + APScheduler
│   ├── indexer/
│   │   ├── evm_indexer.py              # Core event extraction (web3.py)
│   │   ├── decoder.py                  # ABI event decoder + registry
│   │   ├── event_classifier.py         # Swap/transfer/mint/burn classification
│   │   ├── price_service.py            # CoinGecko price fetcher + cache
│   │   └── block_tracker.py            # Checkpoint persistence
│   ├── analysis/
│   │   ├── whale_segmentation.py       # K-means + RFM scoring
│   │   ├── volume_anomaly.py           # Z-score anomaly detection
│   │   ├── token_flow_analysis.py      # Net flow + correlation
│   │   └── protocol_health.py          # Gini, DAU, health score
│   ├── api/
│   │   └── routes.py                   # All API endpoints
│   ├── db/
│   │   ├── schema.sql                  # Raw table DDL
│   │   ├── connection.py               # Neon connection pool
│   │   └── queries.py                  # Parameterized SQL queries
│   ├── scheduler/
│   │   └── jobs.py                     # APScheduler: dbt runs + analysis
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── dbt_chainpulse/
│   ├── dbt_project.yml
│   ├── profiles.yml
│   ├── packages.yml                    # dbt-utils, dbt-expectations
│   ├── models/
│   │   ├── staging/
│   │   │   ├── _stg_sources.yml        # Source definitions + freshness
│   │   │   ├── stg_raw_events.sql
│   │   │   ├── stg_raw_swaps.sql
│   │   │   └── stg_raw_transfers.sql
│   │   ├── intermediate/
│   │   │   ├── int_swaps_enriched.sql
│   │   │   ├── int_transfers_enriched.sql
│   │   │   └── int_wallet_activity.sql
│   │   ├── marts/
│   │   │   ├── _marts_schema.yml       # Tests + documentation
│   │   │   ├── fact_swaps.sql
│   │   │   ├── fact_transfers.sql
│   │   │   ├── dim_tokens.sql
│   │   │   └── dim_wallets.sql
│   │   └── analytics/
│   │       ├── _analytics_schema.yml
│   │       ├── agg_hourly_volume.sql
│   │       ├── agg_daily_protocol.sql
│   │       ├── wallet_segments.sql
│   │       ├── token_flow_summary.sql
│   │       └── anomaly_flagged.sql
│   ├── tests/
│   │   └── custom/
│   │       ├── test_no_future_timestamps.sql
│   │       └── test_positive_amounts.sql
│   ├── macros/
│   │   └── usd_conversion.sql          # Reusable price conversion macro
│   └── seeds/
│       └── known_tokens.csv            # Token metadata seed
├── frontend/
│   ├── pages/
│   │   └── index.tsx
│   ├── components/
│   │   ├── ProtocolHealthCards.tsx
│   │   ├── VolumeChart.tsx
│   │   ├── WhaleTracker.tsx
│   │   ├── AnomalyFeed.tsx
│   │   └── TokenFlowHeatmap.tsx
│   ├── lib/
│   │   └── api.ts                      # API client
│   ├── package.json
│   └── next.config.js
├── docker-compose.yml                   # Local dev: PostgreSQL + backend
├── .github/
│   └── workflows/
│       └── dbt_scheduled.yml            # Backup: GitHub Actions dbt run
└── README.md
```

---

## 15. SUCCESS METRICS

| Metric | Target |
|---|---|
| Blockchain events indexed/day | 10K+ |
| Data freshness (on-chain → analytics table) | <5 min |
| API response time (p95) | <100ms |
| Dashboard load time | <2s |
| dbt test pass rate | 100% |
| Analysis script runtime | <60s per run |
| Anomaly detection precision | >80% (manual spot check) |
| Uptime | 99.9% (excluding Render cold starts) |

---

## 16. RISKS & MITIGATIONS

| Risk | Impact | Mitigation |
|---|---|---|
| Alchemy rate limit hit | Indexer pauses | Exponential backoff + fallback public RPC |
| Neon storage limit | Writes fail | 30-day retention cleanup, monitor usage |
| Render cold start (30s) | Slow first request | Keep-alive ping + frontend loading state |
| CoinGecko rate limit | Missing USD prices | 5-min price cache, fallback to last known |
| dbt model failure | Stale analytics | Alert on failure, auto-retry, last-good fallback |
| Low swap volume periods | Empty dashboards | Seed with 24hr backfill on deploy |

---

## 17. RESUME BULLETS (What This Becomes)

```latex
\textbf{ChainPulse — On-Chain DeFi Analytics Pipeline} \hfill GitHub | Live Demo
\begin{itemize}
    \item Built on-chain pipeline (Python, web3.py, dbt) indexing Uniswap swap events
      and ERC-20 transfers into Kimball star schema on PostgreSQL
    \item Implemented whale detection and Z-score anomaly analysis, serving real-time
      insights via FastAPI dashboard
\end{itemize}
```

---

## 18. WHY THIS ISN'T A STUDENT PROJECT

| Student Project | ChainPulse |
|---|---|
| Reads from CSV/API dump | Extracts directly from Ethereum blockchain via RPC |
| Single script, no structure | dbt project with staging → marts → analytics layers |
| No data modeling | Kimball star schema with fact/dim tables |
| Basic pandas analysis | Statistical methods: Z-score, K-means, Gini coefficient, RFM |
| Runs locally | Production deployed on Vercel + Render + Neon |
| No tests | dbt tests, data freshness checks, custom validations |
| No scheduling | APScheduler + GitHub Actions backup |
| README only | Generated dbt docs with full lineage graph |
