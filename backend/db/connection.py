import os
from contextlib import contextmanager
from typing import Iterator

import psycopg2
from psycopg2.pool import SimpleConnectionPool


_pool: SimpleConnectionPool | None = None


def get_database_url() -> str:
    """Resolve the Postgres connection string."""
    url = os.getenv("DATABASE_URL")
    if not url:
        # Fallback to discrete env vars (e.g. for dbt profile)
        host = os.getenv("PGHOST", "localhost")
        port = os.getenv("PGPORT", "5432")
        dbname = os.getenv("PGDATABASE", "chainpulse")
        user = os.getenv("PGUSER", "postgres")
        password = os.getenv("PGPASSWORD", "postgres")
        url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
    return url


def init_connection_pool(minconn: int = 1, maxconn: int = 10) -> None:
    """Initialise a global psycopg2 connection pool."""
    global _pool
    if _pool is None:
        _pool = SimpleConnectionPool(minconn, maxconn, get_database_url())


def close_connection_pool() -> None:
    """Close all connections in the global pool."""
    global _pool
    if _pool is not None:
        _pool.closeall()
        _pool = None


@contextmanager
def get_conn_cursor():
    """
    Context manager yielding a (connection, cursor) pair.

    Ensures that connections are returned to the pool and transactions are
    committed/rolled back appropriately.
    """
    if _pool is None:
        init_connection_pool()

    assert _pool is not None
    conn = _pool.getconn()
    try:
        cursor = conn.cursor()
        try:
            yield conn, cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
    finally:
        _pool.putconn(conn)

