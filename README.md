# European Stock News Dashboard

A real-time news aggregator for major European stocks, built with Flask. Pulls news from multiple sources and displays them in a filterable, responsive dashboard.

![Python](https://img.shields.io/badge/Python-3.9+-blue) ![Flask](https://img.shields.io/badge/Flask-3.x-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

## Features

- **300 blue-chip tickers** across 13 European exchanges (Paris, London, Frankfurt, Amsterdam, Madrid, Zurich, Nordic, Milan, Brussels, Lisbon, Warsaw, Vienna, Dublin)
- **1,400+ articles** per refresh with **100% ticker coverage** — every single company has news
- **Multi-source news aggregation**: Finnhub API, Google News per-company RSS, Bloomberg, Reuters, Financial Times, DW, Investing.com, and index/sector-specific feeds
- **Client-side filtering**: instant exchange tabs and free-text search (ticker, company, or headline)
- **Background refresh**: news updates every 15 minutes with rate-limited API calls
- **Responsive design**: 3-column grid on desktop, single column on mobile
- **Color-coded exchange badges** for quick visual identification

## News Sources

| Source | Method | Coverage |
|--------|--------|----------|
| Google News (per-company) | RSS search per company name, 15 threads in parallel | All 300 tickers — ensures 100% coverage |
| Finnhub | API (company-news + general) | Per-ticker + market news |
| Bloomberg | Direct RSS feeds | Markets, economics, technology, wealth |
| Reuters | Google News RSS proxy | Stocks, European equities, indices |
| Financial Times | Google News RSS proxy | European equities, major indices |
| DW (Deutsche Welle) | Direct RSS | German/EU business |
| Investing.com | Google News RSS proxy | European stocks |
| Index-specific | Google News RSS | CAC 40, DAX, FTSE 100, IBEX 35, SMI, STOXX 600, FTSE MIB, OMX |
| Sector-specific | Google News RSS | European banks, luxury, energy |

## Setup

```bash
# Clone
git clone https://github.com/tomas887/stock-news.git
cd stock-news

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Add your Finnhub API key
echo "FINNHUB_API_KEY=your_key_here" > .env
```

Get a free API key at [finnhub.io](https://finnhub.io/).

## Run

```bash
python app.py
```

Open **http://localhost:5001** in your browser.

The first page load takes ~7 minutes while it fetches news for all 300 tickers (Finnhub rate-limited + Google News in parallel). Subsequent loads are instant from cache.

## Exchanges Covered

| Exchange | Index | Tickers | Examples |
|----------|-------|---------|----------|
| Paris (Euronext) | CAC 40 + Next 20 | 35 | LVMH, Hermès, L'Oréal, TotalEnergies, Sanofi |
| London (LSE) | FTSE 100 | 40 | Shell, AstraZeneca, HSBC, Rolls-Royce, BAE Systems |
| Frankfurt (XETRA) | DAX 40 | 36 | SAP, Siemens, Allianz, Porsche, Airbus |
| Amsterdam (Euronext) | AEX 25 + AMX | 23 | ASML, Prosus, ING, Philips, Heineken |
| Madrid (BME) | IBEX 35 | 23 | Santander, Inditex, Iberdrola, Cellnex, Aena |
| Zurich (SIX) | SMI 20 + SLI | 24 | Nestlé, Roche, Novartis, Richemont, UBS |
| Nordic (OMX) | OMX Stockholm/Copenhagen/Helsinki/Oslo | 42 | Novo Nordisk, Volvo, Equinor, Nokia, Ericsson |
| Milan (Borsa Italiana) | FTSE MIB | 23 | Ferrari, Enel, UniCredit, Campari, Pirelli |
| Brussels (Euronext) | BEL 20 | 14 | AB InBev, UCB, KBC, Solvay, Umicore |
| Lisbon (Euronext) | PSI 20 | 11 | Galp, EDP, Jerónimo Martins, Corticeira Amorim |
| Warsaw (GPW) | WIG 20 | 12 | PKO Bank, CD Projekt, Allegro, Dino Polska |
| Vienna (Wiener Börse) | ATX | 10 | Verbund, Erste Group, OMV, Raiffeisen Bank |
| Dublin (Euronext) | ISE | 7 | Ryanair, CRH, Flutter, Kingspan, Smurfit Kappa |

## Tech Stack

- **Backend**: Flask, Requests, feedparser, python-dotenv
- **Frontend**: Jinja2 templates, vanilla JS, CSS Grid
- **Data**: Finnhub API + 22 RSS feeds + 300 Google News per-company feeds (parallel)
