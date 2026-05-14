"""
Entrypoint for the daily stock digest.

Usage:
    python -m stock_news_daily.run --market us
    python -m stock_news_daily.run --market india
    python -m stock_news_daily.run    # auto-detect from current CST hour

Run twice daily via GitHub Actions:
    6am CST  -> --market us
    7pm CST  -> --market india
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

import pytz
from dotenv import load_dotenv

load_dotenv()

from stock_news_daily.digest import generate_digest
from stock_news_daily.mailer import send_digest
from stock_news_daily.technicals import get_technicals_for_list

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("digest")

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "stocks.json"


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text())


def auto_detect_market() -> str:
    """Pick US or India based on current CST hour. Used when no flag is passed."""
    cst_hour = datetime.now(pytz.timezone("America/Chicago")).hour
    # Morning run (4–10am CST) -> US digest. Evening (16–22) -> India digest.
    return "us" if 4 <= cst_hour < 12 else "india"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--market", choices=["us", "india"], default=None)
    parser.add_argument("--dry-run", action="store_true", help="Print HTML, don't email")
    args = parser.parse_args()

    market = args.market or auto_detect_market()
    log.info("running digest for market=%s", market)

    config = load_config()
    market_cfg = config[market]
    tickers = market_cfg["tickers"]
    market_name = market_cfg["market_name"]
    log.info("tickers: %s", tickers)

    log.info("fetching technicals…")
    technicals = get_technicals_for_list(tickers)

    log.info("generating digest via Claude (this is the slow step — web search runs here)…")
    html = generate_digest(market_name, technicals)

    today = datetime.now(pytz.timezone("America/Chicago")).strftime("%b %d, %Y")
    subject = f"{market_name} Digest — {today}"

    if args.dry_run:
        print(html)
        return 0

    send_digest(subject, html)
    log.info("done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
