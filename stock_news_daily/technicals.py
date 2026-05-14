"""
Fetches technical analysis for a list of tickers using fintools-mcp internals
as a regular Python library (not as an MCP server).

We import the underlying analysis functions directly. This avoids the overhead
of running an MCP server in a cron job.
"""

from __future__ import annotations

import logging
from typing import Any

from fintools_mcp import data as ft_data
from fintools_mcp.indicators import rsi, macd, atr, ema
from fintools_mcp.analysis import position_sizer

log = logging.getLogger(__name__)


def _safe(fn, *args, **kwargs):
    """Run a function and return None on any error, with a logged warning.

    Technical indicators occasionally fail for illiquid tickers, fresh IPOs,
    or when Yahoo Finance returns incomplete history. We don't want one bad
    ticker to kill the whole digest.
    """
    try:
        return fn(*args, **kwargs)
    except Exception as e:
        log.warning("indicator failed: %s(%s) -> %s", fn.__name__, args, e)
        return None


def get_technicals(ticker: str) -> dict[str, Any]:
    """Return a dict of technical indicators for one ticker.

    Returns whatever computed successfully — missing fields are simply absent.
    The Claude prompt is written to handle partial data gracefully.
    """
    result: dict[str, Any] = {"ticker": ticker}

    # Pull historical price data once and reuse for every indicator.
    bars = _safe(ft_data.fetch_bars, ticker, period="1y")
    if not bars:
        result["error"] = "no price history available"
        return result

    quote = _safe(ft_data.fetch_quote, ticker)
    if quote:
        price = quote.get("price")
        prev_close = quote.get("previous_close")
        change_pct = (
            round((price - prev_close) / prev_close * 100, 2)
            if price and prev_close
            else None
        )
        result["quote"] = {
            "price": price,
            "change_pct": change_pct,
            "volume": quote.get("volume"),
            "week_52_high": quote.get("fifty_two_week_high"),
            "week_52_low": quote.get("fifty_two_week_low"),
            "market_cap": quote.get("market_cap"),
        }

    closes = [b.close for b in bars]
    highs = [b.high for b in bars]
    lows = [b.low for b in bars]

    result["rsi_14"] = _safe(rsi.compute_rsi, closes, period=14)
    result["macd"] = _safe(macd.compute_macd, closes)
    result["ema_9"] = _safe(ema.compute_ema, closes, period=9)
    result["ema_21"] = _safe(ema.compute_ema, closes, period=21)
    result["ema_50"] = _safe(ema.compute_ema, closes, period=50)
    result["ema_200"] = _safe(ema.compute_ema, closes, period=200)
    result["atr_14"] = _safe(atr.compute_atr, highs, lows, closes, period=14)

    return result


def get_technicals_for_list(tickers: list[str]) -> list[dict[str, Any]]:
    """Fetch technicals for every ticker in the list. Best-effort."""
    return [get_technicals(t) for t in tickers]