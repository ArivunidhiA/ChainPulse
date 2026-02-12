"""
Protocol health: DAU, swap count, volume, median swap size, Gini, whale share %, health score 0-100.
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta

from db.connection import init_connection_pool
from db.queries import run_query, execute_sql


def _ensure_pool():
    init_connection_pool()


def _gini(values: list[float]) -> float:
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    cumsum = 0.0
    for i, v in enumerate(sorted_vals):
        cumsum += (2 * (i + 1) - n - 1) * v
    total = sum(sorted_vals)
    if total == 0:
        return 0.0
    return cumsum / (n * total)


def _daily_metrics() -> list[dict]:
    _ensure_pool()
    sql = """
        SELECT
            date_trunc('day', event_timestamp)::date AS date_bucket,
            count(DISTINCT wallet_address) AS unique_active_wallets,
            count(*) AS total_swaps,
            sum(amount_usd) AS total_volume_usd,
            percentile_cont(0.5) WITHIN GROUP (ORDER BY amount_usd) AS median_swap_size
        FROM marts.fact_swaps
        GROUP BY 1
    """
    try:
        return run_query(sql, ())
    except Exception:
        sql_raw = """
            SELECT
                date_trunc('day', event_timestamp)::date AS date_bucket,
                count(DISTINCT sender_address) AS unique_active_wallets,
                count(*) AS total_swaps,
                sum(COALESCE(usd_value, 0)) AS total_volume_usd,
                percentile_cont(0.5) WITHIN GROUP (ORDER BY COALESCE(usd_value, 0)) AS median_swap_size
            FROM raw_swaps
            GROUP BY 1
        """
        return run_query(sql_raw, ())


def _daily_whale_share() -> dict[tuple, float]:
    _ensure_pool()
    sql = """
        SELECT
            date_trunc('day', event_timestamp)::date AS date_bucket,
            sum(CASE WHEN amount_usd >= 50000 THEN amount_usd ELSE 0 END) AS whale_volume,
            sum(amount_usd) AS total_volume
        FROM marts.fact_swaps
        GROUP BY 1
    """
    try:
        rows = run_query(sql, ())
    except Exception:
        sql_raw = """
            SELECT
                date_trunc('day', event_timestamp)::date AS date_bucket,
                sum(CASE WHEN COALESCE(usd_value, 0) >= 50000 THEN usd_value ELSE 0 END) AS whale_volume,
                sum(COALESCE(usd_value, 0)) AS total_volume
            FROM raw_swaps
            GROUP BY 1
        """
        rows = run_query(sql_raw, ())
    out = {}
    for r in rows:
        db = r.get("date_bucket")
        total = float(r.get("total_volume") or 0)
        whale = float(r.get("whale_volume") or 0)
        out[db] = (whale / total * 100.0) if total else 0.0
    return out


def _daily_wallet_volumes() -> dict[tuple, list[float]]:
    _ensure_pool()
    sql = """
        SELECT
            date_trunc('day', event_timestamp)::date AS date_bucket,
            wallet_address,
            sum(amount_usd) AS vol
        FROM marts.fact_swaps
        GROUP BY 1, 2
    """
    try:
        rows = run_query(sql, ())
    except Exception:
        sql_raw = """
            SELECT
                date_trunc('day', event_timestamp)::date AS date_bucket,
                sender_address AS wallet_address,
                sum(COALESCE(usd_value, 0)) AS vol
            FROM raw_swaps
            GROUP BY 1, 2
        """
        rows = run_query(sql_raw, ())
    by_date: dict[tuple, list[float]] = {}
    for r in rows:
        db = r.get("date_bucket")
        vol = float(r.get("vol") or 0)
        by_date.setdefault(db, []).append(vol)
    return by_date


def run() -> None:
    _ensure_pool()
    daily = _daily_metrics()
    whale_share = _daily_whale_share()
    wallet_vols = _daily_wallet_volumes()
    if not daily:
        return
    execute_sql("TRUNCATE analytics_protocol_health")
    for r in daily:
        db = r.get("date_bucket")
        if not db:
            continue
        uaw = int(r.get("unique_active_wallets") or 0)
        total_swaps = int(r.get("total_swaps") or 0)
        total_volume = float(r.get("total_volume_usd") or 0)
        median_swap = float(r.get("median_swap_size") or 0)
        gini = _gini(wallet_vols.get(db, []))
        ws = whale_share.get(db, 0.0)
        # Health score 0-100: weighted mix of activity and diversity
        health = 0.0
        if total_volume > 0:
            health += min(30, (total_volume / 1e6) * 30)  # volume component
        if uaw > 0:
            health += min(25, uaw / 10)  # wallet activity
        health += (1 - gini) * 25  # lower gini = more distributed = better
        health += min(20, total_swaps / 50)
        health_score = min(100.0, health)
        execute_sql(
            """
            INSERT INTO analytics_protocol_health
            (date_bucket, unique_active_wallets, total_swaps, total_volume_usd, median_swap_size, gini_coefficient, whale_share_pct, health_score)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (date_bucket) DO UPDATE SET
                unique_active_wallets = EXCLUDED.unique_active_wallets,
                total_swaps = EXCLUDED.total_swaps,
                total_volume_usd = EXCLUDED.total_volume_usd,
                median_swap_size = EXCLUDED.median_swap_size,
                gini_coefficient = EXCLUDED.gini_coefficient,
                whale_share_pct = EXCLUDED.whale_share_pct,
                health_score = EXCLUDED.health_score
            """,
            (db, uaw, total_swaps, total_volume, median_swap, round(gini, 6), round(ws, 4), round(health_score, 2)),
        )


if __name__ == "__main__":
    run()
