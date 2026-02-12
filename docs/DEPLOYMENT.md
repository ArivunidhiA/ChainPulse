# ChainPulse Deployment (Vercel + Neon)

## Overview

- **App + API**: Single Vercel project (Next.js app and API route handlers that query Neon).
- **Database**: Neon PostgreSQL.
- **Pipeline**: GitHub Actions runs indexer, dbt, and analysis on a schedule and writes to Neon.

No separate backend server (e.g. Render) is required.

## 1. Neon

1. Create a project at [neon.tech](https://neon.tech).
2. Copy the connection string (include `?sslmode=require`).
3. Run the schema once (from repo root):
   ```bash
   psql "YOUR_NEON_CONNECTION_STRING" -f backend/db/schema.sql
   ```

## 2. Vercel (app + API)

1. Import the repo; set **Root Directory** to `frontend`.
2. In **Settings → Environment Variables**, add:
   - **`DATABASE_URL`** (or **`POSTGRES_URL`**) — your Neon connection string.  
     Required for the serverless API routes that read from Neon.
3. Deploy. The dashboard and all `/api/*` endpoints (stats, whales, volume, anomalies, token-flows, protocol-health, health, data-freshness) run on Vercel and query Neon.

With Vercel Pro you get higher function timeouts and no need for a separate backend.

## 3. GitHub Actions (pipeline)

The pipeline (indexer → dbt → analysis) runs in GitHub Actions and writes to Neon.

Add **Repository secrets** (Neon + Alchemy):

- `DATABASE_URL` — Neon connection string (used by indexer and analysis).
- `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`, `PGSSLMODE=require` — for dbt (or use `DATABASE_URL` and set dbt to use it).
- `ALCHEMY_API_URL` — Alchemy Ethereum RPC URL.
- Optional: `COINGECKO_API_KEY`.

Workflows:

- **`pipeline.yml`** — runs indexer, dbt, and analysis on a schedule (e.g. every 30 minutes).
- **`dbt_scheduled.yml`** — dbt-only run every 30 minutes (optional backup).

After the first successful pipeline run, the dashboard will show data.

## 4. Post-deploy

1. Check API health: `GET https://your-app.vercel.app/api/health`.
2. Open the app; once the pipeline has run at least once, the dashboard will show stats, volume, whales, anomalies, and token flows.
