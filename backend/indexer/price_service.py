"""
CoinGecko price fetcher with 5-minute in-memory cache and optional DB write.
"""
from __future__ import annotations

import os
import time
from typing import Any, Dict, Optional

import httpx

from db import queries as db_queries

# Cache TTL seconds (5 min)
CACHE_TTL = 300

# In-memory cache: coingecko_id -> (price_usd, fetched_at)
_price_cache: Dict[str, tuple[float, float]] = {}


def get_base_url() -> str:
    return os.getenv("COINGECKO_BASE_URL", "https://api.coingecko.com/api/v3")


def get_api_key() -> Optional[str]:
    return os.getenv("COINGECKO_API_KEY") or None


def fetch_price(coingecko_id: str) -> Optional[float]:
    """
    Fetch current USD price for a CoinGecko id. Uses 5-min cache.
    Writes to token_prices table when token_address is provided via fetch_and_cache.
    """
    now = time.time()
    if coingecko_id in _price_cache:
        price, fetched_at = _price_cache[coingecko_id]
        if now - fetched_at < CACHE_TTL:
            return price
    url = f"{get_base_url()}/simple/price"
    params = {"ids": coingecko_id, "vs_currencies": "usd"}
    headers = {}
    api_key = get_api_key()
    if api_key:
        headers["x-cg-demo-api-key" if "demo" in api_key.lower() else "x-cg-pro-api-key"] = api_key
    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.get(url, params=params, headers=headers or None)
            r.raise_for_status()
            data = r.json()
        price = data.get(coingecko_id, {}).get("usd")
        if price is not None:
            _price_cache[coingecko_id] = (float(price), now)
            return float(price)
    except Exception:
        pass
    # Fallback to last known from cache even if stale
    if coingecko_id in _price_cache:
        return _price_cache[coingecko_id][0]
    return None


def fetch_and_cache_for_token(token_address: str, coingecko_id: str) -> Optional[float]:
    """
    Fetch price, update cache, and upsert into token_prices table.
    """
    price = fetch_price(coingecko_id)
    if price is not None:
        from datetime import datetime, timezone
        db_queries.upsert_token_price(
            token_address=token_address.lower(),
            coingecko_id=coingecko_id,
            price_usd=price,
            fetched_at=datetime.now(timezone.utc),
            source="coingecko",
        )
    return price


def get_cached_price(coingecko_id: str) -> Optional[float]:
    """Return cached price if still valid, else None."""
    if coingecko_id not in _price_cache:
        return None
    price, fetched_at = _price_cache[coingecko_id]
    if time.time() - fetched_at >= CACHE_TTL:
        return None
    return price
