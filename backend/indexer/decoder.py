"""
ABI event decoder and registry for Uniswap V3 Swap and ERC-20 Transfer.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, List, Optional

# Uniswap V3 Pool Swap event
UNISWAP_V3_SWAP_ABI = [
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

# ERC-20 Transfer event
ERC20_TRANSFER_ABI = [
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

# Token metadata: address -> decimals (and optional coingecko_id for price_service)
KNOWN_TOKENS: Dict[str, Dict[str, Any]] = {
    "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48": {"symbol": "USDC", "decimals": 6, "coingecko_id": "usd-coin"},
    "0xdAC17F958D2ee523a2206206994597C13D831ec7": {"symbol": "USDT", "decimals": 6, "coingecko_id": "tether"},
    "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599": {"symbol": "WBTC", "decimals": 8, "coingecko_id": "wrapped-bitcoin"},
    "0x6B175474E89094C44Da98b954EedeAC495271d0F": {"symbol": "DAI", "decimals": 18, "coingecko_id": "dai"},
    "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2": {"symbol": "WETH", "decimals": 18, "coingecko_id": "weth"},
}


def _to_decimal(value: Any) -> Decimal:
    if isinstance(value, Decimal):
        return value
    if hasattr(value, "__int__"):
        return Decimal(int(value))
    return Decimal(str(value))


def _human_amount(raw: Any, decimals: int) -> Decimal:
    raw_d = _to_decimal(raw)
    if raw_d < 0:
        raw_d = -raw_d
    return raw_d / (10 ** decimals)


def _addr(a: Any) -> str:
    if a is None:
        return ""
    if isinstance(a, str):
        return a.lower().strip()
    return str(a).lower()


class UniswapDecoder:
    """Decode Uniswap V3 Swap events into structured records."""

    def __init__(self, pool_address: str, token0_address: str, token1_address: str):
        self.pool_address = pool_address.lower()
        self.token0_address = token0_address.lower()
        self.token1_address = token1_address.lower()
        self.token0_decimals = KNOWN_TOKENS.get(token0_address, {}).get("decimals", 18)
        self.token1_decimals = KNOWN_TOKENS.get(token1_address, {}).get("decimals", 18)

    def decode(self, log: Dict[str, Any], block_timestamp: Any) -> Optional[Dict[str, Any]]:
        args = log.get("args") or {}
        sender = args.get("sender") or args.get("sender_address")
        recipient = args.get("recipient") or args.get("recipient_address")
        amount0 = args.get("amount0")
        amount1 = args.get("amount1")
        if sender is None or amount0 is None or amount1 is None:
            return None
        amount0_d = _to_decimal(amount0)
        amount1_d = _to_decimal(amount1)
        amt0_human = _human_amount(amount0_d, self.token0_decimals)
        amt1_human = _human_amount(amount1_d, self.token1_decimals)
        # Swap direction: negative amount = token out, positive = token in
        if amount0_d < 0 and amount1_d > 0:
            token_in_addr, token_out_addr = self.token1_address, self.token0_address
            amount_in, amount_out = amt1_human, -amt0_human
        elif amount0_d > 0 and amount1_d < 0:
            token_in_addr, token_out_addr = self.token0_address, self.token1_address
            amount_in, amount_out = amt0_human, -amt1_human
        else:
            return None
        ts = block_timestamp
        if hasattr(ts, "isoformat"):
            event_ts = ts
        else:
            from datetime import datetime
            event_ts = datetime.utcfromtimestamp(ts) if isinstance(ts, (int, float)) else ts
        tx_hash = log.get("transactionHash")
        tx_hex = tx_hash.hex() if hasattr(tx_hash, "hex") else str(tx_hash)
        return {
            "block_number": log.get("blockNumber"),
            "tx_hash": tx_hex,
            "log_index": log.get("logIndex", 0),
            "pool_address": self.pool_address,
            "sender_address": _addr(sender),
            "recipient_address": _addr(recipient or sender),
            "token0_address": self.token0_address,
            "token1_address": self.token1_address,
            "amount0": amt0_human if amount0_d >= 0 else -amt0_human,
            "amount1": amt1_human if amount1_d >= 0 else -amt1_human,
            "sqrt_price_x96": args.get("sqrtPriceX96"),
            "liquidity": args.get("liquidity"),
            "tick": args.get("tick"),
            "event_timestamp": event_ts,
        }


class ERC20Decoder:
    """Decode ERC-20 Transfer events."""

    def __init__(self, token_address: str):
        self.token_address = _addr(token_address)
        meta = KNOWN_TOKENS.get(token_address) or KNOWN_TOKENS.get(self.token_address) or {}
        self.decimals = meta.get("decimals", 18)

    def decode(self, log: Dict[str, Any], block_timestamp: Any) -> Optional[Dict[str, Any]]:
        args = log.get("args") or {}
        from_addr = args.get("from") or args.get("from_address")
        to_addr = args.get("to") or args.get("to_address")
        value = args.get("value")
        if value is None:
            return None
        amount_raw = _to_decimal(value)
        amount = _human_amount(amount_raw, self.decimals)
        ts = block_timestamp
        if hasattr(ts, "isoformat"):
            event_ts = ts
        else:
            from datetime import datetime
            event_ts = datetime.utcfromtimestamp(ts) if isinstance(ts, (int, float)) else ts
        tx_hash = log.get("transactionHash")
        tx_hex = tx_hash.hex() if hasattr(tx_hash, "hex") else str(tx_hash)
        return {
            "block_number": log.get("blockNumber"),
            "tx_hash": tx_hex,
            "log_index": log.get("logIndex", 0),
            "token_address": self.token_address,
            "from_address": _addr(from_addr),
            "to_address": _addr(to_addr),
            "amount_raw": amount_raw,
            "amount": amount,
            "event_timestamp": event_ts,
        }


# Registry: contract_address -> {"events": [...], "decoder": DecoderInstance}
# Decoder instances are created per contract in evm_indexer.
ABI_REGISTRY = {
    "uniswap_v3_pool": {"events": ["Swap"], "decoder_cls": UniswapDecoder},
    "erc20": {"events": ["Transfer"], "decoder_cls": ERC20Decoder},
}