# European Stock News Dashboard

A real-time news aggregator for major European stocks, built with Flask. Pulls news from multiple sources and displays them in a filterable, responsive dashboard.

![Python](https://img.shields.io/badge/Python-3.9+-blue) ![Flask](https://img.shields.io/badge/Flask-3.x-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

## Features

- **113 blue-chip tickers** across 8 European exchanges (Paris, London, Frankfurt, Amsterdam, Madrid, Zurich, Nordic, Milan)
- **Multi-source news aggregation**: Finnhub API, Bloomberg, Reuters, Financial Times, DW, Investing.com, and index/sector-specific feeds
- **Client-side filtering**: instant exchange tabs and free-text search (ticker, company, or headline)
- **Background refresh**: news updates every 15 minutes with rate-limited API calls
- **Responsive design**: 3-column grid on desktop, single column on mobile
- **Color-coded exchange badges** for quick visual identification

## News Sources

| Source | Method | Coverage |
|--------|--------|----------|
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

The first page load takes ~2 minutes while it fetches news for all 113 tickers. Subsequent loads are instant from cache.

## Exchanges Covered

| Exchange | Tickers | Examples |
|----------|---------|----------|
| Paris (Euronext) | 20 | LVMH, L'Oréal, TotalEnergies, Sanofi, BNP Paribas |
| London (LSE) | 20 | Shell, AstraZeneca, HSBC, Unilever, BP |
| Frankfurt (XETRA) | 20 | SAP, Siemens, Allianz, Volkswagen, Adidas |
| Amsterdam (Euronext) | 11 | ASML, ING, Philips, Heineken |
| Madrid (BME) | 10 | Santander, Inditex, Iberdrola, BBVA |
| Zurich (SIX) | 12 | Nestlé, Roche, Novartis, UBS, ABB |
| Nordic (OMX) | 12 | Novo Nordisk, Volvo, Ericsson, H&M |
| Milan (Borsa Italiana) | 10 | Ferrari, Enel, UniCredit, Moncler |

## Tech Stack

- **Backend**: Flask, Requests, feedparser, python-dotenv
- **Frontend**: Jinja2 templates, vanilla JS, CSS Grid
- **Data**: Finnhub API + 22 RSS feeds
