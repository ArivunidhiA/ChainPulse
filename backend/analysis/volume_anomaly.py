"""
Z-score anomaly detection on hourly volume. Output → analytics_anomalies.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone, timedelta

from db.connection import init_connection_pool
from db.queries import run_query, execute_sql


def _ensure_pool():
    init_connection_pool()


def _hourly_volume(hours: int = 168 * 2) -> list[dict]:
    _ensure_pool()
    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    sql = """
        SELECT
            date_trunc('hour', event_timestamp) AS hour_bucket,
            token_in_address AS token_address,
            sum(amount_usd) AS volume_usd
        FROM marts.fact_swaps
        WHERE event_timestamp >= %s
        GROUP BY 1, 2
    """
    try:
        return run_query(sql, (since,))
    except Exception:
        sql_raw = """
            SELECT
                date_trunc('hour', event_timestamp) AS hour_bucket,
                token0_address AS token_address,
                sum(COALESCE(usd_value, 0)) AS volume_usd
            FROM raw_swaps
            WHERE event_timestamp >= %s
            GROUP BY 1, 2
        """
        return run_query(sql_raw, (since,))


def _severity(z: float) -> str:
    abs_z = abs(z)
    if abs_z > 3.0:
        return "critical"
    if abs_z > 2.5:
        return "high"
    if abs_z > 2.0:
        return "medium"
    if abs_z > 1.5:
        return "low"
    return "normal"


def run() -> None:
    _ensure_pool()
    rows = _hourly_volume(168 * 2)
    if not rows:
        return
    # Build series per (token_address): list of (hour_bucket, volume)
    by_token: dict[str, list[tuple[datetime, float]]] = {}
    for r in rows:
        tok = (r.get("token_address") or "").strip().lower()
        if not tok:
            continue
        h = r.get("hour_bucket")
        if hasattr(h, "isoformat"):
            pass
        elif isinstance(h, str):
            from dateutil import parser
            h = parser.parse(h)
        else:
            continue
        vol = float(r.get("volume_usd") or 0)
        by_token.setdefault(tok, []).append((h, vol))

    window = 168  # 7 days
    anomalies = []
    now = datetime.now(timezone.utc)
    for token_address, series in by_token.items():
        series.sort(key=lambda x: x[0])
        for i in range(window, len(series)):
            recent = [v for _, v in series[i - window:i]]
            if len(recent) < 2:
                continue
            mean = sum(recent) / len(recent)
            var = sum((x - mean) ** 2 for x in recent) / len(recent)
            std = (var ** 0.5) or 1e-9
            current = series[i][1]
            z = (current - mean) / std if std else 0
            if abs(z) > 1.5:
                severity = _severity(z)
                anomalies.append({
                    "anomaly_id": uuid.uuid4(),
                    "hour_bucket": series[i][0],
                    "token_address": token_address,
                    "actual_volume": current,
                    "expected_volume": mean,
                    "z_score": round(z, 4),
                    "severity": severity,
                    "detected_at": now,
                })

    execute_sql("TRUNCATE analytics_anomalies")
    for a in anomalies:
        execute_sql(
            """
            INSERT INTO analytics_anomalies
            (anomaly_id, hour_bucket, token_address, actual_volume, expected_volume, z_score, severity, detected_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                a["anomaly_id"],
                a["hour_bucket"],
                a["token_address"],
                a["actual_volume"],
                a["expected_volume"],
                a["z_score"],
                a["severity"],
                a["detected_at"],
            ),
        )


if __name__ == "__main__":
    run()
