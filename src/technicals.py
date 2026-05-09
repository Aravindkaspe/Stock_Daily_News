"""
Fetches technical analysis for a list of tickers using fintools-mcp internals
as a regular Python library (not as an MCP server).

We import the underlying analysis functions directly. This avoids the overhead
of running an MCP server in a cron job — MCPs are designed for interactive use.
"""

from __future__ import annotations

import logging
from typing import Any

# fintools-mcp exposes its analysis functions in submodules. We use these
# directly rather than going through the MCP server protocol.
from fintools_mcp import data as ft_data
from fintools_mcp.indicators import rsi, macd, atr, ema
from fintools_mcp.analysis import position_sizer  # noqa: F401  (kept for future use)

log = logging.getLogger(__name__)


def _safe(fn, *args, **kwargs):
    """Run a function and return None on any error, with a logged warning.

    Technical indicators occasionally fail for illiquid tickers, fresh IPOs,
    or when Yahoo Finance returns incomplete history. We don't want one bad
    ticker to kill the whole digest.
    """
    try:
        return fn(*args, **kwargs)
    except Exception as e:  # noqa: BLE001
        log.warning("indicator failed: %s(%s) -> %s", fn.__name__, args, e)
        return None


def get_technicals(ticker: str) -> dict[str, Any]:
    """Return a dict of technical indicators for one ticker.

    Returns whatever computed successfully — missing fields are simply absent.
    The Claude prompt is written to handle partial data gracefully.
    """
    result: dict[str, Any] = {"ticker": ticker}

    # Pull historical price data once and reuse for every indicator.
    history = _safe(ft_data.get_history, ticker, period="1y")
    if history is None or len(history) == 0:
        result["error"] = "no price history available"
        return result

    quote = _safe(ft_data.get_quote, ticker)
    if quote:
        result["quote"] = {
            "price": quote.get("price"),
            "change_pct": quote.get("change_pct"),
            "volume": quote.get("volume"),
            "week_52_high": quote.get("week_52_high"),
            "week_52_low": quote.get("week_52_low"),
            "market_cap": quote.get("market_cap"),
        }

    closes = history["Close"].tolist() if hasattr(history, "__getitem__") else None
    highs = history["High"].tolist() if closes else None
    lows = history["Low"].tolist() if closes else None

    if closes:
        result["rsi_14"] = _safe(rsi.calculate, closes, period=14)
        result["macd"] = _safe(macd.calculate, closes)
        result["ema_9"] = _safe(ema.calculate, closes, period=9)
        result["ema_21"] = _safe(ema.calculate, closes, period=21)
        result["ema_50"] = _safe(ema.calculate, closes, period=50)
        result["ema_200"] = _safe(ema.calculate, closes, period=200)

    if closes and highs and lows:
        result["atr_14"] = _safe(atr.calculate, highs, lows, closes, period=14)

    return result


def get_technicals_for_list(tickers: list[str]) -> list[dict[str, Any]]:
    """Fetch technicals for every ticker in the list. Best-effort."""
    return [get_technicals(t) for t in tickers]
