"""
Event classification: swap/transfer/mint/burn and size tiers (whale/large/standard).
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, Optional

# USD thresholds
WHALE_MIN_USD = Decimal("50000")
LARGE_MIN_USD = Decimal("10000")
# Transfer dust filter
MIN_TRANSFER_USD = Decimal("1000")


def classify_swap_size(amount_usd: Optional[Decimal]) -> str:
    """Classify swap into whale / large / standard by USD size."""
    if amount_usd is None or amount_usd <= 0:
        return "standard"
    if amount_usd >= WHALE_MIN_USD:
        return "whale"
    if amount_usd >= LARGE_MIN_USD:
        return "large"
    return "standard"


def classify_transfer_direction(from_address: str, to_address: str, tracked_wallets: set) -> Optional[str]:
    """
    Tag direction relative to tracked wallets: 'in' = into tracked, 'out' = from tracked.
    If neither is tracked, returns None (caller may still persist with direction null).
    """
    from_lower = (from_address or "").lower()
    to_lower = (to_address or "").lower()
    tracked = {w.lower() for w in tracked_wallets}
    if to_lower in tracked and from_lower not in tracked:
        return "in"
    if from_lower in tracked and to_lower not in tracked:
        return "out"
    return None


def is_whale_swap(amount_usd: Optional[Decimal]) -> bool:
    return amount_usd is not None and amount_usd >= WHALE_MIN_USD


def filter_dust_transfer(amount_usd: Optional[Decimal], min_usd: Decimal = MIN_TRANSFER_USD) -> bool:
    """Return True if transfer should be included (above dust)."""
    if amount_usd is None:
        return False
    return amount_usd >= min_usd
