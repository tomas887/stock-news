import os
import time
import calendar
import threading
from datetime import datetime, timedelta

import requests
import feedparser
from flask import Flask, render_template, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")
FINNHUB_BASE = "https://finnhub.io/api/v1"

# ---------------------------------------------------------------------------
# Curated European blue-chip tickers (~250)
# Format: (ticker, company_name, exchange)
# ---------------------------------------------------------------------------
TICKERS = [
    # ── Paris (Euronext Paris) – CAC 40 + Next 20 ─────────────────────────
    ("MC.PA", "LVMH", "Paris"),
    ("OR.PA", "L'Oréal", "Paris"),
    ("SAN.PA", "Sanofi", "Paris"),
    ("AI.PA", "Air Liquide", "Paris"),
    ("SU.PA", "Schneider Electric", "Paris"),
    ("BNP.PA", "BNP Paribas", "Paris"),
    ("TTE.PA", "TotalEnergies", "Paris"),
    ("KER.PA", "Kering", "Paris"),
    ("RI.PA", "Pernod Ricard", "Paris"),
    ("SAF.PA", "Safran", "Paris"),
    ("CS.PA", "AXA", "Paris"),
    ("DG.PA", "Vinci", "Paris"),
    ("CAP.PA", "Capgemini", "Paris"),
    ("DSY.PA", "Dassault Systèmes", "Paris"),
    ("HO.PA", "Thales", "Paris"),
    ("EN.PA", "Bouygues", "Paris"),
    ("GLE.PA", "Société Générale", "Paris"),
    ("LR.PA", "Legrand", "Paris"),
    ("STM.PA", "STMicroelectronics", "Paris"),
    ("VIV.PA", "Vivendi", "Paris"),
    ("RMS.PA", "Hermès", "Paris"),
    ("EL.PA", "EssilorLuxottica", "Paris"),
    ("MT.PA", "ArcelorMittal", "Paris"),
    ("ORA.PA", "Orange", "Paris"),
    ("PUB.PA", "Publicis", "Paris"),
    ("ACA.PA", "Crédit Agricole", "Paris"),
    ("URW.PA", "Unibail-Rodamco", "Paris"),
    ("ML.PA", "Michelin", "Paris"),
    ("SGO.PA", "Saint-Gobain", "Paris"),
    ("ERA.PA", "Eramet", "Paris"),
    ("RNO.PA", "Renault", "Paris"),
    ("ALO.PA", "Alstom", "Paris"),
    ("TEP.PA", "Teleperformance", "Paris"),
    ("WLN.PA", "Worldline", "Paris"),
    ("ATO.PA", "Atos", "Paris"),
    # ── London (LSE) – FTSE 100 major constituents ────────────────────────
    ("SHEL.L", "Shell", "London"),
    ("AZN.L", "AstraZeneca", "London"),
    ("HSBA.L", "HSBC", "London"),
    ("ULVR.L", "Unilever", "London"),
    ("BP.L", "BP", "London"),
    ("GSK.L", "GSK", "London"),
    ("RIO.L", "Rio Tinto", "London"),
    ("BATS.L", "British American Tobacco", "London"),
    ("DGE.L", "Diageo", "London"),
    ("LSEG.L", "London Stock Exchange", "London"),
    ("GLEN.L", "Glencore", "London"),
    ("VOD.L", "Vodafone", "London"),
    ("BARC.L", "Barclays", "London"),
    ("LLOY.L", "Lloyds Banking", "London"),
    ("REL.L", "RELX", "London"),
    ("AAL.L", "Anglo American", "London"),
    ("PRU.L", "Prudential", "London"),
    ("CPG.L", "Compass Group", "London"),
    ("RKT.L", "Reckitt Benckiser", "London"),
    ("ABF.L", "Associated British Foods", "London"),
    ("NG.L", "National Grid", "London"),
    ("SSE.L", "SSE", "London"),
    ("AHT.L", "Ashtead Group", "London"),
    ("EXPN.L", "Experian", "London"),
    ("III.L", "3i Group", "London"),
    ("IMB.L", "Imperial Brands", "London"),
    ("ANTO.L", "Antofagasta", "London"),
    ("BA.L", "BAE Systems", "London"),
    ("LAND.L", "Land Securities", "London"),
    ("SGRO.L", "Segro", "London"),
    ("WPP.L", "WPP", "London"),
    ("BT-A.L", "BT Group", "London"),
    ("TSCO.L", "Tesco", "London"),
    ("SBRY.L", "Sainsbury's", "London"),
    ("RR.L", "Rolls-Royce", "London"),
    ("STAN.L", "Standard Chartered", "London"),
    ("NWG.L", "NatWest Group", "London"),
    ("LGEN.L", "Legal & General", "London"),
    ("AVST.L", "Avast", "London"),
    ("SMT.L", "Scottish Mortgage", "London"),
    # ── Frankfurt (XETRA) – DAX 40 ───────────────────────────────────────
    ("SAP.DE", "SAP", "Frankfurt"),
    ("SIE.DE", "Siemens", "Frankfurt"),
    ("ALV.DE", "Allianz", "Frankfurt"),
    ("DTE.DE", "Deutsche Telekom", "Frankfurt"),
    ("BAS.DE", "BASF", "Frankfurt"),
    ("MBG.DE", "Mercedes-Benz", "Frankfurt"),
    ("BMW.DE", "BMW", "Frankfurt"),
    ("MRK.DE", "Merck KGaA", "Frankfurt"),
    ("ADS.DE", "Adidas", "Frankfurt"),
    ("DBK.DE", "Deutsche Bank", "Frankfurt"),
    ("MUV2.DE", "Munich Re", "Frankfurt"),
    ("VOW3.DE", "Volkswagen", "Frankfurt"),
    ("IFX.DE", "Infineon", "Frankfurt"),
    ("HEN3.DE", "Henkel", "Frankfurt"),
    ("CON.DE", "Continental", "Frankfurt"),
    ("FRE.DE", "Fresenius", "Frankfurt"),
    ("BEI.DE", "Beiersdorf", "Frankfurt"),
    ("RWE.DE", "RWE", "Frankfurt"),
    ("EOAN.DE", "E.ON", "Frankfurt"),
    ("HEI.DE", "Heidelberg Materials", "Frankfurt"),
    ("SHL.DE", "Siemens Healthineers", "Frankfurt"),
    ("DHL.DE", "DHL Group", "Frankfurt"),
    ("QIA.DE", "Qiagen", "Frankfurt"),
    ("PAH3.DE", "Porsche SE", "Frankfurt"),
    ("P911.DE", "Porsche AG", "Frankfurt"),
    ("SY1.DE", "Symrise", "Frankfurt"),
    ("ENR.DE", "Siemens Energy", "Frankfurt"),
    ("ZAL.DE", "Zalando", "Frankfurt"),
    ("HFG.DE", "HelloFresh", "Frankfurt"),
    ("1COV.DE", "Covestro", "Frankfurt"),
    ("TKA.DE", "thyssenkrupp", "Frankfurt"),
    ("LEG.DE", "LEG Immobilien", "Frankfurt"),
    ("FME.DE", "Fresenius Medical Care", "Frankfurt"),
    ("MTX.DE", "MTU Aero Engines", "Frankfurt"),
    ("SRT3.DE", "Sartorius", "Frankfurt"),
    ("AIR.DE", "Airbus", "Frankfurt"),
    # ── Amsterdam (Euronext Amsterdam) – AEX 25 + AMX ─────────────────────
    ("ASML.AS", "ASML", "Amsterdam"),
    ("INGA.AS", "ING Group", "Amsterdam"),
    ("PHIA.AS", "Philips", "Amsterdam"),
    ("AD.AS", "Ahold Delhaize", "Amsterdam"),
    ("WKL.AS", "Wolters Kluwer", "Amsterdam"),
    ("UNA.AS", "Unilever NV", "Amsterdam"),
    ("HEIA.AS", "Heineken", "Amsterdam"),
    ("AKZA.AS", "Akzo Nobel", "Amsterdam"),
    ("DSM.AS", "DSM-Firmenich", "Amsterdam"),
    ("NN.AS", "NN Group", "Amsterdam"),
    ("RAND.AS", "Randstad", "Amsterdam"),
    ("PRX.AS", "Prosus", "Amsterdam"),
    ("ASM.AS", "ASM International", "Amsterdam"),
    ("AGN.AS", "Aegon", "Amsterdam"),
    ("KPN.AS", "KPN", "Amsterdam"),
    ("IMCD.AS", "IMCD", "Amsterdam"),
    ("LIGHT.AS", "Signify", "Amsterdam"),
    ("JDEP.AS", "JDE Peet's", "Amsterdam"),
    ("ABN.AS", "ABN AMRO", "Amsterdam"),
    ("BESI.AS", "BE Semiconductor", "Amsterdam"),
    ("URW.AS", "Unibail-Rodamco NV", "Amsterdam"),
    ("TKWY.AS", "Just Eat Takeaway", "Amsterdam"),
    ("FLOW.AS", "Flow Traders", "Amsterdam"),
    # ── Madrid (BME) – IBEX 35 ────────────────────────────────────────────
    ("SAN.MC", "Banco Santander", "Madrid"),
    ("ITX.MC", "Inditex", "Madrid"),
    ("IBE.MC", "Iberdrola", "Madrid"),
    ("BBVA.MC", "BBVA", "Madrid"),
    ("TEF.MC", "Telefónica", "Madrid"),
    ("REP.MC", "Repsol", "Madrid"),
    ("FER.MC", "Ferrovial", "Madrid"),
    ("AMS.MC", "Amadeus IT", "Madrid"),
    ("CABK.MC", "CaixaBank", "Madrid"),
    ("ENG.MC", "Enagás", "Madrid"),
    ("ACS.MC", "ACS Group", "Madrid"),
    ("NTGY.MC", "Naturgy", "Madrid"),
    ("GRF.MC", "Grifols", "Madrid"),
    ("MAP.MC", "Mapfre", "Madrid"),
    ("CLNX.MC", "Cellnex", "Madrid"),
    ("IAG.MC", "IAG", "Madrid"),
    ("SAB.MC", "Banco Sabadell", "Madrid"),
    ("RED.MC", "Redeia", "Madrid"),
    ("LOG.MC", "Logista", "Madrid"),
    ("MRL.MC", "Merlin Properties", "Madrid"),
    ("ELE.MC", "Endesa", "Madrid"),
    ("AENA.MC", "Aena", "Madrid"),
    ("BKT.MC", "Bankinter", "Madrid"),
    # ── Zurich (SIX Swiss Exchange) – SMI 20 + SLI ───────────────────────
    ("NESN.SW", "Nestlé", "Zurich"),
    ("ROG.SW", "Roche", "Zurich"),
    ("NOVN.SW", "Novartis", "Zurich"),
    ("UBSG.SW", "UBS", "Zurich"),
    ("CSGN.SW", "Credit Suisse", "Zurich"),
    ("ZURN.SW", "Zurich Insurance", "Zurich"),
    ("ABBN.SW", "ABB", "Zurich"),
    ("SREN.SW", "Swiss Re", "Zurich"),
    ("GIVN.SW", "Givaudan", "Zurich"),
    ("LONN.SW", "Lonza", "Zurich"),
    ("GEBN.SW", "Geberit", "Zurich"),
    ("SIKA.SW", "Sika", "Zurich"),
    ("CFR.SW", "Richemont", "Zurich"),
    ("SCMN.SW", "Swisscom", "Zurich"),
    ("SLHN.SW", "Swiss Life", "Zurich"),
    ("BALN.SW", "Bâloise", "Zurich"),
    ("PGHN.SW", "Partners Group", "Zurich"),
    ("TEMN.SW", "Temenos", "Zurich"),
    ("SOON.SW", "Sonova", "Zurich"),
    ("STMN.SW", "Straumann", "Zurich"),
    ("BARN.SW", "Barry Callebaut", "Zurich"),
    ("CLN.SW", "Clariant", "Zurich"),
    ("SGSN.SW", "SGS", "Zurich"),
    ("KNIN.SW", "Kuehne+Nagel", "Zurich"),
    # ── Nordic – Stockholm, Copenhagen, Helsinki, Oslo ────────────────────
    ("NOVO-B.CO", "Novo Nordisk", "Nordic"),
    ("MAERSK-B.CO", "Maersk", "Nordic"),
    ("CARL-B.CO", "Carlsberg", "Nordic"),
    ("DSV.CO", "DSV", "Nordic"),
    ("ORSTED.CO", "Ørsted", "Nordic"),
    ("VWS.CO", "Vestas", "Nordic"),
    ("COLO-B.CO", "Coloplast", "Nordic"),
    ("GMAB.CO", "Genmab", "Nordic"),
    ("PNDORA.CO", "Pandora", "Nordic"),
    ("DEMANT.CO", "Demant", "Nordic"),
    ("GN.CO", "GN Store Nord", "Nordic"),
    ("ISS.CO", "ISS", "Nordic"),
    ("VOLV-B.ST", "Volvo", "Nordic"),
    ("ERIC-B.ST", "Ericsson", "Nordic"),
    ("ATCO-A.ST", "Atlas Copco", "Nordic"),
    ("SEB-A.ST", "SEB", "Nordic"),
    ("HM-B.ST", "H&M", "Nordic"),
    ("SAND.ST", "Sandvik", "Nordic"),
    ("ABB.ST", "ABB Sweden", "Nordic"),
    ("INVE-B.ST", "Investor AB", "Nordic"),
    ("SWED-A.ST", "Swedbank", "Nordic"),
    ("SKF-B.ST", "SKF", "Nordic"),
    ("HEXA-B.ST", "Hexagon", "Nordic"),
    ("ALFA.ST", "Alfa Laval", "Nordic"),
    ("ESSITY-B.ST", "Essity", "Nordic"),
    ("EVO.ST", "Evolution Gaming", "Nordic"),
    ("SINCH.ST", "Sinch", "Nordic"),
    ("TEL2-B.ST", "Tele2", "Nordic"),
    ("NESTE.HE", "Neste", "Nordic"),
    ("FORTUM.HE", "Fortum", "Nordic"),
    ("NOKIA.HE", "Nokia", "Nordic"),
    ("SAMPO.HE", "Sampo", "Nordic"),
    ("KNEBV.HE", "Kone", "Nordic"),
    ("UPM.HE", "UPM-Kymmene", "Nordic"),
    ("STERV.HE", "Stora Enso", "Nordic"),
    ("EQNR.OL", "Equinor", "Nordic"),
    ("DNB.OL", "DNB Bank", "Nordic"),
    ("TEL.OL", "Telenor", "Nordic"),
    ("MOWI.OL", "Mowi", "Nordic"),
    ("ORK.OL", "Orkla", "Nordic"),
    ("YAR.OL", "Yara International", "Nordic"),
    ("SALM.OL", "SalMar", "Nordic"),
    # ── Milan (Borsa Italiana) – FTSE MIB ─────────────────────────────────
    ("ENEL.MI", "Enel", "Milan"),
    ("ISP.MI", "Intesa Sanpaolo", "Milan"),
    ("UCG.MI", "UniCredit", "Milan"),
    ("RACE.MI", "Ferrari", "Milan"),
    ("ENI.MI", "Eni", "Milan"),
    ("G.MI", "Assicurazioni Generali", "Milan"),
    ("STLAM.MI", "Stellantis", "Milan"),
    ("TIT.MI", "Telecom Italia", "Milan"),
    ("PRY.MI", "Prysmian", "Milan"),
    ("MONC.MI", "Moncler", "Milan"),
    ("SRG.MI", "Snam", "Milan"),
    ("TRN.MI", "Terna", "Milan"),
    ("CPR.MI", "Campari", "Milan"),
    ("REC.MI", "Recordati", "Milan"),
    ("AMP.MI", "Amplifon", "Milan"),
    ("BMED.MI", "Banca Mediolanum", "Milan"),
    ("MB.MI", "Mediobanca", "Milan"),
    ("PST.MI", "Poste Italiane", "Milan"),
    ("LDO.MI", "Leonardo", "Milan"),
    ("SPM.MI", "Saipem", "Milan"),
    ("HER.MI", "Hera", "Milan"),
    ("PIRC.MI", "Pirelli", "Milan"),
    ("A2A.MI", "A2A", "Milan"),
    # ── Brussels (Euronext Brussels) – BEL 20 ─────────────────────────────
    ("ABI.BR", "AB InBev", "Brussels"),
    ("UCB.BR", "UCB", "Brussels"),
    ("KBC.BR", "KBC Group", "Brussels"),
    ("SOLB.BR", "Solvay", "Brussels"),
    ("ACKB.BR", "Ackermans & van Haaren", "Brussels"),
    ("UMI.BR", "Umicore", "Brussels"),
    ("GBLB.BR", "GBL", "Brussels"),
    ("COFB.BR", "Cofinimmo", "Brussels"),
    ("AGS.BR", "Ageas", "Brussels"),
    ("PROX.BR", "Proximus", "Brussels"),
    ("COLR.BR", "Colruyt", "Brussels"),
    ("WDP.BR", "WDP", "Brussels"),
    ("ONTEX.BR", "Ontex", "Brussels"),
    ("APAM.BR", "Aperam", "Brussels"),
    # ── Lisbon (Euronext Lisbon) – PSI 20 ─────────────────────────────────
    ("GALP.LS", "Galp Energia", "Lisbon"),
    ("EDP.LS", "EDP", "Lisbon"),
    ("EDPR.LS", "EDP Renováveis", "Lisbon"),
    ("JMT.LS", "Jerónimo Martins", "Lisbon"),
    ("SON.LS", "Sonae", "Lisbon"),
    ("BCP.LS", "Banco BCP", "Lisbon"),
    ("NOS.LS", "NOS", "Lisbon"),
    ("SEM.LS", "Semapa", "Lisbon"),
    ("ALTR.LS", "Altri", "Lisbon"),
    ("COR.LS", "Corticeira Amorim", "Lisbon"),
    ("RENE.LS", "REN", "Lisbon"),
    # ── Warsaw (GPW) – WIG 20 ────────────────────────────────────────────
    ("PKO.WA", "PKO Bank", "Warsaw"),
    ("PZU.WA", "PZU", "Warsaw"),
    ("PKN.WA", "PKN Orlen", "Warsaw"),
    ("PEO.WA", "Pekao", "Warsaw"),
    ("KGH.WA", "KGHM", "Warsaw"),
    ("LPP.WA", "LPP", "Warsaw"),
    ("DNP.WA", "Dino Polska", "Warsaw"),
    ("ALE.WA", "Allegro", "Warsaw"),
    ("CDR.WA", "CD Projekt", "Warsaw"),
    ("SPL.WA", "Santander Polska", "Warsaw"),
    ("CCC.WA", "CCC", "Warsaw"),
    ("MBK.WA", "mBank", "Warsaw"),
    # ── Vienna (Wiener Börse) – ATX ───────────────────────────────────────
    ("VOE.VI", "voestalpine", "Vienna"),
    ("VER.VI", "Verbund", "Vienna"),
    ("RBI.VI", "Raiffeisen Bank", "Vienna"),
    ("EBS.VI", "Erste Group", "Vienna"),
    ("OMV.VI", "OMV", "Vienna"),
    ("WIE.VI", "Wienerberger", "Vienna"),
    ("TKA.VI", "Telekom Austria", "Vienna"),
    ("IIA.VI", "Immofinanz", "Vienna"),
    ("BG.VI", "BAWAG Group", "Vienna"),
    ("SBO.VI", "Schoeller-Bleckmann", "Vienna"),
    # ── Dublin (Euronext Dublin / ISE) ────────────────────────────────────
    ("RYA.L", "Ryanair", "Dublin"),
    ("CRH.L", "CRH", "Dublin"),
    ("BIRG.L", "Bank of Ireland", "Dublin"),
    ("SKG.L", "Smurfit Kappa", "Dublin"),
    ("KRX.L", "Kingspan", "Dublin"),
    ("FLTR.L", "Flutter Entertainment", "Dublin"),
    ("GLV.L", "Glanbia", "Dublin"),
]

EXCHANGE_LIST = [
    "Paris", "London", "Frankfurt", "Amsterdam", "Madrid",
    "Zurich", "Nordic", "Milan",
    "Brussels", "Lisbon", "Warsaw", "Vienna", "Dublin",
]

# Lookup helpers
TICKER_INFO = {t: (name, exch) for t, name, exch in TICKERS}

# ---------------------------------------------------------------------------
# Rate limiter – keep under 55 calls / 60 s (Finnhub free tier = 60/min)
# ---------------------------------------------------------------------------
_call_timestamps: list[float] = []
_rate_lock = threading.Lock()
RATE_LIMIT = 55
RATE_WINDOW = 60  # seconds


def _rate_limit():
    """Block until a call slot is available."""
    while True:
        with _rate_lock:
            now = time.time()
            _call_timestamps[:] = [t for t in _call_timestamps if now - t < RATE_WINDOW]
            if len(_call_timestamps) < RATE_LIMIT:
                _call_timestamps.append(now)
                return
        time.sleep(0.5)


# ---------------------------------------------------------------------------
# Finnhub API helpers
# ---------------------------------------------------------------------------
def fetch_company_news(ticker: str, days_back: int = 7, max_articles: int = 3) -> list[dict]:
    """Fetch recent company news for a single ticker."""
    _rate_limit()
    to_date = datetime.utcnow().strftime("%Y-%m-%d")
    from_date = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    try:
        resp = requests.get(
            f"{FINNHUB_BASE}/company-news",
            params={"symbol": ticker, "from": from_date, "to": to_date, "token": FINNHUB_API_KEY},
            timeout=10,
        )
        resp.raise_for_status()
        articles = resp.json()
        if not isinstance(articles, list):
            return []
        results = []
        for a in articles[:max_articles]:
            name, exch = TICKER_INFO.get(ticker, (ticker, "Unknown"))
            results.append({
                "ticker": ticker,
                "company": name,
                "exchange": exch,
                "headline": a.get("headline", ""),
                "summary": a.get("summary", ""),
                "url": a.get("url", ""),
                "source": a.get("source", ""),
                "image": a.get("image", ""),
                "datetime": a.get("datetime", 0),
            })
        return results
    except Exception:
        return []


def fetch_general_news(max_articles: int = 10) -> list[dict]:
    """Fetch general market news from Finnhub."""
    _rate_limit()
    try:
        resp = requests.get(
            f"{FINNHUB_BASE}/news",
            params={"category": "general", "token": FINNHUB_API_KEY},
            timeout=10,
        )
        resp.raise_for_status()
        articles = resp.json()
        if not isinstance(articles, list):
            return []
        results = []
        for a in articles[:max_articles]:
            results.append({
                "ticker": "MARKET",
                "company": "General Market News",
                "exchange": "General",
                "headline": a.get("headline", ""),
                "summary": a.get("summary", ""),
                "url": a.get("url", ""),
                "source": a.get("source", ""),
                "image": a.get("image", ""),
                "datetime": a.get("datetime", 0),
            })
        return results
    except Exception:
        return []


# ---------------------------------------------------------------------------
# RSS feeds – Bloomberg, Reuters (via Google News), FT, DW, index-specific
# ---------------------------------------------------------------------------
RSS_FEEDS = [
    # Bloomberg direct feeds
    ("https://feeds.bloomberg.com/markets/news.rss", "Bloomberg"),
    ("https://feeds.bloomberg.com/economics/news.rss", "Bloomberg"),
    ("https://feeds.bloomberg.com/technology/news.rss", "Bloomberg"),
    ("https://feeds.bloomberg.com/wealth/news.rss", "Bloomberg"),
    # Reuters via Google News (Reuters blocks direct RSS)
    ("https://news.google.com/rss/search?q=site:reuters.com+stocks+OR+market&hl=en&gl=US&ceid=US:en", "Reuters"),
    ("https://news.google.com/rss/search?q=site:reuters.com+european+stocks&hl=en&gl=US&ceid=US:en", "Reuters"),
    ("https://news.google.com/rss/search?q=site:reuters.com+FTSE+OR+DAX+OR+CAC&hl=en&gl=US&ceid=US:en", "Reuters"),
    # Financial Times via Google News
    ("https://news.google.com/rss/search?q=site:ft.com+european+stocks+OR+equities&hl=en&gl=US&ceid=US:en", "Financial Times"),
    ("https://news.google.com/rss/search?q=site:ft.com+FTSE+OR+DAX+OR+CAC+OR+STOXX&hl=en&gl=US&ceid=US:en", "Financial Times"),
    # European index-specific feeds
    ("https://news.google.com/rss/search?q=CAC+40+stocks&hl=en&gl=US&ceid=US:en", "Google News"),
    ("https://news.google.com/rss/search?q=DAX+40+stocks&hl=en&gl=US&ceid=US:en", "Google News"),
    ("https://news.google.com/rss/search?q=FTSE+100+stocks&hl=en&gl=US&ceid=US:en", "Google News"),
    ("https://news.google.com/rss/search?q=IBEX+35+stocks&hl=en&gl=US&ceid=US:en", "Google News"),
    ("https://news.google.com/rss/search?q=SMI+Swiss+stocks&hl=en&gl=US&ceid=US:en", "Google News"),
    ("https://news.google.com/rss/search?q=STOXX+600+European+market&hl=en&gl=US&ceid=US:en", "Google News"),
    ("https://news.google.com/rss/search?q=FTSE+MIB+Italian+stocks&hl=en&gl=US&ceid=US:en", "Google News"),
    ("https://news.google.com/rss/search?q=Nordic+OMX+stocks&hl=en&gl=US&ceid=US:en", "Google News"),
    # DW (Deutsche Welle) business
    ("https://rss.dw.com/xml/rss-en-bus", "DW"),
    # Investing.com via Google News
    ("https://news.google.com/rss/search?q=site:investing.com+European+stocks&hl=en&gl=US&ceid=US:en", "Investing.com"),
    # European sector-specific
    ("https://news.google.com/rss/search?q=European+banks+stocks&hl=en&gl=US&ceid=US:en", "Google News"),
    ("https://news.google.com/rss/search?q=European+luxury+stocks+LVMH+OR+Kering+OR+Hermes&hl=en&gl=US&ceid=US:en", "Google News"),
    ("https://news.google.com/rss/search?q=European+energy+stocks+Shell+OR+TotalEnergies+OR+BP&hl=en&gl=US&ceid=US:en", "Google News"),
]

MAX_RSS_PER_FEED = 15


def _parse_rss_date(entry) -> int:
    """Extract a unix timestamp from an RSS entry."""
    for field in ("published_parsed", "updated_parsed"):
        parsed = getattr(entry, field, None)
        if parsed:
            return int(calendar.timegm(parsed))
    return 0


def fetch_rss_news() -> list[dict]:
    """Fetch and parse all RSS feeds."""
    seen_urls: set[str] = set()
    results = []
    for feed_url, source_name in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:MAX_RSS_PER_FEED]:
                url = entry.get("link", "")
                if url in seen_urls:
                    continue
                seen_urls.add(url)
                # Try to get an image from media content
                image = ""
                media = entry.get("media_content", [])
                if media and isinstance(media, list):
                    image = media[0].get("url", "")
                results.append({
                    "ticker": "MARKET",
                    "company": f"{source_name} News",
                    "exchange": "General",
                    "headline": entry.get("title", ""),
                    "summary": entry.get("summary", "")[:300],
                    "url": url,
                    "source": source_name,
                    "image": image,
                    "datetime": _parse_rss_date(entry),
                })
        except Exception:
            continue
    return results


# ---------------------------------------------------------------------------
# In-memory article cache
# ---------------------------------------------------------------------------
_cache: dict = {"articles": [], "last_updated": None}
_cache_lock = threading.Lock()
_initial_load = threading.Event()


def _refresh_cache():
    """Fetch news for all tickers + general + RSS feeds, update cache."""
    all_articles = []
    for ticker, _name, _exch in TICKERS:
        articles = fetch_company_news(ticker)
        all_articles.extend(articles)
    general = fetch_general_news()
    all_articles.extend(general)
    rss = fetch_rss_news()
    all_articles.extend(rss)
    # Deduplicate by URL
    seen_urls: set[str] = set()
    unique = []
    for a in all_articles:
        url = a.get("url", "")
        if url and url in seen_urls:
            continue
        seen_urls.add(url)
        unique.append(a)
    all_articles = unique
    # Sort newest first
    all_articles.sort(key=lambda a: a["datetime"], reverse=True)
    with _cache_lock:
        _cache["articles"] = all_articles
        _cache["last_updated"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    _initial_load.set()


def _background_fetcher():
    """Run cache refresh every 15 minutes."""
    while True:
        _refresh_cache()
        time.sleep(15 * 60)


# Start background thread on import
_bg_thread = threading.Thread(target=_background_fetcher, daemon=True)
_bg_thread.start()


# ---------------------------------------------------------------------------
# Flask routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    # Block until first fetch is done
    _initial_load.wait()
    with _cache_lock:
        articles = list(_cache["articles"])
        last_updated = _cache["last_updated"]
    return render_template(
        "index.html",
        articles=articles,
        last_updated=last_updated,
        exchanges=EXCHANGE_LIST,
        total=len(articles),
    )


@app.route("/api/news")
def api_news():
    _initial_load.wait()
    with _cache_lock:
        return jsonify({
            "articles": _cache["articles"],
            "last_updated": _cache["last_updated"],
            "total": len(_cache["articles"]),
        })


if __name__ == "__main__":
    app.run(debug=True, port=5001)
