"""
Whale segmentation: K-means (k=4) + RFM scoring. Output → analytics_wallet_segments.
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from decimal import Decimal

import numpy as np
from sklearn.cluster import KMeans

from db.connection import init_connection_pool
from db.queries import run_query, execute_sql


def _ensure_pool():
    init_connection_pool()


def _fetch_swap_activity(days: int = 30) -> list[dict]:
    _ensure_pool()
    # Prefer marts.fact_swaps; fallback to raw_swaps if marts not populated
    sql = """
        SELECT sender_address AS wallet_address, event_timestamp, COALESCE(usd_value, 0) AS amount_usd
        FROM raw_swaps
        WHERE event_timestamp >= %s
    """
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    try:
        rows = run_query(sql, (since,))
    except Exception:
        sql_marts = """
            SELECT wallet_address, event_timestamp, amount_usd
            FROM marts.fact_swaps
            WHERE event_timestamp >= %s
        """
        rows = run_query(sql_marts, (since,))
    return rows


def _rfm_and_cluster(rows: list[dict]) -> list[dict]:
    if not rows:
        return []
    now = datetime.now(timezone.utc)
    by_wallet: dict[str, list[dict]] = {}
    for r in rows:
        w = (r.get("wallet_address") or "").strip().lower()
        if not w:
            continue
        if w not in by_wallet:
            by_wallet[w] = []
        ts = r.get("event_timestamp")
        if hasattr(ts, "isoformat"):
            pass
        elif isinstance(ts, str):
            from dateutil import parser
            ts = parser.parse(ts)
        else:
            continue
        amount = float(r.get("amount_usd") or 0)
        by_wallet[w].append({"ts": ts, "amount": amount})

    recency_list = []
    frequency_list = []
    volume_list = []
    wallets = []
    for w, events in by_wallet.items():
        if not events:
            continue
        last_ts = max(e["ts"] for e in events)
        recency_list.append((now - last_ts).total_seconds() / 86400)
        frequency_list.append(len(events))
        volume_list.append(sum(e["amount"] for e in events))
        wallets.append(w)

    if len(wallets) < 4:
        return []

    X = np.column_stack([
        np.array(recency_list),
        np.log1p(frequency_list),
        np.log1p(volume_list),
    ])
    X = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-9)
    kmeans = KMeans(n_clusters=min(4, len(wallets)), random_state=42, n_init=10)
    labels = kmeans.fit_predict(X)

    volume_sorted = sorted(zip(wallets, volume_list), key=lambda x: -x[1])
    top_1_pct = max(1, len(volume_sorted) // 100)
    whale_wallets = {w for w, _ in volume_sorted[:top_1_pct]}
    for w, events in by_wallet.items():
        if any(e["amount"] >= 50000 for e in events):
            whale_wallets.add(w)

    result = []
    for i, w in enumerate(wallets):
        rec = recency_list[i]
        freq = frequency_list[i]
        vol = volume_list[i]
        cluster = int(labels[i])
        # Bot: >50 swaps/day and avg < 100
        n_days = max(0.1, (now - min(e["ts"] for e in by_wallet[w])).total_seconds() / 86400)
        swaps_per_day = len(by_wallet[w]) / n_days
        avg_size = vol / len(by_wallet[w]) if by_wallet[w] else 0
        if swaps_per_day >= 50 and avg_size < 100:
            segment = "bot"
        elif w in whale_wallets:
            segment = "whale"
        elif cluster == 1 or (freq >= 10 and vol >= 10000):
            segment = "active_trader"
        else:
            segment = "retail"
        result.append({
            "wallet_address": w,
            "segment": segment,
            "cluster_id": cluster,
            "rfm_recency": round(rec, 4),
            "rfm_frequency": freq,
            "rfm_volume": round(vol, 2),
            "computed_at": now,
        })
    return result


def run() -> None:
    _ensure_pool()
    rows = _fetch_swap_activity(30)
    segments = _rfm_and_cluster(rows)
    if not segments:
        return
    now = datetime.now(timezone.utc)
    execute_sql("TRUNCATE analytics_wallet_segments")
    for s in segments:
        execute_sql(
            """
            INSERT INTO analytics_wallet_segments
            (wallet_address, segment, cluster_id, rfm_recency, rfm_frequency, rfm_volume, computed_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (wallet_address) DO UPDATE SET
                segment = EXCLUDED.segment,
                cluster_id = EXCLUDED.cluster_id,
                rfm_recency = EXCLUDED.rfm_recency,
                rfm_frequency = EXCLUDED.rfm_frequency,
                rfm_volume = EXCLUDED.rfm_volume,
                computed_at = EXCLUDED.computed_at
            """,
            (
                s["wallet_address"],
                s["segment"],
                s["cluster_id"],
                s["rfm_recency"],
                s["rfm_frequency"],
                s["rfm_volume"],
                s["computed_at"],
            ),
        )


if __name__ == "__main__":
    run()
