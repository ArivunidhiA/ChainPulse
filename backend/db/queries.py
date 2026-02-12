from __future__ import annotations

from typing import Iterable, List, Mapping, Sequence

from .connection import get_conn_cursor


def insert_raw_events(rows: Sequence[Mapping]) -> None:
    """
    Batch insert into raw_events.

    Each row should contain:
      block_number, tx_hash, log_index, contract_address,
      event_name, event_params (dict), event_timestamp
    """
    if not rows:
        return

    sql = """
        INSERT INTO raw_events (
            block_number,
            tx_hash,
            log_index,
            contract_address,
            event_name,
            event_params,
            event_timestamp
        )
        VALUES %s
        ON CONFLICT (tx_hash, log_index) DO NOTHING
    """
    values = [
        (
            r["block_number"],
            r["tx_hash"],
            r["log_index"],
            r["contract_address"],
            r["event_name"],
            r["event_params"],
            r["event_timestamp"],
        )
        for r in rows
    ]

    from psycopg2.extras import execute_values, Json

    # Ensure event_params is wrapped in Json for JSONB column
    safe_values = []
    for v in values:
        v_list = list(v)
        v_list[5] = Json(v_list[5]) if isinstance(v_list[5], dict) else v_list[5]
        safe_values.append(tuple(v_list))

    with get_conn_cursor() as (conn, cur):
        execute_values(cur, sql, safe_values)


def insert_raw_swaps(rows: Sequence[Mapping]) -> None:
    """
    Batch insert into raw_swaps.
    """
    if not rows:
        return

    sql = """
        INSERT INTO raw_swaps (
            block_number,
            tx_hash,
            log_index,
            pool_address,
            sender_address,
            recipient_address,
            token0_address,
            token1_address,
            amount0,
            amount1,
            sqrt_price_x96,
            liquidity,
            tick,
            usd_value,
            event_timestamp,
            size_bucket
        )
        VALUES %s
        ON CONFLICT (tx_hash, log_index) DO NOTHING
    """
    values = [
        (
            r["block_number"],
            r["tx_hash"],
            r["log_index"],
            r["pool_address"],
            r["sender_address"],
            r["recipient_address"],
            r["token0_address"],
            r["token1_address"],
            r["amount0"],
            r["amount1"],
            r.get("sqrt_price_x96"),
            r.get("liquidity"),
            r.get("tick"),
            r.get("usd_value"),
            r["event_timestamp"],
            r.get("size_bucket"),
        )
        for r in rows
    ]

    from psycopg2.extras import execute_values

    with get_conn_cursor() as (conn, cur):
        execute_values(cur, sql, values)


def insert_raw_transfers(rows: Sequence[Mapping]) -> None:
    """
    Batch insert into raw_transfers.
    """
    if not rows:
        return

    sql = """
        INSERT INTO raw_transfers (
            block_number,
            tx_hash,
            log_index,
            token_address,
            from_address,
            to_address,
            amount_raw,
            amount,
            usd_value,
            direction,
            is_exchange,
            event_timestamp
        )
        VALUES %s
        ON CONFLICT (tx_hash, log_index) DO NOTHING
    """
    values = [
        (
            r["block_number"],
            r["tx_hash"],
            r["log_index"],
            r["token_address"],
            r["from_address"],
            r["to_address"],
            r["amount_raw"],
            r.get("amount"),
            r.get("usd_value"),
            r.get("direction"),
            r.get("is_exchange", False),
            r["event_timestamp"],
        )
        for r in rows
    ]

    from psycopg2.extras import execute_values

    with get_conn_cursor() as (conn, cur):
        execute_values(cur, sql, values)


def upsert_token_price(token_address: str, coingecko_id: str, price_usd, fetched_at, source: str = "coingecko") -> None:
    """
    Upsert a token price record into token_prices.
    """
    sql = """
        INSERT INTO token_prices (
            token_address,
            coingecko_id,
            price_usd,
            fetched_at,
            source
        )
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (token_address) DO UPDATE SET
            coingecko_id = EXCLUDED.coingecko_id,
            price_usd = EXCLUDED.price_usd,
            fetched_at = EXCLUDED.fetched_at,
            source = EXCLUDED.source
    """
    with get_conn_cursor() as (conn, cur):
        cur.execute(sql, (token_address, coingecko_id, price_usd, fetched_at, source))


def get_latest_event_timestamp() -> str | None:
    """
    Return ISO string of the most recent event_timestamp in raw_events.
    """
    sql = "SELECT max(event_timestamp) FROM raw_events"
    with get_conn_cursor() as (conn, cur):
        cur.execute(sql)
        row = cur.fetchone()
    if not row or row[0] is None:
        return None
    return row[0].isoformat()


def get_block_checkpoint(contract_address: str) -> int | None:
    sql = """
        SELECT last_block
        FROM block_checkpoints
        WHERE contract_address = %s
    """
    with get_conn_cursor() as (conn, cur):
        cur.execute(sql, (contract_address,))
        row = cur.fetchone()
    return int(row[0]) if row and row[0] is not None else None


def upsert_block_checkpoint(contract_address: str, last_block: int) -> None:
    sql = """
        INSERT INTO block_checkpoints (contract_address, last_block)
        VALUES (%s, %s)
        ON CONFLICT (contract_address) DO UPDATE SET
            last_block = EXCLUDED.last_block,
            updated_at = NOW()
    """
    with get_conn_cursor() as (conn, cur):
        cur.execute(sql, (contract_address, last_block))


def run_query(sql: str, params: tuple = ()) -> list[dict]:
    """Execute SELECT and return list of dicts (column name -> value)."""
    import psycopg2.extras
    with get_conn_cursor() as (conn, cur):
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, params)
        rows = cur.fetchall()
        cur.close()
        return [dict(r) for r in rows]


def execute_sql(sql: str, params: tuple = ()) -> None:
    """Execute a single statement (insert/update/delete)."""
    with get_conn_cursor() as (conn, cur):
        cur.execute(sql, params)

