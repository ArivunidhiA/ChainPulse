"""
Token flow: inflow/outflow/net per token per hour. Output → analytics_token_flows.
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta

from db.connection import init_connection_pool
from db.queries import run_query, execute_sql


def _ensure_pool():
    init_connection_pool()


def _transfer_flows(hours: int = 168 * 2) -> list[dict]:
    _ensure_pool()
    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    sql = """
        SELECT
            date_trunc('hour', event_timestamp) AS hour_bucket,
            token_address,
            from_address,
            to_address,
            COALESCE(amount_usd, 0) AS amount_usd,
            COALESCE(direction, 'out') AS direction
        FROM marts.fact_transfers
        WHERE event_timestamp >= %s
    """
    try:
        return run_query(sql, (since,))
    except Exception:
        sql_raw = """
            SELECT
                date_trunc('hour', event_timestamp) AS hour_bucket,
                token_address,
                from_address,
                to_address,
                COALESCE(usd_value, 0) AS amount_usd,
                COALESCE(direction, 'out') AS direction
            FROM raw_transfers
            WHERE event_timestamp >= %s
        """
        return run_query(sql_raw, (since,))


def run() -> None:
    _ensure_pool()
    rows = _transfer_flows(168 * 2)
    if not rows:
        return
    # Aggregate by (hour_bucket, token_address): inflow, outflow, unique_senders, unique_receivers
    agg: dict[tuple, dict] = {}
    for r in rows:
        h = r.get("hour_bucket")
        if hasattr(h, "isoformat"):
            pass
        elif isinstance(h, str):
            from dateutil import parser
            h = parser.parse(h)
        else:
            continue
        tok = (r.get("token_address") or "").strip().lower()
        if not tok:
            continue
        key = (h, tok)
        if key not in agg:
            agg[key] = {"inflow": 0.0, "outflow": 0.0, "senders": set(), "receivers": set()}
        amt = float(r.get("amount_usd") or 0)
        direction = (r.get("direction") or "out").lower()
        if direction == "in":
            agg[key]["inflow"] += amt
        else:
            agg[key]["outflow"] += amt
        agg[key]["senders"].add((r.get("from_address") or "").strip())
        agg[key]["receivers"].add((r.get("to_address") or "").strip())

    threshold = 1000.0
    execute_sql("TRUNCATE analytics_token_flows")
    for (hour_bucket, token_address), v in agg.items():
        inflow = v["inflow"]
        outflow = v["outflow"]
        net = inflow - outflow
        if net > threshold:
            flow_direction = "accumulation"
        elif net < -threshold:
            flow_direction = "distribution"
        else:
            flow_direction = "neutral"
        execute_sql(
            """
            INSERT INTO analytics_token_flows
            (hour_bucket, token_address, inflow_usd, outflow_usd, net_flow_usd, unique_senders, unique_receivers, flow_direction)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (hour_bucket, token_address) DO UPDATE SET
                inflow_usd = EXCLUDED.inflow_usd,
                outflow_usd = EXCLUDED.outflow_usd,
                net_flow_usd = EXCLUDED.net_flow_usd,
                unique_senders = EXCLUDED.unique_senders,
                unique_receivers = EXCLUDED.unique_receivers,
                flow_direction = EXCLUDED.flow_direction
            """,
            (
                hour_bucket,
                token_address,
                inflow,
                outflow,
                net,
                len(v["senders"]),
                len(v["receivers"]),
                flow_direction,
            ),
        )


if __name__ == "__main__":
    run()
