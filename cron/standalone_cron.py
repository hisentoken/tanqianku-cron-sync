#!/usr/bin/env python3
"""
Standalone cron scheduler - runs independently of the gateway.

Usage:
    python3 standalone_cron.py          # Run once
    python3 standalone_cron.py --daemon # Run forever (daemon mode)
    hermes cron standalone-cron          # Via hermes CLI

Ticks the cron scheduler every 60 seconds using a file lock so multiple
processes don't step on each other.
"""

import argparse
import logging
import os
import sys
import time
import threading
from pathlib import Path

# Add hermes-agent to path
AGENT_ROOT = Path(__file__).parent.parent / "hermes-agent"
sys.path.insert(0, str(AGENT_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [cron] %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("/home/tanqianku/.hermes/cron/cron_daemon.log")],
)
logger = logging.getLogger("cron.standalone")


def tick_once():
    """Run one scheduler tick. Returns True if a job ran, False otherwise."""
    try:
        from cron.scheduler import tick
        from hermes_time import now as _now

        logger.debug("Tick at %s", _now())
        # tick returns number of jobs that ran
        result = tick(verbose=False)
        if result and result > 0:
            logger.info("Jobs run: %d", result)
        return result
    except Exception as e:
        logger.error("Tick error: %s", e)
        return None


def run_daemon(interval: int = 60):
    """Run the cron scheduler forever in daemon mode."""
    import fcntl

    lock_file = Path("/home/tanqianku/.hermes/cron/.standalone.lock")
    lock_file.parent.mkdir(parents=True, exist_ok=True)

    fd = os.open(str(lock_file), os.O_RDWR | os.O_CREAT, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        logger.error("Another cron daemon is already running. Exiting.")
        sys.exit(1)

    logger.info("Standalone cron daemon started (interval=%ds PID=%d)", interval, os.getpid())

    while True:
        tick_once()
        # Use a wait with wakeup to allow clean shutdown
        _stop_event = getattr(threading, "_stop_event", None)
        # Simple sleep - can be interrupted via signal
        time.sleep(interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Standalone Hermes cron scheduler")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    parser.add_argument("--interval", type=int, default=60, help="Tick interval in seconds")
    args = parser.parse_args()

    if args.daemon:
        run_daemon(interval=args.interval)
    else:
        tick_once()
