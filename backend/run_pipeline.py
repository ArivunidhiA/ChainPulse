#!/usr/bin/env python3
"""
Run the full ChainPulse data pipeline:
  1. Index recent blockchain events (Uniswap swaps + ERC-20 transfers)
  2. Run Python analysis scripts (whale segmentation, volume anomaly, token flows, protocol health)

Usage:
  python run_pipeline.py            # run everything
  python run_pipeline.py index      # only indexer
  python run_pipeline.py analyze    # only analysis
"""
import os
import sys

# Load .env from the backend directory
from pathlib import Path
from dotenv import load_dotenv

backend_dir = Path(__file__).parent
load_dotenv(backend_dir / ".env")


def run_indexer():
    print("[Pipeline] Running indexer (recent blocks)...")
    from indexer.evm_indexer import run_indexer_once
    try:
        run_indexer_once()
        print("[Pipeline] Indexer pass complete.")
    except Exception as e:
        print(f"[Pipeline] Indexer error: {e}")
        import traceback
        traceback.print_exc()


def run_analysis():
    print("[Pipeline] Running analysis scripts...")
    scripts = [
        ("Whale Segmentation", "analysis.whale_segmentation", "run"),
        ("Volume Anomaly", "analysis.volume_anomaly", "run"),
        ("Token Flow", "analysis.token_flow_analysis", "run"),
        ("Protocol Health", "analysis.protocol_health", "run"),
    ]
    for name, module_path, func_name in scripts:
        try:
            print(f"  -> {name}...")
            mod = __import__(module_path, fromlist=[func_name])
            getattr(mod, func_name)()
            print(f"  -> {name} done.")
        except Exception as e:
            print(f"  -> {name} error: {e}")
            import traceback
            traceback.print_exc()
    print("[Pipeline] Analysis complete.")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    passes = int(sys.argv[2]) if len(sys.argv) > 2 else 25
    if mode in ("all", "index"):
        # Run indexer multiple passes — Alchemy free tier = 10 blocks per pass
        for i in range(passes):
            print(f"\n[Pipeline] Indexer pass {i+1}/{passes}")
            run_indexer()
    if mode in ("all", "analyze"):
        run_analysis()
    print("\n[Pipeline] All done!")


if __name__ == "__main__":
    main()
