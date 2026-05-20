"""
Catálogo curado de empresas — país · sector · ticker.

Fuente de verdad única del universo navegable de la app. Cada empresa
lleva ``country``, ``sector`` y ``region`` para alimentar el selector en
cascada (País → Sector → Empresa) de la pantalla de búsqueda.

El módulo no importa nada pesado: ``data.regions`` y el selector se
construyen ENCIMA de este catálogo, nunca al revés. Las listas son
curadas — refrescar manualmente cuando el universo cambie; los sufijos
de bolsa de yfinance (.PA .DE .L .T .HK .SA .BA …) y los nombres son
estables.

API
---
``regions()``                  — regiones en orden de display
``countries(region=None)``     — países (todos, o de una región)
``sectors(country)``           — sectores presentes en ese país
``companies(country, sector)`` — empresas de ese país + sector
``company_for(ticker)``        — la ``Company`` de un ticker, o None
``all_companies()``            — el catálogo completo
``universe_by_region(region)`` — ``{ticker: name}`` de la región
``region_of_ticker(ticker)``   — región de un ticker
"""
from __future__ import annotations
from dataclasses import dataclass

from data.ticker_universe import SP500_TOP


@dataclass(frozen=True)
class Company:
    """Un constituyente del catálogo."""
    ticker:  str
    name:    str
    country: str
    sector:  str
    region:  str


# ============================================================
# Taxonomía de sectores — orden de display en el selector
# ============================================================
_SECTOR_ORDER = (
    "Technology",
    "Communication & Media",
    "Financial Services",
    "Healthcare",
    "Consumer Staples",
    "Consumer Discretionary",
    "Industrials",
    "Energy",
    "Materials",
    "Utilities",
    "Real Estate",
    "ETFs & Indices",
)


def _b(country: str, region: str,
       rows: list[tuple[str, str, str]]) -> list[Company]:
    """Expande filas ``(ticker, name, sector)`` a ``Company`` con el
    ``country`` y ``region`` del bloque."""
    return [Company(t, n, country, s, region) for t, n, s in rows]


# ============================================================
# Estados Unidos — subset S&P 500 (nombres desde ticker_universe)
# ============================================================
# ticker → sector. Los nombres salen de SP500_TOP para no duplicarlos.
_US_SECTORS: dict[str, str] = {
    # Tecnología
    "AAPL": "Technology", "MSFT": "Technology", "NVDA": "Technology",
    "AVGO": "Technology", "ORCL": "Technology", "CRM": "Technology",
    "ADBE": "Technology", "CSCO": "Technology", "AMD": "Technology",
    "INTC": "Technology", "QCOM": "Technology", "TXN": "Technology",
    "IBM": "Technology", "INTU": "Technology", "NOW": "Technology",
    "PLTR": "Technology",
    # Comunicación y medios
    "GOOGL": "Communication & Media", "GOOG": "Communication & Media",
    "META": "Communication & Media", "NFLX": "Communication & Media",
    "DIS": "Communication & Media", "CMCSA": "Communication & Media",
    "T": "Communication & Media", "VZ": "Communication & Media",
    # Consumo discrecional
    "AMZN": "Consumer Discretionary", "TSLA": "Consumer Discretionary",
    "MCD": "Consumer Discretionary", "SBUX": "Consumer Discretionary",
    "NKE": "Consumer Discretionary", "HD": "Consumer Discretionary",
    "LOW": "Consumer Discretionary", "TGT": "Consumer Discretionary",
    "BKNG": "Consumer Discretionary", "MAR": "Consumer Discretionary",
    # Servicios financieros
    "BRK-B": "Financial Services", "JPM": "Financial Services",
    "V": "Financial Services", "MA": "Financial Services",
    "BAC": "Financial Services", "WFC": "Financial Services",
    "GS": "Financial Services", "MS": "Financial Services",
    "C": "Financial Services", "AXP": "Financial Services",
    "BLK": "Financial Services", "SCHW": "Financial Services",
    "PYPL": "Financial Services",
    # Salud
    "LLY": "Healthcare", "UNH": "Healthcare", "JNJ": "Healthcare", "ABBV": "Healthcare",
    "MRK": "Healthcare", "PFE": "Healthcare", "TMO": "Healthcare", "ABT": "Healthcare",
    "DHR": "Healthcare", "BMY": "Healthcare", "AMGN": "Healthcare", "CVS": "Healthcare",
    "GILD": "Healthcare", "ISRG": "Healthcare", "VRTX": "Healthcare", "REGN": "Healthcare",
    # Consumo masivo
    "WMT": "Consumer Staples", "PG": "Consumer Staples", "KO": "Consumer Staples",
    "PEP": "Consumer Staples", "COST": "Consumer Staples", "MO": "Consumer Staples",
    "PM": "Consumer Staples", "MDLZ": "Consumer Staples",
    # Industria
    "GE": "Industrials", "HON": "Industrials", "BA": "Industrials",
    "CAT": "Industrials", "DE": "Industrials", "RTX": "Industrials",
    "LMT": "Industrials", "UPS": "Industrials", "FDX": "Industrials",
    # Energía
    "XOM": "Energy", "CVX": "Energy", "COP": "Energy",
    "SLB": "Energy", "EOG": "Energy",
    # Materiales
    "LIN": "Materials", "FCX": "Materials", "NEM": "Materials",
    # Servicios públicos
    "NEE": "Utilities", "DUK": "Utilities",
    "SO": "Utilities",
    # Bienes raíces
    "AMT": "Real Estate", "PLD": "Real Estate",
    # ETF e índices
    "SPY": "ETFs & Indices", "QQQ": "ETFs & Indices", "DIA": "ETFs & Indices",
    "IWM": "ETFs & Indices", "VOO": "ETFs & Indices", "VTI": "ETFs & Indices",
    "GLD": "ETFs & Indices", "TLT": "ETFs & Indices",
}

_UNITED_STATES = [
    Company(t, SP500_TOP.get(t, t), "United States",
            _US_SECTORS.get(t, "Otros"), "North America")
    for t in SP500_TOP
]


# ============================================================
# Europa
# ============================================================
_FRANCE = _b("France", "Europe", [
    ("MC.PA",  "LVMH",                  "Consumer Discretionary"),
    ("OR.PA",  "L'Oréal",               "Consumer Staples"),
    ("TTE.PA", "TotalEnergies",         "Energy"),
    ("SAN.PA", "Sanofi",                "Healthcare"),
    ("AIR.PA", "Airbus",                "Industrials"),
    ("SU.PA",  "Schneider Electric",    "Industrials"),
    ("EL.PA",  "EssilorLuxottica",      "Consumer Discretionary"),
    ("BNP.PA", "BNP Paribas",           "Financial Services"),
    ("AI.PA",  "Air Liquide",           "Materials"),
    ("DG.PA",  "Vinci",                 "Industrials"),
    ("CS.PA",  "AXA",                   "Financial Services"),
    ("RMS.PA", "Hermès",                "Consumer Discretionary"),
    ("KER.PA", "Kering",                "Consumer Discretionary"),
])
_GERMANY = _b("Germany", "Europe", [
    ("SAP.DE",  "SAP",                  "Technology"),
    ("SIE.DE",  "Siemens",              "Industrials"),
    ("ALV.DE",  "Allianz",              "Financial Services"),
    ("DTE.DE",  "Deutsche Telekom",     "Communication & Media"),
    ("MBG.DE",  "Mercedes-Benz Group",  "Consumer Discretionary"),
    ("BMW.DE",  "BMW",                  "Consumer Discretionary"),
    ("BAS.DE",  "BASF",                 "Materials"),
    ("BAYN.DE", "Bayer",                "Healthcare"),
    ("MUV2.DE", "Munich Re",            "Financial Services"),
    ("IFX.DE",  "Infineon Technologies","Technology"),
    ("DBK.DE",  "Deutsche Bank",        "Financial Services"),
    ("VOW3.DE", "Volkswagen",           "Consumer Discretionary"),
])
_UK = _b("United Kingdom", "Europe", [
    ("SHEL.L", "Shell",                       "Energy"),
    ("AZN.L",  "AstraZeneca",                 "Healthcare"),
    ("HSBA.L", "HSBC Holdings",               "Financial Services"),
    ("ULVR.L", "Unilever",                    "Consumer Staples"),
    ("BP.L",   "BP",                          "Energy"),
    ("GSK.L",  "GSK",                         "Healthcare"),
    ("RIO.L",  "Rio Tinto",                   "Materials"),
    ("DGE.L",  "Diageo",                      "Consumer Staples"),
    ("BATS.L", "British American Tobacco",    "Consumer Staples"),
    ("LSEG.L", "London Stock Exchange Group", "Financial Services"),
])
_NETHERLANDS = _b("Netherlands", "Europe", [
    ("ASML.AS", "ASML Holding",   "Technology"),
    ("PRX.AS",  "Prosus",         "Technology"),
    ("INGA.AS", "ING Groep",      "Financial Services"),
    ("AD.AS",   "Ahold Delhaize", "Consumer Staples"),
    ("HEIA.AS", "Heineken",       "Consumer Staples"),
])
_SWITZERLAND = _b("Switzerland", "Europe", [
    ("NESN.SW", "Nestlé",            "Consumer Staples"),
    ("NOVN.SW", "Novartis",          "Healthcare"),
    ("ROG.SW",  "Roche Holding",     "Healthcare"),
    ("UBSG.SW", "UBS Group",         "Financial Services"),
    ("ZURN.SW", "Zurich Insurance",  "Financial Services"),
])
_SPAIN = _b("Spain", "Europe", [
    ("IBE.MC",  "Iberdrola",        "Utilities"),
    ("SAN.MC",  "Banco Santander",  "Financial Services"),
    ("ITX.MC",  "Inditex",          "Consumer Discretionary"),
    ("BBVA.MC", "BBVA",             "Financial Services"),
])
_ITALY = _b("Italy", "Europe", [
    ("ENI.MI",  "Eni",              "Energy"),
    ("ISP.MI",  "Intesa Sanpaolo",  "Financial Services"),
    ("ENEL.MI", "Enel",             "Utilities"),
    ("RACE.MI", "Ferrari",          "Consumer Discretionary"),
    ("UCG.MI",  "UniCredit",        "Financial Services"),
])
_DENMARK = _b("Denmark", "Europe", [
    ("NOVO-B.CO", "Novo Nordisk",   "Healthcare"),
])


# ============================================================
# Asia
# ============================================================
_JAPAN = _b("Japan", "Asia", [
    ("7203.T", "Toyota Motor",                 "Consumer Discretionary"),
    ("6758.T", "Sony Group",                   "Technology"),
    ("9984.T", "SoftBank Group",               "Technology"),
    ("8306.T", "Mitsubishi UFJ Financial",     "Financial Services"),
    ("6861.T", "Keyence",                      "Technology"),
    ("9432.T", "Nippon Telegraph & Telephone", "Communication & Media"),
    ("6098.T", "Recruit Holdings",             "Industrials"),
    ("8035.T", "Tokyo Electron",               "Technology"),
    ("7974.T", "Nintendo",                     "Communication & Media"),
    ("9433.T", "KDDI",                         "Communication & Media"),
    ("6501.T", "Hitachi",                      "Industrials"),
    ("4063.T", "Shin-Etsu Chemical",           "Materials"),
    ("8058.T", "Mitsubishi Corporation",       "Industrials"),
    ("7267.T", "Honda Motor",                  "Consumer Discretionary"),
    ("6594.T", "Nidec",                        "Industrials"),
    ("4502.T", "Takeda Pharmaceutical",        "Healthcare"),
])
_HONG_KONG = _b("Hong Kong", "Asia", [
    ("0700.HK", "Tencent Holdings",          "Communication & Media"),
    ("9988.HK", "Alibaba Group",             "Consumer Discretionary"),
    ("3690.HK", "Meituan",                   "Consumer Discretionary"),
    ("1299.HK", "AIA Group",                 "Financial Services"),
    ("0939.HK", "China Construction Bank",   "Financial Services"),
    ("1810.HK", "Xiaomi",                    "Technology"),
    ("2318.HK", "Ping An Insurance",         "Financial Services"),
    ("0941.HK", "China Mobile",              "Communication & Media"),
    ("1398.HK", "ICBC",                      "Financial Services"),
    ("2628.HK", "China Life Insurance",      "Financial Services"),
    ("0883.HK", "CNOOC",                     "Energy"),
    ("1211.HK", "BYD",                       "Consumer Discretionary"),
    ("9618.HK", "JD.com",                    "Consumer Discretionary"),
])
_KOREA = _b("South Korea", "Asia", [
    ("005930.KS", "Samsung Electronics", "Technology"),
    ("000660.KS", "SK Hynix",            "Technology"),
    ("005380.KS", "Hyundai Motor",       "Consumer Discretionary"),
    ("051910.KS", "LG Chem",             "Materials"),
    ("035420.KS", "NAVER",               "Communication & Media"),
])
_TAIWAN = _b("Taiwan", "Asia", [
    ("2330.TW", "TSMC",                  "Technology"),
    ("2317.TW", "Hon Hai (Foxconn)",     "Technology"),
    ("2454.TW", "MediaTek",              "Technology"),
    ("2308.TW", "Delta Electronics",     "Technology"),
    ("2412.TW", "Chunghwa Telecom",      "Communication & Media"),
    ("2882.TW", "Cathay Financial",      "Financial Services"),
])
_INDIA = _b("India", "Asia", [
    ("RELIANCE.NS",   "Reliance Industries",        "Energy"),
    ("TCS.NS",        "Tata Consultancy Services",  "Technology"),
    ("INFY.NS",       "Infosys",                    "Technology"),
    ("HDFCBANK.NS",   "HDFC Bank",                  "Financial Services"),
    ("ICICIBANK.NS",  "ICICI Bank",                 "Financial Services"),
    ("BHARTIARTL.NS", "Bharti Airtel",              "Communication & Media"),
    ("SBIN.NS",       "State Bank of India",        "Financial Services"),
    ("LT.NS",         "Larsen & Toubro",            "Industrials"),
    ("HINDUNILVR.NS", "Hindustan Unilever",         "Consumer Staples"),
])


# ============================================================
# Latinoamérica
# ============================================================
# Argentina — panel líder del Merval (.BA) + MercadoLibre (NASDAQ).
_ARGENTINA = _b("Argentina", "Latin America", [
    ("GGAL.BA",  "Grupo Financiero Galicia",        "Financial Services"),
    ("BMA.BA",   "Banco Macro",                     "Financial Services"),
    ("BBAR.BA",  "BBVA Argentina",                  "Financial Services"),
    ("SUPV.BA",  "Grupo Supervielle",               "Financial Services"),
    ("VALO.BA",  "Grupo Financiero Valores",        "Financial Services"),
    ("BYMA.BA",  "Bolsas y Mercados Argentinos",    "Financial Services"),
    ("YPFD.BA",  "YPF",                             "Energy"),
    ("PAMP.BA",  "Pampa Energía",                   "Energy"),
    ("CEPU.BA",  "Central Puerto",                  "Energy"),
    ("EDN.BA",   "Edenor",                          "Energy"),
    ("TGSU2.BA", "Transportadora de Gas del Sur",   "Energy"),
    ("TGNO4.BA", "Transportadora de Gas del Norte", "Energy"),
    ("TRAN.BA",  "Transener",                       "Energy"),
    ("METR.BA",  "MetroGAS",                        "Energy"),
    ("TXAR.BA",  "Ternium Argentina",               "Materials"),
    ("ALUA.BA",  "Aluar",                           "Materials"),
    ("LOMA.BA",  "Loma Negra",                      "Materials"),
    ("TECO2.BA", "Telecom Argentina",               "Communication & Media"),
    ("CVH.BA",   "Cablevisión Holding",             "Communication & Media"),
    ("MIRG.BA",  "Mirgor",                          "Industrials"),
    ("COME.BA",  "Sociedad Comercial del Plata",    "Industrials"),
    ("CRES.BA",  "Cresud",                          "Consumer Staples"),
    ("MELI",     "MercadoLibre",                    "Consumer Discretionary"),
])
# Brasil — large-caps de B3 (sufijo .SA).
_BRAZIL = _b("Brazil", "Latin America", [
    ("PETR4.SA", "Petrobras",            "Energy"),
    ("PRIO3.SA", "PRIO",                 "Energy"),
    ("VBBR3.SA", "Vibra Energia",        "Energy"),
    ("VALE3.SA", "Vale",                 "Materials"),
    ("SUZB3.SA", "Suzano",               "Materials"),
    ("GGBR4.SA", "Gerdau",               "Materials"),
    ("ITUB4.SA", "Itaú Unibanco",        "Financial Services"),
    ("BBDC4.SA", "Bradesco",             "Financial Services"),
    ("BBAS3.SA", "Banco do Brasil",      "Financial Services"),
    ("B3SA3.SA", "B3 (Bolsa Brasil)",    "Financial Services"),
    ("ITSA4.SA", "Itaúsa",               "Financial Services"),
    ("BBSE3.SA", "BB Seguridade",        "Financial Services"),
    ("ABEV3.SA", "Ambev",                "Consumer Staples"),
    ("JBSS3.SA", "JBS",                  "Consumer Staples"),
    ("WEGE3.SA", "WEG",                  "Industrials"),
    ("EMBR3.SA", "Embraer",              "Industrials"),
    ("RENT3.SA", "Localiza",             "Consumer Discretionary"),
    ("MGLU3.SA", "Magazine Luiza",       "Consumer Discretionary"),
    ("RADL3.SA", "Raia Drogasil",        "Healthcare"),
    ("ELET3.SA", "Eletrobras",           "Utilities"),
    ("EQTL3.SA", "Equatorial Energia",   "Utilities"),
])


# ============================================================
# Catálogo completo + índices
# ============================================================
CATALOG: tuple[Company, ...] = tuple(
    _UNITED_STATES
    + _FRANCE + _GERMANY + _UK + _NETHERLANDS + _SWITZERLAND
    + _SPAIN + _ITALY + _DENMARK
    + _JAPAN + _HONG_KONG + _KOREA + _TAIWAN + _INDIA
    + _ARGENTINA + _BRAZIL
)

_REGION_ORDER = ("North America", "Europe", "Asia", "Latin America")
# Países en orden de display — agrupados por región, región en orden.
_COUNTRY_ORDER: tuple[str, ...] = (
    "United States",
    "France", "Germany", "United Kingdom", "Netherlands", "Switzerland",
    "Spain", "Italy", "Denmark",
    "Japan", "Hong Kong", "South Korea", "Taiwan", "India",
    "Argentina", "Brazil",
)

_BY_TICKER: dict[str, Company] = {c.ticker: c for c in CATALOG}


# ============================================================
# API pública
# ============================================================
def regions() -> list[str]:
    """Regiones en orden de display."""
    return list(_REGION_ORDER)


def countries(region: str | None = None) -> list[str]:
    """Países en orden de display. Si ``region`` se da, sólo los de esa
    región."""
    present = {c.country for c in CATALOG
               if region is None or c.region == region}
    return [c for c in _COUNTRY_ORDER if c in present]


def sectors(country: str) -> list[str]:
    """Sectores presentes en ``country``, en orden de taxonomía."""
    present = {c.sector for c in CATALOG if c.country == country}
    ordered = [s for s in _SECTOR_ORDER if s in present]
    # Sectores fuera de la taxonomía (defensivo) — al final, alfabéticos.
    extra = sorted(present - set(_SECTOR_ORDER))
    return ordered + extra


def companies(country: str, sector: str) -> list[Company]:
    """Empresas de ``country`` + ``sector``, ordenadas por nombre."""
    out = [c for c in CATALOG
           if c.country == country and c.sector == sector]
    return sorted(out, key=lambda c: c.name.lower())


def company_for(ticker: str) -> Company | None:
    """La ``Company`` de un ticker (case-insensitive), o ``None``."""
    return _BY_TICKER.get((ticker or "").upper()) or _BY_TICKER.get(ticker)


def all_companies() -> tuple[Company, ...]:
    """El catálogo completo."""
    return CATALOG


def universe_by_region(region: str) -> dict[str, str]:
    """``{ticker: name}`` de una región — compatibilidad con el selector
    por región de la página de Equity Analysis."""
    return {c.ticker: c.name for c in CATALOG if c.region == region}


def region_of_ticker(ticker: str) -> str:
    """Región a la que pertenece un ticker; ``North America`` ante un
    ticker desconocido (fallback seguro)."""
    c = company_for(ticker)
    return c.region if c is not None else "North America"


# Sufijos de bolsa cuyos emisores reportan en una moneda con inflación
# crónica alta. Los estados en moneda nominal hacen poco confiable un
# DCF (los ingresos "crecen" 100%+/año sólo por inflación); ajustarlo
# bien requeriría deflactar las series por IPC — fuera del alcance.
_HIGH_INFLATION_SUFFIXES = (".BA",)        # BYMA — Argentina, en pesos


def is_high_inflation_ticker(ticker: str) -> bool:
    """``True`` si el ticker cotiza en un mercado cuya MONEDA DE REPORTE
    tiene inflación crónica alta.

    La valuación intrínseca (DCF, múltiplos) sobre estados en moneda
    nominal de estos mercados no es confiable — el caller debería
    omitirla o avisarle al usuario.

    Clave: la moneda de reporte, NO la nacionalidad de la empresa. Se
    detecta por sufijo de bolsa (``.BA`` = BYMA, reporta en pesos). Una
    empresa argentina que cotiza en NASDAQ y reporta en dólares (MELI)
    NO entra acá — sus estados están en una moneda estable."""
    return (ticker or "").upper().endswith(_HIGH_INFLATION_SUFFIXES)
