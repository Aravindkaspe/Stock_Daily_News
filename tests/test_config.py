"""
Smoke tests for config/stocks.json.
These run without any API keys — just validate the config file structure.
Run with: pytest tests/
"""

import json
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "stocks.json"


def test_config_is_valid_json():
    assert CONFIG_PATH.exists(), "config/stocks.json not found"
    data = json.loads(CONFIG_PATH.read_text())
    assert isinstance(data, dict)


def test_config_has_required_markets():
    data = json.loads(CONFIG_PATH.read_text())
    for market in ("us", "india"):
        assert market in data, f"Missing '{market}' key in stocks.json"
        assert "tickers" in data[market], f"Missing 'tickers' in {market} config"
        assert "market_name" in data[market], f"Missing 'market_name' in {market} config"
        assert len(data[market]["tickers"]) > 0, f"No tickers listed for {market}"


def test_india_tickers_have_ns_suffix():
    data = json.loads(CONFIG_PATH.read_text())
    for ticker in data["india"]["tickers"]:
        assert ticker.endswith(".NS"), (
            f"Indian ticker '{ticker}' must end with .NS for yfinance compatibility"
        )
