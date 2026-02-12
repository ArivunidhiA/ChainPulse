# Run ChainPulse locally

## Option A: Local Postgres (Docker)

1. Start Docker Desktop, then:
   ```bash
   docker compose up -d db
   ```
2. Wait ~5s, then apply schema:
   ```bash
   psql "postgresql://postgres:postgres@localhost:5432/chainpulse" -f backend/db/schema.sql
   ```
   (If `psql` is not installed, use any Postgres client or run the SQL in `backend/db/schema.sql` against the DB.)

3. In `frontend/.env` set:
   ```
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/chainpulse
   ```

4. Run the app:
   ```bash
   cd frontend && npm install && npm run dev
   ```
   Open http://localhost:3000

5. (Optional) To get data, run the pipeline once (from repo root):
   ```bash
   cd backend && pip install -r requirements.txt
   export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/chainpulse
   export ALCHEMY_API_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY
   PYTHONPATH=. python -c "from indexer.evm_indexer import run_indexer_once; run_indexer_once()"
   cd ../dbt_chainpulse && dbt deps && dbt seed && dbt run
   cd ../backend && PYTHONPATH=. python -c "from analysis.whale_segmentation import run; run()"
   # ... other analysis scripts
   ```

## Option B: Neon (no Docker)

1. Create a Neon project and run the schema:
   ```bash
   psql "YOUR_NEON_CONNECTION_STRING" -f backend/db/schema.sql
   ```

2. In `frontend/.env` set:
   ```
   DATABASE_URL=YOUR_NEON_CONNECTION_STRING
   ```

3. Run the app:
   ```bash
   cd frontend && npm install && npm run dev
   ```
   Open http://localhost:3000

Data will appear after the pipeline (indexer + dbt + analysis) has run at least once (e.g. via GitHub Actions or the optional steps in Option A.5).
