"""
FastAPI routes: serve pre-computed analytics with pagination and filters.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from db.connection import init_connection_pool
from db.queries import run_query, get_latest_event_timestamp

router = APIRouter(prefix="/api", tags=["api"])


def _serialize_row(r: dict) -> dict:
    out = {}
    for k, v in r.items():
        if hasattr(v, "isoformat"):
            out[k] = v.isoformat()
        elif hasattr(v, "__float__") and not isinstance(v, bool):
            try:
                out[k] = float(v)
            except (TypeError, ValueError):
                out[k] = v
        else:
            out[k] = v
    return out


@router.get("/health")
def health():
    try:
        init_connection_pool()
        run_query("SELECT 1")
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        return JSONResponse({"status": "error", "db": str(e)}, status_code=503)


@router.get("/data-freshness")
def data_freshness():
    ts = get_latest_event_timestamp()
    if not ts:
        return {"seconds_since_last_event": None, "message": "No events yet"}
    from datetime import datetime, timezone
    from dateutil import parser
    try:
        last = parser.parse(ts)
        if last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)
    except Exception:
        return {"seconds_since_last_event": None, "message": "Invalid timestamp"}
    delta = (datetime.now(timezone.utc) - last).total_seconds()
    return {"seconds_since_last_event": int(delta), "last_event_at": ts}


@router.get("/swaps")
def get_swaps(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    token_address: Optional[str] = Query(None),
    wallet_address: Optional[str] = Query(None),
):
    try:
        sql = """
            SELECT swap_id, block_number, tx_hash, wallet_address, token_in_address, token_out_address,
                   amount_in, amount_out, amount_usd, pool_address, event_timestamp, is_whale, wallet_segment
            FROM marts.fact_swaps
            WHERE 1=1
        """
        params = []
        if token_address:
            sql += " AND (token_in_address = %s OR token_out_address = %s)"
            t = token_address.lower().strip()
            params.extend([t, t])
        if wallet_address:
            sql += " AND wallet_address = %s"
            params.append(wallet_address.lower().strip())
        sql += " ORDER BY event_timestamp DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        rows = run_query(sql, tuple(params))
    except Exception:
        sql = """
            SELECT block_number, tx_hash, sender_address AS wallet_address, token0_address AS token_in_address,
                   token1_address AS token_out_address, amount0 AS amount_in, amount1 AS amount_out,
                   usd_value AS amount_usd, pool_address, event_timestamp
            FROM raw_swaps
            ORDER BY event_timestamp DESC LIMIT %s OFFSET %s
        """
        params = [limit, offset]
        rows = run_query(sql, tuple(params))
    return {"data": [_serialize_row(r) for r in rows], "limit": limit, "offset": offset}


@router.get("/whales")
def get_whales(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    segment: Optional[str] = Query(None),
):
    sql = """
        SELECT wallet_address, segment, cluster_id, rfm_recency, rfm_frequency, rfm_volume, computed_at
        FROM analytics_wallet_segments
        WHERE 1=1
    """
    params = []
    if segment:
        sql += " AND segment = %s"
        params.append(segment.strip().lower())
    sql += " ORDER BY rfm_volume DESC NULLS LAST LIMIT %s OFFSET %s"
    params.extend([limit, offset])
    try:
        rows = run_query(sql, tuple(params))
    except Exception:
        rows = []
    return {"data": [_serialize_row(r) for r in rows], "limit": limit, "offset": offset}


@router.get("/volume")
def get_volume(
    limit: int = Query(168, ge=1, le=720),
    token_address: Optional[str] = Query(None),
):
    try:
        sql = """
            SELECT hour_bucket, token_address, swap_count, volume_usd, unique_wallets
            FROM analytics.agg_hourly_volume
            WHERE 1=1
        """
        params = []
        if token_address:
            sql += " AND token_address = %s"
            params.append(token_address.lower().strip())
        sql += " ORDER BY hour_bucket DESC LIMIT %s"
        params.append(limit)
        rows = run_query(sql, tuple(params))
    except Exception:
        sql = """
            SELECT date_trunc('hour', event_timestamp) AS hour_bucket, token0_address AS token_address,
                   count(*) AS swap_count, sum(COALESCE(usd_value, 0)) AS volume_usd, count(DISTINCT sender_address) AS unique_wallets
            FROM raw_swaps
            GROUP BY 1, 2
            ORDER BY 1 DESC LIMIT %s
        """
        rows = run_query(sql, (limit,))
    return {"data": [_serialize_row(r) for r in rows], "limit": limit}


@router.get("/anomalies")
def get_anomalies(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    severity: Optional[str] = Query(None),
    token_address: Optional[str] = Query(None),
):
    sql = """
        SELECT anomaly_id, hour_bucket, token_address, actual_volume, expected_volume, z_score, severity, detected_at
        FROM analytics_anomalies
        WHERE 1=1
    """
    params = []
    if severity:
        sql += " AND severity = %s"
        params.append(severity.strip().lower())
    if token_address:
        sql += " AND token_address = %s"
        params.append(token_address.lower().strip())
    sql += " ORDER BY detected_at DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])
    try:
        rows = run_query(sql, tuple(params))
    except Exception:
        rows = []
    return {"data": [_serialize_row(r) for r in rows], "limit": limit, "offset": offset}


@router.get("/token-flows")
def get_token_flows(
    limit: int = Query(168, ge=1, le=720),
    token_address: Optional[str] = Query(None),
):
    sql = """
        SELECT hour_bucket, token_address, inflow_usd, outflow_usd, net_flow_usd, unique_senders, unique_receivers, flow_direction
        FROM analytics_token_flows
        WHERE 1=1
    """
    params = []
    if token_address:
        sql += " AND token_address = %s"
        params.append(token_address.lower().strip())
    sql += " ORDER BY hour_bucket DESC LIMIT %s"
    params.append(limit)
    try:
        rows = run_query(sql, tuple(params))
    except Exception:
        rows = []
    return {"data": [_serialize_row(r) for r in rows], "limit": limit}


@router.get("/protocol-health")
def get_protocol_health(limit: int = Query(30, ge=1, le=90)):
    sql = """
        SELECT date_bucket, unique_active_wallets, total_swaps, total_volume_usd, median_swap_size, gini_coefficient, whale_share_pct, health_score
        FROM analytics_protocol_health
        ORDER BY date_bucket DESC LIMIT %s
    """
    try:
        rows = run_query(sql, (limit,))
    except Exception:
        rows = []
    return {"data": [_serialize_row(r) for r in rows], "limit": limit}


@router.get("/stats")
def get_stats():
    out = {"total_volume_usd": 0, "active_wallets": 0, "total_swaps": 0, "anomalies_count": 0}
    try:
        r = run_query("SELECT coalesce(sum(total_volume_usd), 0) AS v FROM analytics_protocol_health")
        if r:
            out["total_volume_usd"] = float(r[0].get("v") or 0)
    except Exception:
        pass
    try:
        r = run_query("SELECT unique_active_wallets AS v FROM analytics_protocol_health ORDER BY date_bucket DESC LIMIT 1")
        if r:
            out["active_wallets"] = int(r[0].get("v") or 0)
    except Exception:
        try:
            r = run_query("SELECT count(DISTINCT sender_address) AS v FROM raw_swaps")
            if r:
                out["active_wallets"] = int(r[0].get("v") or 0)
        except Exception:
            pass
    try:
        r = run_query("SELECT coalesce(sum(total_swaps), 0) AS v FROM analytics_protocol_health")
        if r:
            out["total_swaps"] = int(r[0].get("v") or 0)
    except Exception:
        try:
            r = run_query("SELECT count(*) AS v FROM raw_swaps")
            if r:
                out["total_swaps"] = int(r[0].get("v") or 0)
        except Exception:
            pass
    try:
        r = run_query("SELECT count(*) AS v FROM analytics_anomalies")
        if r:
            out["anomalies_count"] = int(r[0].get("v") or 0)
    except Exception:
        pass
    return out
