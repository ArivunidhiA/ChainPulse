"""
EVM indexer: fetch Uniswap V3 Swap and ERC-20 Transfer events, decode, enrich, persist.
"""
from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List

from web3 import Web3

from indexer.block_tracker import get_last_block, set_last_block
from indexer.decoder import (
    KNOWN_TOKENS,
    ERC20Decoder,
    UniswapDecoder,
)
from indexer.event_classifier import classify_swap_size, filter_dust_transfer
from indexer.price_service import fetch_and_cache_for_token, get_cached_price
from db.queries import insert_raw_events, insert_raw_swaps, insert_raw_transfers

# Alchemy RPC
def get_web3() -> Web3:
    url = os.getenv("ALCHEMY_API_URL", "").strip()
    if not url:
        url = "https://eth-mainnet.g.alchemy.com/v2/demo"
    return Web3(Web3.HTTPProvider(url, request_kwargs={"timeout": 30}))

# Contract config: Uniswap V3 pools (address -> token0, token1) and ERC-20 list
UNISWAP_V3_POOLS: List[Dict[str, str]] = [
    {
        "address": "0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8",
        "token0": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # USDC
        "token1": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH
    },
]
ERC20_CONTRACTS: List[str] = [
    "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # USDC
    "0xdAC17F958D2ee523a2206206994597C13D831ec7",  # USDT
    "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",  # WBTC
    "0x6B175474E89094C44Da98b954EedeAC495271d0F",  # DAI
    "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH
]

BATCH_SIZE = 50
BLOCK_CHUNK = 9  # Alchemy free tier: max 10 blocks per eth_getLogs
# How many blocks behind head to start if no checkpoint exists
DEFAULT_LOOKBACK = 200


def _block_timestamp(web3: Web3, block_number: int) -> datetime:
    try:
        block = web3.eth.get_block(block_number)
        ts = block.get("timestamp")
        if isinstance(ts, (int, float)):
            return datetime.fromtimestamp(ts, tz=timezone.utc)
    except Exception:
        pass
    return datetime.now(timezone.utc)


def _swap_usd_value(amount_in: Decimal, token_in_address: str) -> Decimal | None:
    """Estimate swap USD from token-in amount and cached price."""
    addr = token_in_address.lower()
    meta = KNOWN_TOKENS.get(token_in_address) or KNOWN_TOKENS.get(addr)
    if not meta:
        return None
    cg_id = meta.get("coingecko_id")
    if not cg_id:
        return None
    price = get_cached_price(cg_id)
    if price is None:
        price = fetch_and_cache_for_token(addr, cg_id)
    if price is None:
        return None
    return amount_in * Decimal(str(price))


def _run_indexer_pass() -> None:
    w3 = get_web3()
    if not w3.is_connected():
        return

    # Index Uniswap V3 Swap events
    swap_abi = [
        {
            "anonymous": False,
            "inputs": [
                {"indexed": True, "name": "sender", "type": "address"},
                {"indexed": True, "name": "recipient", "type": "address"},
                {"indexed": False, "name": "amount0", "type": "int256"},
                {"indexed": False, "name": "amount1", "type": "int256"},
                {"indexed": False, "name": "sqrtPriceX96", "type": "uint160"},
                {"indexed": False, "name": "liquidity", "type": "int128"},
                {"indexed": False, "name": "tick", "type": "int24"},
            ],
            "name": "Swap",
            "type": "event",
        }
    ]
    transfer_abi = [
        {
            "anonymous": False,
            "inputs": [
                {"indexed": True, "name": "from", "type": "address"},
                {"indexed": True, "name": "to", "type": "address"},
                {"indexed": False, "name": "value", "type": "uint256"},
            ],
            "name": "Transfer",
            "type": "event",
        }
    ]

    for pool in UNISWAP_V3_POOLS:
        addr = pool["address"].lower()
        end_block = w3.eth.block_number
        start = get_last_block(addr)
        if start is None:
            start = max(0, end_block - DEFAULT_LOOKBACK)
        if start >= end_block:
            continue
        decoder = UniswapDecoder(pool["address"], pool["token0"], pool["token1"])
        to_block = min(start + BLOCK_CHUNK, end_block)
        try:
            contract = w3.eth.contract(address=Web3.to_checksum_address(pool["address"]), abi=swap_abi)
            logs = contract.events.Swap.get_logs(fromBlock=start + 1, toBlock=to_block)
        except Exception:
            logs = []
        raw_events_batch: List[Dict] = []
        swaps_batch: List[Dict] = []
        for log in logs:
            block_ts = _block_timestamp(w3, log["blockNumber"])
            decoded = decoder.decode(dict(log), block_ts)
            if not decoded:
                continue
            # Enrich with USD and size_bucket
            amount_in = decoded.get("amount1") if decoded.get("amount0", 0) < 0 else decoded.get("amount0")
            token_in = decoded.get("token1_address") if decoded.get("amount0", 0) < 0 else decoded.get("token0_address")
            usd = _swap_usd_value(Decimal(str(amount_in)), token_in)
            decoded["usd_value"] = float(usd) if usd is not None else None
            decoded["size_bucket"] = classify_swap_size(usd)
            # Raw event
            raw_events_batch.append({
                "block_number": decoded["block_number"],
                "tx_hash": decoded["tx_hash"],
                "log_index": decoded["log_index"],
                "contract_address": addr,
                "event_name": "Swap",
                "event_params": {k: str(v) for k, v in decoded.items()},
                "event_timestamp": decoded["event_timestamp"],
            })
            swaps_batch.append(decoded)
        for i in range(0, len(raw_events_batch), BATCH_SIZE):
            insert_raw_events(raw_events_batch[i : i + BATCH_SIZE])
        for i in range(0, len(swaps_batch), BATCH_SIZE):
            insert_raw_swaps(swaps_batch[i : i + BATCH_SIZE])
        set_last_block(addr, to_block)
        time.sleep(0.2)  # rate limit

    # Index ERC-20 Transfer events
    for token_address in ERC20_CONTRACTS:
        addr = token_address.lower()
        end_block = w3.eth.block_number
        start = get_last_block(addr)
        if start is None:
            start = max(0, end_block - DEFAULT_LOOKBACK)
        if start >= end_block:
            continue
        decoder = ERC20Decoder(token_address)
        to_block = min(start + BLOCK_CHUNK, end_block)
        try:
            contract = w3.eth.contract(address=Web3.to_checksum_address(token_address), abi=transfer_abi)
            logs = contract.events.Transfer.get_logs(fromBlock=start + 1, toBlock=to_block)
        except Exception:
            logs = []
        raw_events_batch = []
        transfers_batch = []
        meta = KNOWN_TOKENS.get(token_address) or KNOWN_TOKENS.get(addr) or {}
        cg_id = meta.get("coingecko_id")
        for log in logs:
            block_ts = _block_timestamp(w3, log["blockNumber"])
            decoded = decoder.decode(dict(log), block_ts)
            if not decoded:
                continue
            amount = decoded.get("amount")
            usd = None
            if cg_id and amount is not None:
                price = get_cached_price(cg_id) or (fetch_and_cache_for_token(addr, cg_id))
                if price is not None:
                    usd = Decimal(str(amount)) * Decimal(str(price))
            if not filter_dust_transfer(usd):
                continue
            decoded["usd_value"] = float(usd) if usd is not None else None
            decoded["direction"] = None  # optional: pass tracked_wallets
            decoded["is_exchange"] = False
            raw_events_batch.append({
                "block_number": decoded["block_number"],
                "tx_hash": decoded["tx_hash"],
                "log_index": decoded["log_index"],
                "contract_address": addr,
                "event_name": "Transfer",
                "event_params": {k: str(v) for k, v in decoded.items()},
                "event_timestamp": decoded["event_timestamp"],
            })
            transfers_batch.append(decoded)
        for i in range(0, len(raw_events_batch), BATCH_SIZE):
            insert_raw_events(raw_events_batch[i : i + BATCH_SIZE])
        for i in range(0, len(transfers_batch), BATCH_SIZE):
            insert_raw_transfers(transfers_batch[i : i + BATCH_SIZE])
        set_last_block(addr, to_block)
        time.sleep(0.2)


def run_indexer_once() -> None:
    """Single indexer pass (called by scheduler or manually)."""
    _run_indexer_pass()
