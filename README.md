# Stock News Daily

Twice-daily LLM-curated stock news emailed to you. Combines technical analysis
(via [fintools-mcp](https://github.com/slimbiggins007/fintools-mcp)) with web-searched
news, corporate actions, and announcements, summarized by Claude.

- **6am CST weekdays** — US market news (NYSE/NASDAQ tickers)
- **7pm CST weekdays** — India market news (NSE tickers)

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

## Local development

```bash
# Install dependencies
pip install -r requirements.txt

# Or install the package in editable mode (enables the `stock-digest` CLI command)
pip install -e .

# Copy the env template and fill in your secrets
cp .env .env

# Print the HTML without sending an email
python -m stock_news_daily.run --market us --dry-run

# Send for real
python -m stock_news_daily.run --market us

# If installed with pip install -e . you can also use the shorthand:
stock-digest --market us --dry-run
```

## Run tests

```bash
pip install pytest
pytest tests/
```

## Project structure

```
Stock_Daily_News/
├── .github/workflows/digest.yml   # GitHub Actions cron schedule
├── config/stocks.json             # Your watchlists — edit freely
├── stock_news_daily/              # The Python package
│   ├── digest.py                  # Claude API call + web search → HTML
│   ├── mailer.py                  # Resend email delivery
│   ├── run.py                     # Entrypoint — orchestrates everything
│   └── technicals.py              # fintools-mcp technical indicators
├── tests/
│   └── test_config.py             # Smoke tests (no API keys needed)
├── .env.example                   # Secret template — copy to .env locally
├── pyproject.toml                 # Modern Python packaging definition
└── requirements.txt               # For GitHub Actions pip install
```

## Customization

- **Prompt tuning** — `stock_news_daily/digest.py`, `SYSTEM_PROMPT` constant.
- **Search budget** — `MAX_SEARCHES_PER_RUN` env var (default 40). Each search is $0.01.
- **Model quality** — set `CLAUDE_MODEL=claude-sonnet-4-6` for better output at ~3x cost.
- **Different scheduler** — `stock_news_daily/run.py` is the entrypoint; swap GitHub
  Actions for cron, Lambda, Cloud Run, etc.

## Cost estimate

~$0.17 per run using Claude Haiku 4.5 with 40 web searches.
~$90/year for 2 runs/day on weekdays.

## Not investment advice. For personal research only.
