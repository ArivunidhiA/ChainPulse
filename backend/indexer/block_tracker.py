"""
Block checkpoint persistence for indexer resume and backfill.
"""
from __future__ import annotations

from db import queries as db_queries


def get_last_block(contract_address: str) -> int | None:
    """Return last processed block for this contract, or None."""
    return db_queries.get_block_checkpoint(contract_address)


def set_last_block(contract_address: str, block_number: int) -> None:
    """Persist last processed block for this contract."""
    db_queries.upsert_block_checkpoint(contract_address, block_number)
