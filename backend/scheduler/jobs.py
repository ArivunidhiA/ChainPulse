"""
APScheduler jobs: indexer every 15s, dbt run every 30min, analysis every hour.
"""
from __future__ import annotations

import os
import subprocess
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)


def run_indexer():
    try:
        from indexer.evm_indexer import run_indexer_once
        run_indexer_once()
    except Exception as e:
        logger.exception("Indexer job failed: %s", e)


def run_dbt():
    try:
        dbt_dir = os.getenv("DBT_PROFILES_DIR", "").replace("/dbt_chainpulse", "")
        if not dbt_dir:
            dbt_dir = os.path.join(os.path.dirname(__file__), "..", "..", "dbt_chainpulse")
        project_dir = os.path.abspath(dbt_dir)
        if not os.path.isdir(project_dir):
            project_dir = os.path.join(os.path.dirname(__file__), "..", "..", "dbt_chainpulse")
        env = os.environ.copy()
        env["DBT_PROFILES_DIR"] = project_dir
        subprocess.run(["dbt", "run", "--project-dir", project_dir], env=env, capture_output=True, timeout=600, cwd=project_dir)
    except Exception as e:
        logger.exception("dbt run failed: %s", e)


def run_analysis():
    try:
        from analysis.whale_segmentation import run as run_whale
        from analysis.volume_anomaly import run as run_anomaly
        from analysis.token_flow_analysis import run as run_flow
        from analysis.protocol_health import run as run_health
        run_whale()
        run_anomaly()
        run_flow()
        run_health()
    except Exception as e:
        logger.exception("Analysis job failed: %s", e)


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_indexer, IntervalTrigger(seconds=15), id="indexer")
    scheduler.add_job(run_dbt, IntervalTrigger(minutes=30), id="dbt")
    scheduler.add_job(run_analysis, IntervalTrigger(hours=1), id="analysis")
    scheduler.start()
    return scheduler
