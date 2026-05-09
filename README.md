# Stock Digest

Twice-daily LLM-curated stock digest emailed to you. Combines technical analysis
(via [fintools-mcp](https://github.com/slimbiggins007/fintools-mcp)) with web-searched
news, corporate actions, and announcements, summarized by Claude.

- **6am CST weekdays** — US market digest (NYSE/NASDAQ tickers)
- **7pm CST weekdays** — India market digest (NSE tickers)

Runs on free GitHub Actions. Costs ~$5–$15/month in Claude API + web search calls
for ~10 tickers per market. No news API subscription required.

## Setup

### 1. Fork or copy this repo to your own GitHub.

### 2. Get API keys

- **Anthropic API key** → https://console.anthropic.com/ → Settings → API Keys
- **Resend API key** → https://resend.com/ (free tier, 3,000 emails/month)
  - You'll need to verify a domain, OR use Resend's `onboarding@resend.dev`
    sender for testing (only sends to your own verified email)

### 3. Add GitHub secrets

In your repo: **Settings → Secrets and variables → Actions → New repository secret**

| Secret              | Value                                              |
| ------------------- | -------------------------------------------------- |
| `ANTHROPIC_API_KEY` | `sk-ant-...`                                       |
| `RESEND_API_KEY`    | `re_...`                                           |
| `EMAIL_FROM`        | `Digest <digest@yourdomain.com>` or sandbox sender |
| `EMAIL_TO`          | your email                                         |

Optional repo **variable** (not secret): `CLAUDE_MODEL` — defaults to
`claude-haiku-4-5-20251001`. Set to `claude-sonnet-4-6` if you want higher
quality at ~3x the cost.

### 4. Edit your watchlist

Open `config/stocks.json`. Add/remove tickers anytime — commit and push, the
next scheduled run picks up the change. Indian tickers need `.NS` suffix
(e.g. `RELIANCE.NS`) so yfinance recognizes them.

### 5. Trigger a test run

Go to **Actions → Stock Digest → Run workflow** and pick a market. You should
get an email within ~2 minutes.

## Local testing

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
export RESEND_API_KEY=re_...
export EMAIL_FROM="Digest <digest@yourdomain.com>"
export EMAIL_TO="you@example.com"

# Print the HTML without sending an email
python -m src.run --market us --dry-run

# Send for real
python -m src.run --market us
```

## Cost estimate

For 10 tickers × 2 runs/day × 22 weekdays:

| Item                                             | Monthly        |
| ------------------------------------------------ | -------------- |
| GitHub Actions (free tier covers this)           | $0             |
| Anthropic API — Haiku 4.5, ~5K in / 3K out       | ~$2–4          |
| Web search tool calls — ~3–5 searches per ticker | ~$5–10         |
| Resend (free tier covers <3,000/month)           | $0             |
| **Total**                                        | **~$7–14**     |

Switch `CLAUDE_MODEL` to Sonnet 4.6 for ~$25–40/month if Haiku quality is insufficient.

## Customization

- **Prompt tuning** — `src/digest.py`, `SYSTEM_PROMPT` constant. This is where
  you'll spend time iterating on output quality.
- **Search budget** — `MAX_SEARCHES_PER_RUN` env var (default 40). Each search
  is $0.01.
- **Adding sentiment / urgency flags** — extend the prompt, no code changes needed.
- **Different scheduler** — the `src/run.py` script is the entrypoint; replace
  GitHub Actions with cron, Lambda, etc. as you like.

## Not investment advice. For personal research only.
