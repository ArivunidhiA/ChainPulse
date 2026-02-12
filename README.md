<p align="center"><strong>ChainPulse</strong></p>
<p align="center">On-chain DeFi analytics pipeline — extract, transform, analyze, visualize.</p>
<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue" alt="version" />
  <img src="https://img.shields.io/badge/license-MIT-green" alt="license" />
  <img src="https://img.shields.io/badge/status-production--ready-brightgreen" alt="status" />
  <img src="https://img.shields.io/badge/Next.js-14-black" alt="Next.js" />
  <img src="https://img.shields.io/badge/Python-3.12-3776AB" alt="Python" />
  <img src="https://img.shields.io/badge/dbt-1.8-FF694B" alt="dbt" />
  <img src="https://img.shields.io/badge/Neon-PostgreSQL-00E5A0" alt="Neon" />
</p>

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [API Reference](#-api-reference)
- [Deployment](#-deployment)
- [Project Structure](#-project-structure)
- [License](#-license)

---

## 🔍 Overview

ChainPulse is a **production-grade data engineering portfolio project** that indexes Ethereum smart contract events (Uniswap V3 swaps, ERC-20 transfers), transforms them through a **Kimball star-schema** data warehouse using dbt, runs statistical analysis (K-means clustering, Z-score anomaly detection, Gini coefficients), and serves insights through a minimal, light-themed **Next.js dashboard**.

**Key highlights:**
- End-to-end pipeline: extraction → transformation → analysis → visualization
- Real Ethereum mainnet data via Alchemy RPC + CoinGecko price enrichment
- Kimball-modeled warehouse: fact tables, dimension tables, incremental models
- Four analysis modules producing actionable intelligence
- Clean, production-ready UI with expandable cards and hover interactions

---

## ✨ Features

| Category | Details |
|---|---|
| **Data Extraction** | Uniswap V3 Swap events, ERC-20 Transfer events, block checkpointing, CoinGecko USD enrichment |
| **Data Modeling** | dbt staging → intermediate → marts → analytics, surrogate keys, incremental loads, freshness tests |
| **Whale Detection** | RFM scoring, K-means clustering (5 segments), bot detection heuristics |
| **Anomaly Detection** | Rolling Z-score on hourly volume, severity classification (critical/high/medium/low) |
| **Token Flow Analysis** | Net inflow/outflow per token per hour, accumulation vs distribution labeling |
| **Protocol Health** | DAU, swap volume, median swap size, Gini coefficient, whale share %, composite health score |
| **Dashboard** | Expandable KPI cards, volume trend chart, whale table, anomaly feed, token flow table |
| **Infrastructure** | Vercel serverless deployment, Neon PostgreSQL, GitHub Actions scheduled pipeline |

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Ethereum Mainnet                             │
└──────────────┬──────────────────────────────────┬───────────────────┘
               │ Alchemy RPC                      │ CoinGecko API
               ▼                                  ▼
┌──────────────────────────┐        ┌──────────────────────────┐
│   EVM Indexer (Python)   │        │   Price Service (Python)  │
│  web3.py + block tracker │        │   5-min cache + DB write  │
└──────────┬───────────────┘        └──────────┬───────────────┘
           │                                   │
           ▼                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     Neon PostgreSQL                                  │
│  raw_events │ raw_swaps │ raw_transfers │ token_prices │ checkpoints │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     dbt Transformation                               │
│  staging → intermediate → marts (fact_swaps, dim_tokens, dim_wallets)│
│                        → analytics (agg_hourly_volume, agg_daily)    │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   Python Analysis Scripts                             │
│  whale_segmentation │ volume_anomaly │ token_flows │ protocol_health │
│         ↓                  ↓               ↓               ↓         │
│  analytics_wallet_segments │ analytics_anomalies │ analytics_token_*  │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│               Next.js 14 (Vercel)                                    │
│  Route Handlers (/api/*) → React Dashboard (Tailwind + Recharts)     │
└─────────────────────────────────────────────────────────────────────┘
```

| Component | Role | Tech |
|---|---|---|
| EVM Indexer | Fetches Swap + Transfer events from Ethereum | Python, web3.py, Alchemy |
| Price Service | USD enrichment with caching | Python, httpx, CoinGecko |
| Data Warehouse | Star-schema transformation | dbt-core, dbt-postgres |
| Analysis Engine | Statistical analysis (4 modules) | scikit-learn, scipy, pandas |
| API Layer | Serverless REST endpoints | Next.js Route Handlers |
| Dashboard | Interactive analytics UI | React, Tailwind, Recharts, Framer Motion |
| Database | Serverless PostgreSQL | Neon |
| CI/CD | Scheduled pipeline runs | GitHub Actions |

---

## 🛠 Tech Stack

**Backend** — Python 3.12 · web3.py · scikit-learn · pandas · scipy · psycopg2 · httpx

**Data** — dbt-core 1.8 · dbt-postgres · Neon PostgreSQL

**Frontend** — Next.js 14 · TypeScript · Tailwind CSS · Recharts · Framer Motion · Lucide Icons

**Infrastructure** — Vercel (app + API) · Neon (database) · GitHub Actions (pipeline) · Docker Compose (local dev)

---

## 🚀 Quick Start

**Prerequisites:** Node.js 18+, Git, a Neon database (or Docker for local Postgres)

```bash
# 1. Clone
git clone https://github.com/ArivunidhiA/ChainPulse.git && cd ChainPulse

# 2. Apply database schema (use your Neon connection string)
psql "$DATABASE_URL" -f backend/db/schema.sql

# 3. (Optional) Seed demo data for instant dashboard
psql "$DATABASE_URL" -f backend/seed_data.sql

# 4. Configure frontend
cp frontend/.env.example frontend/.env
# Edit frontend/.env → set DATABASE_URL to your Neon connection string

# 5. Start the dashboard
cd frontend && npm install && npm run dev
```

Open **http://localhost:3000** — landing page loads immediately. Click "Explore dashboard" to see the analytics.

---

## 📡 API Reference

All endpoints are Next.js Route Handlers (serverless on Vercel).

| Endpoint | Description | Params |
|---|---|---|
| `GET /api/health` | Liveness + DB connectivity | — |
| `GET /api/data-freshness` | Seconds since last indexed event | — |
| `GET /api/stats` | Dashboard summary (volume, wallets, swaps, anomalies) | — |
| `GET /api/swaps` | Paginated swap records | `limit`, `offset`, `token_address`, `wallet_address` |
| `GET /api/whales` | Wallet segments (RFM + K-means) | `limit`, `offset`, `segment` |
| `GET /api/volume` | Hourly volume time series | `limit`, `token_address` |
| `GET /api/anomalies` | Z-score flagged anomalies | `limit`, `offset`, `severity`, `token_address` |
| `GET /api/token-flows` | Net token flow per hour | `limit`, `token_address` |
| `GET /api/protocol-health` | Daily health KPIs | `limit` |

---

## 🌐 Deployment

**Vercel** (frontend + API):
1. Import repo at [vercel.com/new](https://vercel.com/new)
2. Set **Root Directory** → `frontend`
3. Add env variable: `DATABASE_URL` = your Neon connection string
4. Deploy

**GitHub Actions** (data pipeline):
Add these secrets in repo **Settings → Secrets → Actions**:
- `DATABASE_URL` — Neon connection string
- `ALCHEMY_API_URL` — Alchemy Ethereum RPC
- `COINGECKO_API_KEY` — CoinGecko API key
- `PGHOST`, `PGUSER`, `PGPASSWORD`, `PGDATABASE` — for dbt

Full guide: **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)**

---

## 📁 Project Structure

```
ChainPulse/
├── backend/
│   ├── indexer/          # EVM event indexer (web3.py)
│   ├── analysis/         # 4 analysis modules (whale, anomaly, flow, health)
│   ├── db/               # Schema, connection pool, query helpers
│   └── seed_data.sql     # Demo data seed script
├── dbt_chainpulse/
│   ├── models/
│   │   ├── staging/      # Raw data cleaning + dedup
│   │   ├── intermediate/ # Enriched joins
│   │   ├── marts/        # Star schema (facts + dimensions)
│   │   └── analytics/    # Aggregations + views
│   ├── seeds/            # known_tokens.csv
│   └── tests/            # Custom data quality tests
├── frontend/
│   ├── app/              # Next.js pages + API route handlers
│   ├── components/       # Dashboard widgets (5 panels)
│   └── lib/              # DB client, API helpers, utils
├── .github/workflows/    # CI/CD: scheduled pipeline + dbt runs
└── docs/                 # Deployment guide
```

---

## 📄 License

MIT — see [LICENSE](LICENSE) for details.

---

<p align="center">
  Built by <a href="https://arivfolio.tech">Arivunidhi</a> · 
  <a href="https://github.com/ArivunidhiA">GitHub</a> · 
  <a href="https://www.linkedin.com/in/arivunidhi-anna-arivan/">LinkedIn</a> · 
  <a href="https://x.com/Ariv_2012">𝕏</a>
</p>
