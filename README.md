# Stock Daily News

Twice-daily AI-curated stock digest delivered straight to your inbox. Combines real-time technical indicators with web-searched news, earnings, corporate actions, and filings — summarized by Google Gemini and sent via Gmail.

- **6:00 AM CST weekdays** — US market digest (NYSE / NASDAQ)
- **7:00 PM CST weekdays** — India market digest (NSE)

---

## How It Works

```
GitHub Actions (cron)
      │
      ▼
technicals.py ──── fintools-mcp + yfinance ──── RSI, MACD, EMA, ATR per ticker
      │
      ▼
digest.py ─────── Gemini 2.5 Flash + Google Search ──── HTML email body
      │
      ▼
mailer.py ─────── Gmail SMTP ──── delivered to your inbox
```

1. **Technical indicators** are fetched for every ticker using `fintools-mcp` (RSI, MACD, EMA 9/21/50/200, ATR).
2. **Gemini 2.5 Flash** searches the web for material news in the last 24 hours and combines it with the technicals into a formatted HTML digest.
3. **Gmail SMTP** delivers the email to your configured recipients — no domain or paid email service required.

---

## Tech Stack

| Layer | Tool |
|---|---|
| AI / LLM | [Google Gemini 2.5 Flash](https://ai.google.dev/) |
| Web Search | Gemini Google Search grounding |
| Technical Analysis | [fintools-mcp](https://github.com/slimbiggins007/fintools-mcp) + yfinance |
| Email Delivery | Gmail SMTP (`smtplib` — Python built-in) |
| Scheduler | GitHub Actions (cron) |
| Local Dev | python-dotenv |

---

## Project Structure

```
Stock_Daily_News/
├── .github/
│   └── workflows/
│       └── digest.yml          # GitHub Actions — cron schedule & secrets wiring
├── config/
│   └── stocks.json             # Watchlists for US and India — edit freely
├── stock_news_daily/
│   ├── run.py                  # Entrypoint — orchestrates everything
│   ├── digest.py               # Gemini API call + Google Search → HTML
│   ├── mailer.py               # Gmail SMTP delivery
│   └── technicals.py          # fintools-mcp indicators (RSI, MACD, EMA, ATR)
├── tests/
│   └── test_config.py          # Smoke tests — no API keys needed
├── .env                        # Local secrets (never commit this)
├── requirements.txt
└── pyproject.toml
```

---

## Setup

### 1. Fork this repo

Fork or clone to your own GitHub account.

### 2. Get API keys

**Gemini API key**
1. Go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Create an API key
3. Enable billing on the linked Google Cloud project (required for Google Search grounding)

**Gmail App Password**
1. Enable 2-Factor Authentication on your Google account at [myaccount.google.com/security](https://myaccount.google.com/security)
2. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. Create a new app password — name it "Stock Daily News"
4. Copy the 16-character password (you won't see it again)

### 3. Add GitHub Secrets

Go to your repo → **Settings → Secrets and variables → Actions → New repository secret**

| Secret | Value |
|---|---|
| `GEMINI_API_KEY` | Your Gemini API key |
| `GMAIL_USER` | Your Gmail address (e.g. `you@gmail.com`) |
| `GMAIL_KEY` | The 16-character Gmail app password |
| `EMAIL_TO` | Recipient email address |

Optional repo **variable** (not secret): `GEMINI_MODEL` — defaults to `gemini-2.5-flash`.

### 4. Edit your watchlist

Open `config/stocks.json` and add or remove tickers. Indian tickers require the `.NS` suffix (e.g. `RELIANCE.NS`) for yfinance compatibility.

```json
{
  "us": {
    "tickers": ["AAPL", "NVDA", "TSLA", "GOOGL"],
    "market_name": "US Markets"
  },
  "india": {
    "tickers": ["RELIANCE.NS", "TCS.NS", "INFY.NS"],
    "market_name": "Indian Markets"
  }
}
```

Commit and push — the next scheduled run picks up the change automatically.

### 5. Trigger a test run

Go to **Actions → Stock Digest → Run workflow**, pick a market, and click **Run workflow**. You should receive an email within ~2 minutes.

---

## Local Development

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Fill in your secrets
# Edit .env with your GEMINI_API_KEY, GMAIL_USER, GMAIL_KEY, EMAIL_TO

# Print the HTML without sending an email
python -m stock_news_daily.run --market us --dry-run

# Send a real email
python -m stock_news_daily.run --market us
python -m stock_news_daily.run --market india
```

---

## Customization

**Change tickers** — edit `config/stocks.json`, commit and push.

**Tune the prompt** — edit `SYSTEM_PROMPT` in `stock_news_daily/digest.py`.

**Change the model** — set `GEMINI_MODEL` as a GitHub Actions variable or in `.env`.

**Change schedule** — edit the cron lines in `.github/workflows/digest.yml`. Times are in UTC (CST = UTC−6).

---

## Cost Estimate

| Item | Cost |
|---|---|
| Gemini 2.5 Flash | ~$0.001 per run |
| Gmail SMTP | Free (500 emails/day) |
| GitHub Actions | Free (public repo) |
| **Total** | **< $0.10 / month** |

---

> **Not investment advice. For personal research only.**