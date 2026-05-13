"""
Calls the Gemini AI Studio API with Google Search grounding to:
1. Fetch the latest material news, corporate actions, and announcements per ticker
2. Combine that with pre-computed technicals
3. Return a polished HTML digest ready to email
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

from google import genai
from google.genai import types

log = logging.getLogger(__name__)

MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")


SYSTEM_PROMPT = """You are a financial research assistant producing a daily \
stock digest email for one private user. Be terse, factual, and skeptical of \
hype. Skip routine noise (analyst price-target tweaks, generic market \
commentary, social media chatter). Surface only what would change a thoughtful \
investor's view of the company.

For each ticker, search the web for material developments in the last 24 hours:
- Corporate actions (dividends, splits, buybacks, M&A)
- Earnings, guidance changes, pre-announcements
- Material business announcements (major contracts, regulatory actions, leadership changes)
- Scheduled events (earnings dates, investor days, AGMs)
- Filings (10-K/10-Q for US, SEBI/exchange filings for India)

Combine that with the technical indicators provided. Produce a single HTML email body.

OUTPUT FORMAT — return ONLY raw HTML (no markdown, no code fences). Use this structure:

<div style="font-family: -apple-system, system-ui, sans-serif; max-width: 700px;">
  <h1 style="font-size:20px;">{Market Name} Digest — {Date}</h1>
  <p style="color:#666;font-size:13px;">Generated automatically. Not investment advice.</p>

  <!-- For each ticker: -->
  <div style="border-top:1px solid #eee;padding:16px 0;">
    <h2 style="font-size:16px;margin:0 0 4px 0;">{TICKER} — {Company Name}</h2>
    <div style="color:#666;font-size:13px;margin-bottom:8px;">
      ${price} ({change_pct}%) · RSI {rsi} · Trend: {one_line_trend_summary}
    </div>
    <h3 style="font-size:14px;margin:12px 0 4px 0;">News & Events</h3>
    <ul style="margin:0;padding-left:20px;font-size:14px;line-height:1.5;">
      <li>{Concise headline} — {1-line context why it matters}. <a href="{url}">source</a></li>
    </ul>
    <h3 style="font-size:14px;margin:12px 0 4px 0;">Technical Read</h3>
    <p style="font-size:14px;line-height:1.5;margin:0;">{2-3 sentence interpretation of the technicals}</p>
  </div>
</div>

If a ticker has no material news, write: <li style="color:#999;">No material news in last 24h.</li>

Keep the whole email scannable in under 60 seconds. Quality over quantity."""


def build_user_message(market_name: str, technicals: list[dict[str, Any]]) -> str:
    return (
        f"Generate the {market_name} digest for today.\n\n"
        f"Tickers and pre-computed technicals (use these — do not recompute):\n\n"
        f"```json\n{json.dumps(technicals, indent=2, default=str)}\n```\n\n"
        f"Search the web for material news on each ticker from the last 24 hours, "
        f"then produce the HTML digest per the system prompt format."
    )


def generate_digest(market_name: str, technicals: list[dict[str, Any]]) -> str:
    """Call Gemini with Google Search grounding and return the HTML email body."""
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    response = client.models.generate_content(
        model=MODEL,
        contents=build_user_message(market_name, technicals),
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=[types.Tool(google_search=types.GoogleSearch())],
            max_output_tokens=8000,
        ),
    )

    # response.text is Optional[str] — None when blocked by safety filters,
    # quota exceeded, or the model returned only non-text parts.
    if not response.text:
        finish = (
            response.candidates[0].finish_reason
            if response.candidates
            else "unknown"
        )
        raise RuntimeError(f"Gemini returned no text content (finish_reason={finish})")

    html = response.text.strip()

    # Defensive cleanup — if the model wraps in code fences despite instructions.
    if html.startswith("```"):
        html = html.split("\n", 1)[1] if "\n" in html else html
        html = html.rsplit("```", 1)[0]
    return html.strip()