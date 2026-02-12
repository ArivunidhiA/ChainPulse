# ChainPulse — On-Chain DeFi Analytics Pipeline

Production-grade pipeline that extracts, transforms, and analyzes EVM smart contract events (Uniswap V3, ERC-20) through a modern data stack: **Python + web3.py**, **dbt**, **Neon PostgreSQL**, with statistical analysis and a **Next.js** dashboard.

## Architecture

```mermaid
flowchart TB
  subgraph extraction [Extraction Layer]
    EVM[EVM Indexer - web3.py]
    Price[CoinGecko Price Service]
    Checkpoint[Block Checkpoint Tracker]
  end

  subgraph store [Neon PostgreSQL]
    Raw[raw_events, raw_swaps, raw_transfers]
    Analytics[analytics_wallet_segments, analytics_anomalies, analytics_token_flows, analytics_protocol_health]
  end

  subgraph transformation [dbt Transformation]
    Staging[staging]
    Intermediate[intermediate]
    Marts[marts: fact_swaps, fact_transfers, dim_tokens, dim_wallets]
    Agg[analytics: agg_hourly_volume, agg_daily_protocol]
  end

  subgraph analysis [Analysis Scripts]
    Whale[whale_segmentation]
    Anomaly[volume_anomaly]
    Flow[token_flow_analysis]
    Health[protocol_health]
  end

  subgraph api [FastAPI]
    Routes[/api/swaps, /whales, /volume, /anomalies, /token-flows, /protocol-health, /stats]
  end

  subgraph dashboard [Next.js Dashboard]
    UI[Protocol Health, Volume Chart, Whale Table, Anomaly Feed, Token Flows]
  end

  EVM --> Raw
  Price --> Raw
  Checkpoint --> EVM
  Raw --> Staging --> Intermediate --> Marts --> Agg
  Marts --> analysis --> Analytics
  Agg --> api
  Analytics --> api
  api --> UI
```

- **Extraction**: Uniswap V3 Swap + ERC-20 Transfer events (Alchemy RPC), block checkpoints, CoinGecko price enrichment.
- **Transformation**: dbt staging → intermediate → marts → analytics; Kimball-style star schema (fact_swaps, fact_transfers, dim_tokens, dim_wallets).
- **Analysis**: K-means whale segmentation, Z-score volume anomalies, token flow, Gini-based protocol health → `analytics_*` tables.
- **Serving**: FastAPI with APScheduler (indexer every 15s, dbt every 30min, analysis every hour).

## Tech stack

- **Backend**: Python 3.11, FastAPI, web3.py, APScheduler, psycopg2, scikit-learn, pandas
- **Warehouse**: Neon PostgreSQL (or local Postgres via Docker)
- **Transform**: dbt-core, dbt-postgres
- **Frontend**: Next.js 14, TypeScript, Tailwind, Recharts
- **Infra**: Docker Compose (local), Vercel (app + API), GitHub Actions (pipeline)

## Run locally (quick)

1. **Start Postgres** (Docker): `docker compose up -d db`  
   Then apply schema: `psql "postgresql://postgres:postgres@localhost:5432/chainpulse" -f backend/db/schema.sql`

2. **Frontend** already has `frontend/.env` with `DATABASE_URL=postgresql://postgres:postgres@localhost:5432/chainpulse`.  
   If you use Neon instead, replace `DATABASE_URL` in `frontend/.env` with your Neon connection string.

3. **Start the app**: `cd frontend && npm install && npm run dev`  
   Open **http://localhost:3000**

Without a running DB (or with an invalid `DATABASE_URL`), the UI loads but API calls will fail. See [scripts/run-local.md](scripts/run-local.md) for the full pipeline (indexer + dbt + analysis) to populate data.

## Setup

### 1. Environment

Copy `backend/.env.example` to `backend/.env` and set:

- `ALCHEMY_API_URL` — Alchemy Ethereum RPC URL
- `DATABASE_URL` — Neon Postgres connection string (or `PGHOST`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`, `PGSSLMODE=require` for dbt)
- `COINGECKO_API_KEY` — optional CoinGecko API key
- `FRONTEND_ORIGIN` — e.g. `http://localhost:3000` for CORS

Do not commit `.env`; use it for local overrides only.

### 2. Database

Apply the schema (e.g. on Neon):

```bash
psql "$DATABASE_URL" -f backend/db/schema.sql
```

### 3. Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

From the project root, run with Python path:

```bash
cd backend && PYTHONPATH=. uvicorn main:app --reload --port 8000
```

### 4. dbt

```bash
cd dbt_chainpulse
export PGHOST=... PGUSER=... PGPASSWORD=... PGDATABASE=... PGSSLMODE=require
dbt deps
dbt seed
dbt run
dbt test
```

### 5. Frontend

```bash
cd frontend
npm install
npm run dev
```

Set `NEXT_PUBLIC_API_URL=http://localhost:8000` if the API is not proxied. The app uses Next.js rewrites so `/api/*` can target the backend when same-origin.

## Deployment (Vercel + Neon)

See **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** for step-by-step deployment.

- **Neon**: Create project, run `backend/db/schema.sql`, add the connection string as `DATABASE_URL` in Vercel.
- **Vercel**: Set root to `frontend`, add `DATABASE_URL` (Neon). The app and all API routes run on Vercel (no separate backend).
- **GitHub Actions**: Add secrets (`DATABASE_URL`, `ALCHEMY_API_URL`, and PGHOST/PGUSER/PGPASSWORD/PGDATABASE for dbt). The pipeline (indexer, dbt, analysis) runs on a schedule and writes to Neon.

## Docker (local Postgres + backend)

```bash
docker compose up -d db
# Apply schema to local DB, then:
docker compose up -d backend
```

Backend will use `DATABASE_URL=postgresql://postgres:postgres@db:5432/chainpulse` from compose; mount `dbt_chainpulse` for scheduled dbt runs.

## API

- `GET /api/health` — liveness + DB
- `GET /api/data-freshness` — seconds since last indexed event
- `GET /api/stats` — dashboard summary (volume, wallets, swaps, anomalies)
- `GET /api/swaps` — paginated swaps (optional: token_address, wallet_address)
- `GET /api/whales` — wallet segments (optional: segment)
- `GET /api/volume` — hourly volume time series
- `GET /api/anomalies` — flagged anomalies (optional: severity)
- `GET /api/token-flows` — net flow per token
- `GET /api/protocol-health` — daily health KPIs

## Project layout

- `backend/` — FastAPI, indexer, analysis, db, scheduler
- `dbt_chainpulse/` — dbt project (staging, intermediate, marts, analytics)
- `frontend/` — Next.js app and dashboard components
- `docs/DEPLOYMENT.md` — deployment guide (Vercel + Neon, GitHub Actions pipeline)
- `ChainPulse_PRD_v2.md` — product requirements

## License

MIT.
