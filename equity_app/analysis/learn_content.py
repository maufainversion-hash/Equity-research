"""
Academy — contenido curado (sin AI).

Cada lección es un objeto :class:`Lesson` con definición propia, los
libros canónicos que tratan el tema, charlas/lecturas en video,
citas atribuidas a inversores y académicos reconocidos
(Buffett, Graham, Marks, Damodaran, Munger, Klarman, Lynch, Fisher,
Dalio), casos reales y errores comunes.

Fuentes consultadas para el currículum:
- *Security Analysis* (Graham + Dodd, 1934)
- *The Intelligent Investor* (Graham, 1949)
- *Investment Valuation* (Damodaran, 3rd ed.)
- *Valuation: Measuring and Managing the Value of Companies* (Koller,
  Goedhart, Wessels — McKinsey)
- *The Most Important Thing* (Howard Marks)
- *Mastering the Market Cycle* (Howard Marks)
- *Margin of Safety* (Seth Klarman, 1991)
- *One Up On Wall Street* (Peter Lynch)
- *Common Stocks and Uncommon Profits* (Phil Fisher)
- *Berkshire Hathaway Annual Letters* (Warren Buffett, 1977-presente)
- *Principles* + *Big Debt Crises* (Ray Dalio)
- *CFA Institute Body of Knowledge* (Levels I-III)
- *JP Morgan Guide to the Markets* (quarterly)

Diseño:
- Contenido estático en este módulo (zero API calls, instantáneo).
- ``get_lesson(slug)`` devuelve ``Lesson | None``.
- ``CATALOG`` mantiene la misma estructura que la versión AI para
  que la página no tenga que cambiar lo demás.
- Algunos temas tienen contenido completo; otros son stubs con
  libros + videos recomendados — la página marca cuáles están
  completos.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


# ============================================================
# Data structure
# ============================================================
@dataclass(frozen=True)
class Book:
    title: str
    author: str
    year: Optional[int] = None
    chapter_hint: str = ""              # capítulo / sección relevante
    why: str = ""                       # por qué leerlo para este tema


@dataclass(frozen=True)
class Video:
    title: str
    channel: str
    url: str = ""
    minutes: Optional[int] = None
    why: str = ""


@dataclass(frozen=True)
class Quote:
    text: str
    author: str
    source: str = ""                    # libro / carta / discurso


@dataclass
class Lesson:
    slug: str
    label: str
    category: str
    hook: str

    # Texto principal (escrito a mano, no generado por AI).
    definition: str = ""
    why_matters: str = ""
    how_pros_analyze: str = ""
    key_metrics: list[tuple[str, str]] = field(default_factory=list)   # (nombre, explicación)
    bullish_vs_bearish: list[tuple[str, str]] = field(default_factory=list)  # (bull, bear)
    valuation_impact: str = ""
    case_study: str = ""
    common_mistakes: list[str] = field(default_factory=list)
    mental_model: str = ""

    # Fuentes externas
    books: list[Book] = field(default_factory=list)
    videos: list[Video] = field(default_factory=list)
    quotes: list[Quote] = field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        """Una lección está "completa" si tiene definición + métricas
        + al menos un libro y una cita. El resto es nice-to-have."""
        return bool(
            self.definition and self.key_metrics
            and self.books and self.quotes
        )


# ============================================================
# Topic catalog — categoría → [(slug, label, hook)]
# (idéntico al de la versión AI para no romper el resto de la app)
# ============================================================
CATALOG: dict[str, list[tuple[str, str, str]]] = {
    "📊 Empresas": [
        ("revenue_growth",       "Revenue growth",         "Calidad del crecimiento: orgánico, M&A, FX, mix"),
        ("margins",              "Márgenes",               "Gross / operating / net — qué dicen sobre el moat"),
        ("operating_leverage",   "Operating leverage",     "Por qué pequeños cambios en revenue mueven mucho la utilidad"),
        ("free_cash_flow",       "Free Cash Flow",         "El número que más mira un buy-side senior"),
        ("roic",                 "ROIC",                   "Retorno sobre capital invertido vs WACC — value creation"),
        ("roe",                  "ROE · DuPont",           "Descomposición y trampas (apalancamiento que disfraza)"),
        ("debt_analysis",        "Análisis de deuda",      "Coverage, maturity walls, refinancing risk"),
        ("dilution",             "Dilución (SBC + raises)", "Cómo erosiona retornos sin que se note"),
        ("moats",                "Moats económicos",       "Network effects, switching costs, scale, brand"),
        ("unit_economics",       "Unit economics",         "CAC, LTV, payback — para entender modelos SaaS / consumer"),
        ("pricing_power",        "Pricing power",          "Cómo detectarlo antes de que aparezca en el P&L"),
        ("earnings_quality",     "Calidad de earnings",    "Accruals, working capital, non-recurring"),
        ("capital_allocation",   "Capital allocation",     "Buybacks vs dividendos vs capex vs M&A"),
        ("guidance",             "Guidance de management", "Cómo leer entre líneas en earnings calls"),
        ("cyclicality",          "Ciclicidad",             "Normalizar earnings para no comprar peaks"),
        ("competitive_advantages", "Ventajas competitivas", "Por qué duran las que duran"),
        ("saas_metrics",         "SaaS metrics",           "ARR, NRR, magic number, rule of 40"),
        ("banking_metrics",      "Bancos · métricas",      "NIM, efficiency, NPL, CET1, ROTE"),
        ("insurance_metrics",    "Aseguradoras · métricas", "Combined ratio, float, reserves"),
        ("semis_metrics",        "Semis · métricas",       "Inventory days, design wins, capex intensity"),
        ("consumer_brands",      "Consumer brands",        "Brand equity, market share, pricing premium"),
        ("network_effects",      "Network effects",        "Por qué hay winner-takes-most en algunos modelos"),
    ],
    "💰 Valuación": [
        ("dcf",                  "DCF",                    "El framework, sus assumptions críticas y cuándo NO usarlo"),
        ("multiples_overview",   "Múltiplos · overview",   "Cuándo cada múltiplo y por qué"),
        ("ev_ebitda",            "EV/EBITDA",              "Por qué prefieren EV vs P/E en industriales / leverage"),
        ("pe_ratio",             "P/E",                    "El más usado y el más mal usado"),
        ("peg",                  "PEG",                    "Growth-adjusted — cuándo es trampa"),
        ("sotp",                 "Sum-of-the-parts",       "Conglomerados, hidden value, holding discount"),
        ("terminal_value",       "Terminal value",         "El 70% del DCF — qué assumptions importan"),
        ("sensitivity_analysis", "Sensitivity analysis",   "WACC × g terminal — leer la matriz como pro"),
        ("scenario_analysis",    "Scenario analysis",      "Bull / base / bear — no es promediar es discriminar"),
        ("intrinsic_value",      "Intrinsic value",        "El concepto Damodaranista — value vs price"),
        ("margin_of_safety",     "Margin of safety",       "Graham, Buffett, Marks — la única defensa real"),
    ],
    "🏛️ Sectores": [
        ("sector_banks",         "Bancos",                 "P/TBV, ROTE, sensibilidad a curva, credit losses"),
        ("sector_tech",          "Tecnológicas",           "Growth-at-scale, rule of 40, valuation por etapa"),
        ("sector_utilities",     "Utilities",              "Regulated returns, rate base, allowed ROE"),
        ("sector_energy",        "Energía",                "Reservas, breakeven price, capital intensity"),
        ("sector_consumer",      "Consumo masivo",         "Pricing, volumes, brand equity, EM exposure"),
        ("sector_industrials",   "Industriales",           "Backlog, book-to-bill, ciclo capex"),
        ("sector_healthcare",    "Healthcare",             "Pipeline, patent cliff, payer mix"),
        ("sector_semis",         "Semiconductores",        "Ciclo, lead times, capex intensity, geopolitical"),
    ],
    "🌐 Macro & economía": [
        ("inflation",            "Inflación",              "Headline vs core, expectativas, base effects"),
        ("interest_rates",       "Tasas de interés",       "Real vs nominal, curva, impacto en activos"),
        ("yield_curve",          "Yield curve",            "Forma, inversión, predictivo de recesión"),
        ("credit_spreads",       "Credit spreads",         "IG vs HY, leading indicator de stress"),
        ("gdp",                  "GDP",                    "Composición, growth vs nivel, nowcasting"),
        ("unemployment",         "Desempleo",              "U-3, U-6, participation rate, wage growth"),
        ("monetary_policy",      "Política monetaria",     "Fed, ECB, BoJ — herramientas y reaction function"),
        ("fiscal_policy",        "Política fiscal",        "Deficit, debt-to-GDP, fiscal multiplier"),
        ("liquidity",            "Liquidez",               "M2, reverse repo, RRP, financial conditions"),
        ("business_cycles",      "Ciclos económicos",      "Expansión, peak, contracción, trough — y cómo posicionarse"),
        ("recession_indicators", "Recession indicators",   "Curva, claims, ISM, Sahm rule"),
        ("dollar_strength",      "Dólar (DXY)",            "Driver de EM, commodities, earnings multinacionales"),
        ("commodity_cycles",     "Commodity cycles",       "Super-ciclos, supply response, financialization"),
    ],
    "📈 Mercado": [
        ("risk_on_off",          "Risk-on vs risk-off",    "Cómo se lee el cambio de régimen"),
        ("positioning",          "Positioning",            "CFTC, dealer gamma, fund flows — lo que mueve a corto"),
        ("sentiment",            "Sentiment",              "VIX, put/call, AAII — contrarian vs trend"),
        ("volatility",           "Volatilidad",            "Term structure, vol-of-vol, ATM vs skew"),
        ("earnings_season",      "Earnings season",        "Beats/misses, guidance, reacción del precio"),
        ("institutional_flows",  "Flows institucionales",  "ETFs, mutual funds, hedge funds, retail"),
        ("market_regimes",       "Market regimes",         "Bull, bear, range-bound — y cómo cambia la estrategia"),
        ("factor_investing",     "Factor investing",       "Value, momentum, quality, size, low-vol"),
        ("momentum",             "Momentum",               "El factor con mejor evidencia empírica"),
        ("growth_vs_value",      "Growth vs value",        "Por qué rotan y cuándo"),
    ],
}


def _cat_for(slug: str) -> str:
    for cat, topics in CATALOG.items():
        for s, _, _ in topics:
            if s == slug:
                return cat
    return ""


def _hook_for(slug: str) -> str:
    for _, topics in CATALOG.items():
        for s, _, hook in topics:
            if s == slug:
                return hook
    return ""


def _label_for(slug: str) -> str:
    for _, topics in CATALOG.items():
        for s, label, _ in topics:
            if s == slug:
                return label
    return slug


def all_topics() -> list[tuple[str, str, str, str]]:
    """Flat list of (category, slug, label, hook)."""
    out: list[tuple[str, str, str, str]] = []
    for cat, topics in CATALOG.items():
        for slug, label, hook in topics:
            out.append((cat, slug, label, hook))
    return out


def find_topic(slug: str) -> Optional[tuple[str, str, str, str]]:
    for cat, topics in CATALOG.items():
        for s, label, hook in topics:
            if s == slug:
                return (cat, s, label, hook)
    return None


# ============================================================
# Reusable book references (canónicos del currículum)
# ============================================================
_BOOK_INTELLIGENT_INVESTOR = Book(
    title="The Intelligent Investor",
    author="Benjamin Graham",
    year=1949,
    chapter_hint="Cap. 8 (Mr. Market) y cap. 20 (Margin of Safety)",
    why="La biblia del value investing. Buffett dijo que es 'by far the best book on investing ever written'.",
)
_BOOK_SECURITY_ANALYSIS = Book(
    title="Security Analysis",
    author="Benjamin Graham & David Dodd",
    year=1934,
    chapter_hint="Parte VI (Analysis of the Income Account) y parte VII (Balance Sheet)",
    why="Texto fundacional del análisis de estados financieros. Denso pero el original.",
)
_BOOK_DAMODARAN_VALUATION = Book(
    title="Investment Valuation",
    author="Aswath Damodaran",
    year=2012,
    chapter_hint="Cap. 4 (Free Cash Flow), 12 (DCF) y 17 (Real Options)",
    why="El manual moderno de valuación. Damodaran enseña qué assumption importa más en cada modelo.",
)
_BOOK_MCKINSEY_VALUATION = Book(
    title="Valuation: Measuring and Managing the Value of Companies",
    author="Koller, Goedhart & Wessels (McKinsey)",
    year=2020,
    chapter_hint="Parte 1 (Foundations) y parte 2 (Core Valuation Techniques)",
    why="El estándar de oro corporate-side. Conecta valor con value drivers operativos (ROIC + crecimiento).",
)
_BOOK_MARKS_MOST_IMPORTANT = Book(
    title="The Most Important Thing",
    author="Howard Marks",
    year=2011,
    chapter_hint="Cap. 5 (Risk) y cap. 19 (The Most Important Thing)",
    why="Lo más cercano a un curso de inversión escrito por el CIO de Oaktree.",
)
_BOOK_MARKS_MARKET_CYCLE = Book(
    title="Mastering the Market Cycle",
    author="Howard Marks",
    year=2018,
    chapter_hint="Cap. 4-8 (the cycles in profits, attitudes, credit, real estate)",
    why="Cómo leer el ciclo desde el psicológico hasta el de crédito. Esencial para macro/regime.",
)
_BOOK_KLARMAN_MOS = Book(
    title="Margin of Safety",
    author="Seth Klarman",
    year=1991,
    chapter_hint="Cap. 6 (Value Investing) y cap. 7 (Identifying Investment Opportunities)",
    why="Out-of-print pero leyenda. El value investing institucional del Baupost Group.",
)
_BOOK_LYNCH = Book(
    title="One Up On Wall Street",
    author="Peter Lynch",
    year=1989,
    chapter_hint="Cap. 8 (Categorías de stocks) y cap. 13 (Earnings)",
    why="Cómo un retail puede usar lo que ve todos los días como edge analítico.",
)
_BOOK_FISHER = Book(
    title="Common Stocks and Uncommon Profits",
    author="Philip Fisher",
    year=1958,
    chapter_hint="Los '15 puntos' del cap. 3 — qué buscar en una empresa",
    why="Padre del growth investing. Buffett dice que es 85% Graham + 15% Fisher.",
)
_BOOK_DALIO_PRINCIPLES = Book(
    title="Principles for Navigating Big Debt Crises",
    author="Ray Dalio",
    year=2018,
    chapter_hint="Parte 2 (Archetypal Long-Term Debt Cycle)",
    why="El framework macro de Bridgewater para entender ciclos largos. Disponible gratis en PDF en su sitio.",
)
_BOOK_BUFFETT_LETTERS = Book(
    title="Berkshire Hathaway Annual Letters",
    author="Warren Buffett",
    year=None,
    chapter_hint="1977-2023 — todas disponibles en berkshirehathaway.com",
    why="Masterclass anual de capital allocation, moats, riesgo y temperamento. Gratis.",
)
_BOOK_CFA = Book(
    title="CFA Program Curriculum (Levels I-III)",
    author="CFA Institute",
    year=None,
    chapter_hint="Equity Investments + Financial Reporting + Quantitative Methods",
    why="Currículum oficial. No tan divertido como Buffett pero exhaustivo y estandarizado.",
)
_BOOK_JPM_GUIDE = Book(
    title="JP Morgan Guide to the Markets",
    author="JP Morgan Asset Management",
    year=None,
    chapter_hint="Edición trimestral más reciente",
    why="40 páginas de charts macro/sector/valuación. Gratis cada trimestre en su sitio.",
)


# ============================================================
# Reusable video references
# ============================================================
_VIDEO_DAMODARAN_VALUATION = Video(
    title="Foundations of Valuation (NYU Stern · curso completo)",
    channel="Aswath Damodaran",
    url="https://www.youtube.com/playlist?list=PLUkh9m2BorqnKWu0g5ZUps_CbQ-JGtbI9",
    minutes=1200,
    why="El curso entero de valuación de Damodaran en NYU Stern, gratis.",
)
_VIDEO_DAMODARAN_CORPFIN = Video(
    title="Corporate Finance · NYU Stern",
    channel="Aswath Damodaran",
    url="https://www.youtube.com/playlist?list=PLUkh9m2BorqkQjjjf36KOdvHC3HOZNkPo",
    minutes=900,
    why="Mismo profesor, lente de empresa: cómo deciden las firmas qué proyectos hacer.",
)
_VIDEO_BUFFETT_1996 = Video(
    title="Warren Buffett · Talk to MBA Students at University of Florida",
    channel="William Green (clip clásico)",
    url="https://www.youtube.com/watch?v=2MHIcabnjrA",
    minutes=90,
    why="Probablemente la mejor charla de Buffett. Cubre moats, capital allocation y temperamento.",
)
_VIDEO_MARKS_MEMOS = Video(
    title="Howard Marks Memos · Oaktree (lectura) + YouTube channel",
    channel="Oaktree Capital",
    url="https://www.oaktreecapital.com/insights/memos",
    minutes=None,
    why="Sus memos cuatrimestrales son the closest thing to a Buffett letter equivalent.",
)


# ============================================================
# Reusable quotes (atribuidas + verificables)
# ============================================================
_Q_BUFFETT_PRICE_VALUE = Quote(
    text="Price is what you pay. Value is what you get.",
    author="Warren Buffett",
    source="Berkshire Hathaway 2008 letter (atribuido a Graham, popularizado por Buffett)",
)
_Q_BUFFETT_MOAT = Quote(
    text="The most important thing is trying to find a business with a wide and long-lasting moat around it… protecting a terrific economic castle with an honest lord in charge of the castle.",
    author="Warren Buffett",
    source="1999 Fortune interview",
)
_Q_BUFFETT_TIME = Quote(
    text="Our favorite holding period is forever.",
    author="Warren Buffett",
    source="Berkshire Hathaway 1988 letter",
)
_Q_GRAHAM_MOS = Quote(
    text="The margin of safety is always dependent on the price paid.",
    author="Benjamin Graham",
    source="The Intelligent Investor, ch. 20",
)
_Q_MARKS_RISK = Quote(
    text="Risk means more things can happen than will happen.",
    author="Howard Marks",
    source="The Most Important Thing, paraphrased from Elroy Dimson",
)
_Q_DAMODARAN_STORY = Quote(
    text="A valuation is a bridge between story and numbers. If your numbers don't match your story, one of the two is wrong.",
    author="Aswath Damodaran",
    source="Narrative and Numbers (2017)",
)
_Q_MUNGER_INCENTIVES = Quote(
    text="Show me the incentive and I will show you the outcome.",
    author="Charlie Munger",
    source="Poor Charlie's Almanack",
)
_Q_LYNCH_INVERT = Quote(
    text="Know what you own, and know why you own it.",
    author="Peter Lynch",
    source="One Up On Wall Street",
)


# ============================================================
# LESSONS — content for the full topics
# ============================================================
_LESSONS: dict[str, Lesson] = {}


def _add(lesson: Lesson) -> None:
    _LESSONS[lesson.slug] = lesson


# ---------- Free Cash Flow ----------
_add(Lesson(
    slug="free_cash_flow",
    label=_label_for("free_cash_flow"),
    category=_cat_for("free_cash_flow"),
    hook=_hook_for("free_cash_flow"),
    definition=(
        "Free Cash Flow (FCF) es el dinero que queda en la caja después "
        "de que la empresa paga todos los gastos operativos, impuestos y "
        "reinversión necesaria (CapEx). Es el efectivo que el management "
        "puede usar para pagar deuda, recomprar acciones, repartir "
        "dividendos o acumular. A diferencia del net income — que está "
        "lleno de items contables (D&A, accruals, ganancias por venta de "
        "activos) — el FCF es lo que un dueño privado realmente se "
        "podría llevar a casa.\n\n"
        "Fórmula simple: **FCF = Operating Cash Flow − CapEx**.\n"
        "Versión Damodaran (FCFF): EBIT(1−t) + D&A − ΔWC − CapEx."
    ),
    why_matters=(
        "Es la base del DCF (el modelo de valuación más usado en buy-side "
        "institucional). Una empresa puede reportar utilidades crecientes "
        "y aún así quemar caja — esto fue el patrón de WeWork, "
        "Peloton durante el COVID, muchas SaaS pre-IPO. El FCF es el "
        "shield contra la contabilidad creativa. Buffett mira 'owner "
        "earnings' (su versión de FCF) antes que el net income."
    ),
    how_pros_analyze=(
        "1. **Tendencia plurianual**: 5-10 años de FCF, no un año aislado. "
        "Empresas cíclicas en peak earnings tienen FCF inflado.\n"
        "2. **FCF conversion**: FCF / Net Income. Una empresa de calidad "
        "convierte 80%+ del net income en caja. <50% es bandera roja.\n"
        "3. **Margen de FCF**: FCF / Revenue. Visa, Mastercard, MSCI tienen "
        "márgenes de FCF >40%; industriales en zona 5-10%.\n"
        "4. **Stock-based compensation (SBC)**: ajustar FCF restando SBC "
        "real. Muchas tech reportan 'adjusted FCF' que oculta dilución.\n"
        "5. **Working capital quality**: si OCF crece por estirar a "
        "proveedores o adelantar cobros, no es sostenible."
    ),
    key_metrics=[
        ("Free Cash Flow (USD)",
         "OCF − CapEx. La cifra absoluta. Mirar tendencia 5y."),
        ("FCF margin (%)",
         "FCF / Revenue. >20% = capital-light excellent. <5% = capital-intensive."),
        ("FCF conversion (%)",
         "FCF / Net Income. >80% = limpio. <50% = revisar accruals."),
        ("FCF per share (USD)",
         "FCF / shares. Útil para empresas con buybacks agresivos (ej. Apple)."),
        ("FCF yield (%)",
         "FCF / Market Cap. Inverso al P/FCF. >5% = barato en términos absolutos."),
    ],
    bullish_vs_bearish=[
        ("FCF crece 5+ años seguidos sin acquisitions",
         "FCF estancado o cae mientras revenue crece"),
        ("Conversion 80-100% del net income",
         "Conversion <50% — accruals altos, ¿earnings management?"),
        ("Stable / decreasing CapEx % revenue",
         "CapEx creciendo más rápido que revenue (capex bingo)"),
        ("Buybacks netos consistentes con FCF",
         "Buybacks financiados con deuda mientras FCF cae"),
        ("Working capital eficiente (CCC estable)",
         "OCF aumenta solo por estirar payables (CCC se alarga)"),
    ],
    valuation_impact=(
        "El DCF descuenta FCF futuros: si tu estimación de FCF es 10% "
        "más alta, tu valor intrínseco también. Sensibilidad típica: "
        "1pp en FCF margin → 5-15% en intrinsic value depending on stage. "
        "Empresas con FCF predecible (Coca-Cola, Microsoft) merecen "
        "multiples más altos que las de FCF errático (aerolíneas, "
        "shipping). El FCF también determina la sustentabilidad de "
        "dividendos: payout ratio en función del FCF, no del net income."
    ),
    case_study=(
        "**Apple FY2024**: revenue $391B, net income $94B, OCF $118B, "
        "CapEx $9.5B → FCF $108B. FCF conversion = 115% (mejor que el "
        "net income porque D&A excede CapEx — Apple es capital-light). "
        "FCF margin = 28%. Con esos $108B Apple recompró ~$95B en "
        "acciones y pagó $15B en dividendos. Ese es el modelo de "
        "capital allocation que Buffett admira: convertir earnings en "
        "caja y devolverla a los dueños.\n\n"
        "**Contraejemplo — WeWork pre-IPO**: revenue crecía 100% YoY "
        "pero FCF era −$1.9B/año. El modelo necesitaba reinversión "
        "constante para sostener el crecimiento. La S-1 mostró que "
        "nunca había generado caja positiva. La oferta colapsó."
    ),
    common_mistakes=[
        "Confundir net income con cash flow — son fundamentalmente distintos.",
        "Usar 'adjusted FCF' que excluye stock-based compensation. SBC es un costo real (dilución).",
        "Comparar FCF de un año peak vs uno trough en empresas cíclicas. Siempre normalizar.",
        "Ignorar CapEx de mantenimiento vs CapEx de crecimiento. El de mantenimiento es no-negociable.",
        "Asumir que OCF creciente es bueno cuando solo crece por estirar working capital.",
    ],
    mental_model=(
        "Pensá en FCF como en el cheque que la empresa te firmaría si vos "
        "fueras el único dueño. ¿Cuánto te podrías llevar a casa sin "
        "comprometer el negocio? Esa pregunta filtra el 90% del ruido "
        "contable. Los grandes inversores no compran empresas — compran "
        "futuros flujos de caja descontados a una tasa exigente."
    ),
    books=[_BOOK_DAMODARAN_VALUATION, _BOOK_MCKINSEY_VALUATION,
           _BOOK_BUFFETT_LETTERS],
    videos=[_VIDEO_DAMODARAN_VALUATION,
            Video(title="Why Free Cash Flow Matters More Than Earnings",
                  channel="The Plain Bagel", minutes=12,
                  url="https://www.youtube.com/c/ThePlainBagel",
                  why="Intro accesible para retail.")],
    quotes=[_Q_DAMODARAN_STORY,
            Quote(text="The value of any asset is the present value of "
                       "its expected future cash flows.",
                  author="Aswath Damodaran", source="Investment Valuation"),
            _Q_BUFFETT_PRICE_VALUE],
))


# ---------- ROIC ----------
_add(Lesson(
    slug="roic",
    label=_label_for("roic"),
    category=_cat_for("roic"),
    hook=_hook_for("roic"),
    definition=(
        "Return on Invested Capital (ROIC) mide cuánta ganancia "
        "operativa después de impuestos genera la empresa por cada "
        "dólar de capital invertido (deuda + equity). Es la métrica "
        "que mejor captura la **eficiencia operacional real**, "
        "independiente de la estructura de capital.\n\n"
        "Fórmula: **ROIC = NOPAT / Invested Capital**\n"
        "  · NOPAT = EBIT × (1 − tax rate)\n"
        "  · Invested Capital = Total Equity + Total Debt − Cash\n\n"
        "La regla de oro: una empresa solo crea valor cuando "
        "**ROIC > WACC** (el costo de su capital). Cualquier "
        "crecimiento por debajo de WACC destruye valor."
    ),
    why_matters=(
        "Es la métrica favorita de la escuela de McKinsey (Koller) y de "
        "Buffett. Le dice al inversor si el negocio es realmente bueno o "
        "solo grande. Una empresa con ROIC 25% y crecimiento 5% crea más "
        "valor que una con ROIC 10% y crecimiento 15%. La razón: "
        "el spread (ROIC − WACC) × Invested Capital ES la economic value "
        "added (EVA) que captura cada año."
    ),
    how_pros_analyze=(
        "1. **Spread vs WACC**: ROIC − WACC. Esa diferencia es la 'economic "
        "rent' del negocio. >5pp consistente = moat real.\n"
        "2. **ROIC trend 10y**: ¿el moat se ensancha o se erosiona? "
        "Empresas con ROIC declinante (Intel últimos 10y) pierden "
        "competitividad aunque revenue siga creciendo.\n"
        "3. **ROIC vs peers en la misma industria**: comparar Mastercard "
        "vs Visa, no vs Boeing. Cada sector tiene su 'normal'.\n"
        "4. **Excluir goodwill**: ROIC pre-goodwill mide la performance del "
        "core business; ROIC con goodwill incluido mide qué tan bien "
        "asignó capital el management vía M&A.\n"
        "5. **NOPAT ajustado**: capitalizar R&D y leases operativos "
        "(post-IFRS 16 los leases ya están en balance, pero las decisiones "
        "previas distorsionan comparaciones históricas)."
    ),
    key_metrics=[
        ("ROIC (%)",
         "NOPAT / Invested Capital. >15% excelente · 10-15% bueno · "
         "<WACC destruye valor."),
        ("ROIC − WACC (pp)",
         "El spread real. >5pp es señal de moat duro."),
        ("ROIC ex-goodwill",
         "Calidad del negocio core (sin distorsión de M&A)."),
        ("Incremental ROIC",
         "ΔNOPAT / ΔInvested Capital. ¿El nuevo capital rinde tanto como "
         "el viejo? Damodaran lo llama 'marginal ROIC'."),
        ("ROIC durability",
         "Cuántos años se mantiene en >20%. Lo que dura es lo valioso."),
    ],
    bullish_vs_bearish=[
        ("ROIC 20%+ consistente 10 años",
         "ROIC erosiona año tras año aunque revenue crezca"),
        ("Spread ROIC−WACC ≥ 5pp",
         "ROIC < WACC (la empresa destruye valor con cada inversión)"),
        ("Incremental ROIC ≥ historical ROIC",
         "Incremental ROIC cae bruscamente (saturación / mal capital allocation)"),
        ("ROIC ex-goodwill > ROIC con goodwill (M&A disciplinada)",
         "ROIC con goodwill <<< ex-goodwill (overpaid en M&A)"),
        ("Moat detectable (network, switching, scale, brand)",
         "Returns altos pero sin moat identificable — atraerá competencia"),
    ],
    valuation_impact=(
        "En el framework Koller/McKinsey: **Value = Invested Capital × "
        "(1 + (ROIC − g) / (WACC − g))** para steady state. ROIC alto + "
        "g modesto > ROIC bajo + g alto. Por eso Mastercard cotiza a "
        "30x earnings con crecimiento 12% y un retailer a 10x con "
        "crecimiento 8% — la diferencia es ROIC.\n\n"
        "En DCF: el terminal value depende del 'reinvestment rate' = g / ROIC. "
        "Si asumís ROIC alto, necesitás reinvertir poco para sostener "
        "crecimiento → más FCF disponible → más valor."
    ),
    case_study=(
        "**Mastercard FY2024**: ROIC ~85% (sí, ochenta y cinco). "
        "Capital intensity casi cero (red de pagos + software, no "
        "infraestructura física). El spread vs WACC ~10% es ~78pp — "
        "uno de los moats más anchos del S&P. Por eso cotiza a P/E 35+ "
        "con crecimiento de 'solo' 12% YoY.\n\n"
        "**Contraejemplo — Intel últimos 10 años**: ROIC pasó de "
        "~22% (2015) a ~5% (2024). Aumentó capex en foundries para "
        "competir con TSMC pero el rendimiento incremental es bajo. "
        "Mercado descuenta esto: P/E vs TSMC se invirtió completamente."
    ),
    common_mistakes=[
        "Mirar ROE en lugar de ROIC. ROE incluye apalancamiento — un banco quebrado puede tener ROE alto antes de quebrar.",
        "Comparar ROIC entre industrias. Software vs manufacturing son juegos distintos.",
        "Ignorar el ROIC incremental. Una empresa puede tener ROIC promedio alto pero el último capital invertido rinde mucho menos.",
        "Confundir ROIC alto con seguridad. ROIC alto sin moat = imán para competencia.",
        "Pasar por alto que las acquisitions inflan invested capital con goodwill. Comparar pre/post.",
    ],
    mental_model=(
        "Buffett: 'El test definitivo de la dirección es lo que pasa con cada "
        "dólar de retained earnings. Una buena empresa lo convierte en "
        "más de un dólar de market value.' Eso es ROIC > WACC en idioma "
        "Buffett. Si una empresa rinde 20% sobre el capital invertido y vos "
        "le exigís 8%, cada dólar de inversión vale ~$2.50 en valor "
        "intrínseco (perpetuity simplified)."
    ),
    books=[_BOOK_MCKINSEY_VALUATION, _BOOK_BUFFETT_LETTERS,
           _BOOK_DAMODARAN_VALUATION],
    videos=[_VIDEO_DAMODARAN_CORPFIN,
            Video(title="The McKinsey Valuation Framework (Tim Koller)",
                  channel="McKinsey & Company", minutes=45,
                  url="https://www.mckinsey.com/capabilities/strategy-and-corporate-finance/our-insights",
                  why="Koller, autor de Valuation, explica ROIC + g + WACC.")],
    quotes=[
        Quote(text="Over the long term, it's hard for a stock to earn a "
                   "much better return than the business which underlies "
                   "it earns. If the business earns 6% on capital over 40 "
                   "years and you hold it for those 40 years, you're not "
                   "going to make much different than a 6% return.",
              author="Charlie Munger",
              source="USC Business School speech (1994)"),
        _Q_BUFFETT_MOAT,
        Quote(text="The first rule of compounding: never interrupt it "
                   "unnecessarily.",
              author="Charlie Munger", source="Poor Charlie's Almanack"),
    ],
))


# ---------- DCF ----------
_add(Lesson(
    slug="dcf",
    label=_label_for("dcf"),
    category=_cat_for("dcf"),
    hook=_hook_for("dcf"),
    definition=(
        "Discounted Cash Flow (DCF) calcula el valor intrínseco de una "
        "empresa como el valor presente de sus flujos de caja futuros, "
        "descontados a una tasa que refleja el riesgo. Es la encarnación "
        "matemática de la idea de Graham/Williams: 'el valor de cualquier "
        "activo es el valor presente de los flujos de caja que generará "
        "en el resto de su vida'.\n\n"
        "Estructura básica:\n"
        "  · Proyectar FCF para N años explícitos (típico 5-10).\n"
        "  · Calcular un terminal value para todo lo que viene después.\n"
        "  · Descontar todo al presente usando el WACC.\n"
        "  · Restar deuda neta, dividir por shares → intrinsic value por acción."
    ),
    why_matters=(
        "DCF te obliga a hacer explícitas las assumptions que el mercado "
        "está descontando: crecimiento, márgenes, reinversión, riesgo. "
        "Si el precio de mercado implica 25% de crecimiento durante 10 "
        "años, vos sabés qué tan ambicioso es eso vs el historial. El "
        "DCF no es para 'comprar cuando intrinsic > price' mecánicamente — "
        "es para entender la **brecha entre narrativa y números** "
        "(Damodaran)."
    ),
    how_pros_analyze=(
        "1. **3-stage DCF** (Damodaran/Koller): high growth → fade → terminal. "
        "Reflejaa la realidad: las empresas no crecen 30% para siempre.\n"
        "2. **Terminal value scrutiny**: en un DCF típico, 60-80% del valor "
        "está en el TV. Si vos no entendés tu g_terminal (≤ growth nominal "
        "del economy, típicamente 2-3%) tu DCF es ruido.\n"
        "3. **Sensitivity matrix**: WACC × g terminal en una grilla 5×5. "
        "Si una variación de 50bp en WACC mueve el intrinsic 30%, tu "
        "modelo es frágil — cobrá ese riesgo con margin of safety mayor.\n"
        "4. **Reverse DCF**: solvé para qué crecimiento implica el precio "
        "actual. Damodaran prefiere esto al DCF normal — más honesto.\n"
        "5. **No usar DCF para bancos / aseguradoras / REITs**: requieren "
        "modelos especializados (RI, DDM, FFO multiples)."
    ),
    key_metrics=[
        ("WACC", "Costo promedio ponderado del capital. CAPM + cost of debt."),
        ("g (high growth)", "Crecimiento de la fase explícita — anclado al histórico."),
        ("g (terminal)", "Crecimiento perpetuo. Hard cap = growth nominal del PIB (~2-3%)."),
        ("Reinvestment rate", "g / ROIC. Cuánto del NOPAT se reinvierte para sostener g."),
        ("Terminal value % of total PV", "Si >75%, tu DCF está casi todo en assumptions de muy largo plazo."),
        ("Implied steady-state ROIC", "ROIC en perpetuidad. >25% es asumir un moat extraordinario."),
    ],
    bullish_vs_bearish=[
        ("Sensitivity matrix relativamente plana",
         "Pequeños cambios en WACC/g cambian el intrinsic >25% (modelo frágil)"),
        ("Terminal value <70% del valor total",
         "Terminal value >80% — casi todo el valor en perpetuidad"),
        ("g terminal ≤ crecimiento nominal economy",
         "g terminal > 4% (implica que la empresa pasa al PIB en perpetuidad)"),
        ("Reverse DCF muestra growth implícito alcanzable",
         "Reverse DCF requiere >25% CAGR por 10 años para justificar precio"),
        ("ROIC steady-state plausible (10-15%)",
         "ROIC steady-state >25% sin moat estructural claro"),
    ],
    valuation_impact=(
        "El DCF es self-referential: cambia el WACC 100bp y el intrinsic se "
        "mueve 15-25%. Cambia el g terminal 50bp y se mueve 10-15%. Por eso "
        "Damodaran insiste: no es un punto, es un rango. La mejor práctica "
        "es presentar el DCF junto a una sensitivity matrix y un reverse "
        "DCF — eso da contexto. Un DCF point estimate sin rango es ingenuo."
    ),
    case_study=(
        "**Reverse DCF clásico — Amazon ~2001**: la empresa cotizaba a una "
        "valuación que implicaba mantener crecimiento >40% por 15 años. "
        "El consenso decía 'imposible'. Resultó posible — pero el bear de "
        "2001-2002 ofreció igual una entrada con margin of safety amplio.\n\n"
        "**Contraejemplo — Cisco 2000**: cotizaba a P/E 100+ y el reverse "
        "DCF requería ~35% CAGR por 10 años, en una industria que ya "
        "facturaba $300B globalmente. Era matemáticamente improbable. "
        "Bajó 80% en 2 años."
    ),
    common_mistakes=[
        "Usar terminal growth > crecimiento nominal del PIB. Termina implicando que la empresa absorbe la economía.",
        "Capex de mantenimiento subestimado. Si CapEx < D&A en steady state, la base productiva se erosiona.",
        "Ignorar dilución por SBC. El intrinsic per share se calcula sobre shares diluidos, no las actuales.",
        "Un solo escenario (base case). Bull/base/bear da contexto y probabilidades.",
        "Modelar empresas cíclicas en peak earnings. Hay que normalizar through-the-cycle.",
        "Aplicar DCF a bancos. Usar Residual Income o DDM en su lugar.",
    ],
    mental_model=(
        "Damodaran: 'A DCF model is a story translated into numbers.' Si "
        "tu DCF dice que Tesla vale $1.5T, tu story tiene que sostener "
        "ese número (cuántos autos, qué margen, qué duración del moat). "
        "Si no podés contar la story coherentemente, no creas el número. "
        "El proceso de hacer el DCF vale más que el output — te fuerza "
        "a confrontar tus assumptions."
    ),
    books=[_BOOK_DAMODARAN_VALUATION, _BOOK_MCKINSEY_VALUATION,
           _BOOK_KLARMAN_MOS],
    videos=[_VIDEO_DAMODARAN_VALUATION,
            Video(title="DCF Model in Excel · A to Z (Damodaran)",
                  channel="Aswath Damodaran", minutes=90,
                  url="https://www.youtube.com/user/AswathDamodaran",
                  why="Damodaran arma un DCF desde cero con sus papers."),
            Video(title="Stop Doing DCF Models Wrong",
                  channel="Mario Gabelli / Value Investing community",
                  minutes=30,
                  url="",
                  why="Los errores típicos por los que un DCF da números absurdos.")],
    quotes=[
        _Q_DAMODARAN_STORY,
        Quote(text="The value of a business is the cash it will generate "
                   "between now and judgment day, discounted at an "
                   "appropriate rate.",
              author="Warren Buffett",
              source="Berkshire 1992 letter"),
        _Q_BUFFETT_PRICE_VALUE,
    ],
))


# ---------- Margin of Safety ----------
_add(Lesson(
    slug="margin_of_safety",
    label=_label_for("margin_of_safety"),
    category=_cat_for("margin_of_safety"),
    hook=_hook_for("margin_of_safety"),
    definition=(
        "Margin of safety (MoS) es comprar un activo por **significativamente "
        "menos** que su valor intrínseco estimado. La idea no es 'pagar el "
        "precio justo' — es dejarse espacio para estar equivocado y aún así "
        "ganar plata.\n\n"
        "Fórmula simple: **MoS = (Intrinsic Value − Price) / Intrinsic Value**.\n"
        "Graham buscaba MoS de 30-50%; Klarman pide más; Buffett moderno "
        "acepta menos en negocios de alta calidad."
    ),
    why_matters=(
        "Es la idea más importante de Graham — la que Buffett llama 'las "
        "tres palabras más importantes en inversión'. La razón: tus "
        "estimaciones de intrinsic value SIEMPRE van a estar mal. El "
        "futuro es incierto. La MoS es la única protección sistemática "
        "contra los errores en assumptions, el ciclo económico, y la "
        "mala suerte. Sin MoS, una valuación correcta dejas un retorno "
        "modesto. Con MoS, un análisis equivocado todavía puede dar "
        "ganancias."
    ),
    how_pros_analyze=(
        "1. **No es un descuento al precio — es un descuento al intrinsic**. "
        "Comprar 30% abajo del peak NO es margin of safety si el "
        "intrinsic ya cayó 50%.\n"
        "2. **Más MoS para negocios cíclicos / leveraged / sin moat**. "
        "Una utility regulada con cash flow predecible puede tener "
        "menos MoS que una aerolínea.\n"
        "3. **Usar rango, no punto**: si tu intrinsic es $80-$120 "
        "(rango DCF), el precio debe estar bien debajo de $80 para "
        "tener MoS real.\n"
        "4. **MoS contra el escenario bear, no contra el base**. "
        "Klarman: '¿qué hace este investment en mi peor escenario "
        "razonable?'"
    ),
    key_metrics=[
        ("MoS contra intrinsic point estimate",
         "(Intrinsic − Price) / Intrinsic. Graham: 30%+."),
        ("MoS contra range_p25 (conservador)",
         "(P25 − Price) / Price. Si incluso el escenario cauto deja upside, "
         "hay MoS real."),
        ("MoS contra reverse-DCF implícito",
         "Si el growth implícito por el precio es ≪ tu estimación, "
         "hay MoS."),
        ("Downside symmetry",
         "Worst case loss vs best case gain. Buena inversión: gain/loss > 3:1."),
    ],
    bullish_vs_bearish=[
        ("Price <70% del intrinsic estimate",
         "Price >100% del intrinsic estimate"),
        ("Bear case loss < 30%",
         "Bear case loss >50% — riesgo de ruina permanente"),
        ("Negocio de calidad alta + MoS modesta",
         "Negocio de calidad baja + MoS escaso"),
        ("Multiple options de salida (M&A, recovery, dividend)",
         "Una sola tesis muy específica que debe cumplirse"),
    ],
    valuation_impact=(
        "MoS no es un input de valuación — es un input de **decisión de "
        "compra**. Una empresa con DCF $100 que cotiza a $50 tiene "
        "100% de upside teórico (= 50% MoS). Pero si tu DCF tiene "
        "incertidumbre ±30%, el rango real es $70-$130. A precio $50 "
        "tenés MoS contra el bear case ($70). A precio $90, no la "
        "tenés. La MoS ajusta lo que estás dispuesto a pagar dado "
        "tu nivel de confianza."
    ),
    case_study=(
        "**Buffett comprando Wells Fargo en 1990**: el banco cotizaba "
        "a P/E ~5 y precio/tangible book ~1.2 después de un mini-crash "
        "regional. Buffett calculó que incluso con un escenario "
        "catastrófico (todo el portafolio de hipotecas defaulteando "
        "10%) el banco salía levemente positivo. Esa era la MoS: el "
        "downside era cuantificable y manejable.\n\n"
        "**Contraejemplo — Long-Term Capital Management 1998**: "
        "modelos perfectos, math impecable, MoS nula. Asumían que "
        "spreads no se ampliarían más de cierto rango. Cuando Rusia "
        "default-eó, los spreads explotaron 6x esa banda. Cero MoS = "
        "wipe-out."
    ),
    common_mistakes=[
        "Confundir 'bajó mucho desde su pico' con margin of safety. Lo que importa es vs intrinsic.",
        "Aplicar la misma MoS a una blue chip y a una small cap apalancada. La calidad importa.",
        "Asumir que el intrinsic es estático. Las empresas se deterioran (Kodak, BlackBerry, Sears).",
        "Comprar 'value traps': empresas baratas que se vuelven más baratas porque el negocio se deteriora.",
        "MoS al alza pero risk asimétrico al baja (out-of-the-money options, biotech binarias).",
    ],
    mental_model=(
        "Graham: cruzás un puente que en teoría aguanta 30,000 lbs. ¿Lo "
        "cruzás con un camión de 29,500 lbs? No — querés margen. El "
        "intrinsic value es la capacidad del puente; el price es el peso "
        "de tu camión. La diferencia es la margin of safety, y tiene que "
        "ser ancha porque el futuro tiene viento y temblores."
    ),
    books=[_BOOK_INTELLIGENT_INVESTOR, _BOOK_KLARMAN_MOS,
           _BOOK_SECURITY_ANALYSIS, _BOOK_MARKS_MOST_IMPORTANT],
    videos=[_VIDEO_BUFFETT_1996,
            Video(title="Seth Klarman on Margin of Safety",
                  channel="Talks at Google / Columbia Business School",
                  minutes=60,
                  url="",
                  why="Klarman explica su filosofía en una conferencia académica.")],
    quotes=[
        _Q_GRAHAM_MOS,
        Quote(text="The three most important words in investing are "
                   "'margin of safety'.",
              author="Warren Buffett",
              source="Berkshire 1992 letter"),
        Quote(text="In the short run, the market is a voting machine. "
                   "In the long run, it is a weighing machine.",
              author="Benjamin Graham",
              source="The Intelligent Investor"),
    ],
))


# ---------- Moats ----------
_add(Lesson(
    slug="moats",
    label=_label_for("moats"),
    category=_cat_for("moats"),
    hook=_hook_for("moats"),
    definition=(
        "Un 'economic moat' es una ventaja competitiva estructural "
        "que permite a la empresa generar retornos sobre capital "
        "superiores al costo del capital durante períodos prolongados, "
        "incluso enfrentando competencia. El término lo popularizó "
        "Buffett: 'lo que busco es un castillo económico protegido por "
        "un foso ancho y duradero'.\n\n"
        "Las 5 fuentes clásicas (Pat Dorsey, Morningstar):\n"
        "1. **Intangibles**: marca, patentes, licencias regulatorias.\n"
        "2. **Switching costs**: costo / fricción para que cliente cambie.\n"
        "3. **Network effect**: cada usuario nuevo aumenta valor para todos.\n"
        "4. **Cost advantage**: escala, ubicación, recursos únicos.\n"
        "5. **Efficient scale**: mercado nicho donde 1-2 jugadores "
        "saturan la demanda y nuevos no encuentran ROIC viable."
    ),
    why_matters=(
        "Sin moat, los retornos altos atraen competencia hasta que el "
        "ROIC converge al WACC — y la empresa se vuelve mediocre. Con "
        "moat ancho y duradero, esos retornos se sostienen 10, 20, 50 "
        "años. **Compounding requiere durabilidad.** Una empresa con "
        "ROIC 20% por 30 años multiplica el capital ~237x. Una con "
        "ROIC 20% por 5 años (porque la competencia entra), apenas "
        "2.5x. El moat determina cuánto dura el compounding."
    ),
    how_pros_analyze=(
        "1. **Identificar la fuente exacta**: 'Apple tiene moat' no "
        "alcanza — ¿es marca? switching costs (iCloud, App Store)? "
        "ambos? saberlo te dice qué amenaza importa.\n"
        "2. **Tendencia del moat (ensanchando vs erosionando)**. "
        "Microsoft 2010 tenía moat erosionando (Windows pierde "
        "relevancia móvil); 2024 ensanchando (Azure + AI).\n"
        "3. **ROIC consistentemente > WACC durante 10+ años** = "
        "moat empíricamente demostrado, no narrativa.\n"
        "4. **Test de los 'qué pasa si' (Mauboussin)**: ¿qué tendría que "
        "pasar para que la empresa pierda esto? Si la respuesta es "
        "'mucho y poco probable', el moat es real.\n"
        "5. **Mind the duration**: tech moats son más cortos que "
        "consumer brand moats. Coca-Cola tiene >100 años; Kodak "
        "perdió el suyo en una década."
    ),
    key_metrics=[
        ("ROIC sostenido vs WACC",
         "Spread positivo durante 10+ años = moat empírico."),
        ("Market share trend",
         "Estable o creciente en mercado consolidado = moat funcional."),
        ("Gross margin durability",
         "Margen alto y estable años aún en recesiones."),
        ("Pricing power test",
         "¿Pudieron subir precios above inflation sin perder volumen?"),
        ("Customer retention / NRR (SaaS)",
         ">120% NRR indica switching costs + expansion."),
    ],
    bullish_vs_bearish=[
        ("ROIC >20% durante 10 años consecutivos",
         "ROIC declina año tras año a pesar de crecimiento revenue"),
        ("Market share estable o creciente",
         "Erosión de market share / nuevos entrantes ganando ground"),
        ("Pricing power demostrado en recesiones",
         "Empresa cede precios ante presión competitiva"),
        ("Switching costs altos (data, integration, certifications)",
         "Producto / servicio fácilmente sustituible"),
        ("Moat ensanchando (Microsoft 2020-2024)",
         "Moat erosionando (Intel 2014-2024)"),
    ],
    valuation_impact=(
        "Las empresas con moat ancho merecen multiples más altos — pero "
        "no infinitos. Mastercard a 35x P/E refleja ROIC ~80% que "
        "durará décadas; Coca-Cola a 24x P/E refleja moat más modesto "
        "(~15% ROIC) pero ultra-durable. El error común es pagar "
        "moat-multiples por empresas sin moat. En DCF: el moat permite "
        "asumir competitive advantage period (CAP) más largo y ROIC "
        "steady-state más alto — esos dos números pueden agregar 30-50% "
        "al intrinsic value."
    ),
    case_study=(
        "**Visa / Mastercard — network effect + switching costs**. "
        "Los comercios necesitan aceptar las tarjetas que tienen los "
        "consumidores; los consumidores eligen tarjetas que aceptan "
        "los comercios. Cada nuevo participante refuerza la red. "
        "Switching costs altos (integración con bancos, comercios, "
        "regulatorios). ROIC 60-85% sostenido por décadas.\n\n"
        "**Contraejemplo — BlackBerry 2005-2013**: tenían switching "
        "costs corporativos enormes (BlackBerry Enterprise Server). "
        "Apple/Android disolvieron el switching cost convirtiendo la "
        "elección de teléfono en personal, no corporativa. El moat "
        "duró ~8 años. Lección: los moats tech pueden colapsar por "
        "cambios de paradigma."
    ),
    common_mistakes=[
        "Confundir tamaño con moat. Sears era enorme y no tenía moat real frente a Walmart/Amazon.",
        "Asumir que crecimiento alto = moat. La mayoría del crecimiento alto es competido al ROIC=WACC.",
        "Subestimar la velocidad de erosión del moat en tech.",
        "Ignorar que las marcas se construyen en décadas y se pierden en años (Nokia, Polaroid).",
        "Pagar moat-multiples sin verificar la fuente del moat. Narrativa de moat ≠ moat real.",
    ],
    mental_model=(
        "Buffett: 'Si vos me das $100 billions y me decís que destruya a "
        "Coca-Cola, no podría hacerlo. Esa es la prueba del moat.' "
        "Pensá en cuánto capital tendría que tirar un competidor con "
        "recursos infinitos para desplazar a la empresa que mirás. Si "
        "la respuesta es 'mucho y no garantizado', el moat es real."
    ),
    books=[_BOOK_BUFFETT_LETTERS, _BOOK_FISHER,
           Book(title="The Little Book That Builds Wealth",
                author="Pat Dorsey", year=2008,
                chapter_hint="Caps. 4-7 — las 4 fuentes de moat",
                why="El framework de Morningstar para identificar moats. Corto y claro.")],
    videos=[_VIDEO_BUFFETT_1996,
            Video(title="Pat Dorsey on Economic Moats",
                  channel="Talks at Google", minutes=50,
                  url="",
                  why="El ex-director de research de Morningstar explica su framework.")],
    quotes=[
        _Q_BUFFETT_MOAT,
        Quote(text="In business, I look for economic castles protected by "
                   "unbreachable moats.",
              author="Warren Buffett",
              source="1995 Berkshire annual meeting"),
        Quote(text="Time is the friend of the wonderful business, the "
                   "enemy of the mediocre.",
              author="Warren Buffett",
              source="Berkshire 1989 letter"),
    ],
))


# ---------- Earnings Quality ----------
_add(Lesson(
    slug="earnings_quality",
    label=_label_for("earnings_quality"),
    category=_cat_for("earnings_quality"),
    hook=_hook_for("earnings_quality"),
    definition=(
        "Earnings quality es qué tanto los earnings reportados reflejan "
        "el verdadero poder económico del negocio. Earnings de alta "
        "calidad son: sostenibles, convertibles en caja, libres de "
        "items no-recurrentes, y producidos sin contabilidad agresiva. "
        "Earnings de baja calidad pueden engañar al mercado por "
        "trimestres o años — hasta que la caja contradice los reportes."
    ),
    why_matters=(
        "Los modelos de valuación se construyen sobre earnings — pero si "
        "los earnings son humo, el modelo es humo. Casos como Enron, "
        "WorldCom, Wirecard mostraron P/E 'razonables' sobre earnings "
        "inventados. El analista profesional pregunta no '¿cuánto "
        "ganó?' sino '¿qué tan buena es esa ganancia?'."
    ),
    how_pros_analyze=(
        "1. **Net Income vs Operating Cash Flow**: si NI crece y OCF "
        "cae, ALERTA. Es el indicador #1 de earnings management.\n"
        "2. **Beneish M-Score**: 8 variables que detectan probable "
        "manipulación contable. M > -1.78 = sospechoso.\n"
        "3. **Piotroski F-Score**: 9 puntos de calidad fundamental "
        "(rentabilidad, leverage, eficiencia). >7 = limpio.\n"
        "4. **Sloan Ratio**: accruals / total assets. >10% absoluto = "
        "alta dependencia de items no-cash.\n"
        "5. **One-time items**: cuántos 'one-time' aparecen en 5 años "
        "consecutivos. Si son recurrentes, no son one-time.\n"
        "6. **Revenue recognition policy**: ¿bookean revenue antes de "
        "entregar? ¿reconocen long-term contracts agresivamente?"
    ),
    key_metrics=[
        ("OCF / Net Income",
         ">1.0 saludable · <0.6 bandera roja"),
        ("Beneish M-Score",
         "< -2.22 muy limpio · entre -2.22 y -1.78 zona gris · > -1.78 sospechoso"),
        ("Piotroski F-Score",
         "0-9 puntos. 7+ excelente · 4-6 medio · 0-3 deteriorando"),
        ("Sloan Ratio",
         "|accruals/TA| < 5% limpio · 5-10% medio · >10% riesgoso"),
        ("DSR · Days Sales Receivables",
         "Estable o decreciendo = ok. Aumenta sin explicación = revenue agresivo"),
    ],
    bullish_vs_bearish=[
        ("OCF / NI consistente >0.9",
         "OCF / NI <0.6 — gap creciente"),
        ("Beneish bajo (<-2.22) · Piotroski alto (>7)",
         "Beneish >-1.78 o Piotroski <4"),
        ("Pocos 'non-recurring items'",
         "'Non-recurring' aparece todos los años"),
        ("Working capital eficiente y estable",
         "DSO inflándose · inventarios subiendo más rápido que revenue"),
        ("Auditor Big 4 sin cambios recientes",
         "Cambio reciente de auditor · qualifications en el opinion letter"),
    ],
    valuation_impact=(
        "El mercado paga multiples premium por earnings de alta calidad "
        "(predictibles, convertibles). Una empresa con earnings de baja "
        "calidad merece P/E con descuento — y cuando se descubre la "
        "verdad, el descuento se materializa de golpe (Enron pasó de "
        "P/E 30 a 0 en 6 meses). En DCF, earnings de baja calidad "
        "implican que la conversión FCF/NI es baja → menos FCF futuro "
        "→ menor intrinsic."
    ),
    case_study=(
        "**Wirecard 2018-2020**: net income reportado crecía 30% YoY "
        "mientras OCF prácticamente plano. Los earnings eran ficticios — "
        "$2B en cuentas en Filipinas que no existían. Beneish M-Score "
        "venía rojo desde 2017. Bajaron de €100/acción a €1 en cuatro "
        "días cuando KPMG dijo 'no podemos verificar el cash'.\n\n"
        "**Caso limpio — Microsoft 2024**: NI $88B, OCF $119B → "
        "conversion >1.0 (D&A excede CapEx). Piotroski 9/9. Sin "
        "non-recurring items materiales. Eso es earnings quality."
    ),
    common_mistakes=[
        "Mirar solo el bottom-line. NI puede crecer con buybacks o ingeniería contable.",
        "Confiar en EPS guidance sin chequear cash flow.",
        "Ignorar el cambio de auditor — es un red flag clásico.",
        "Asumir que earnings reportados en GAAP son 'la verdad'. GAAP da margen para criterio.",
        "Pasar por alto que el SBC infla el EPS no-GAAP. Los earnings 'adjusted' suelen ser inflados.",
    ],
    mental_model=(
        "Buffett: 'The basic ideas of investing are to look at stocks as "
        "businesses, use market fluctuations to your advantage, and seek "
        "a margin of safety.' Para mirar 'as businesses' tenés que "
        "verificar que los números reportados reflejan economía real. "
        "Cash doesn't lie — accounting earnings sometimes do."
    ),
    books=[_BOOK_SECURITY_ANALYSIS, _BOOK_INTELLIGENT_INVESTOR,
           Book(title="Financial Shenanigans",
                author="Howard Schilit", year=2018,
                chapter_hint="Caps. 1-6 — los 6 tipos de manipulación contable",
                why="Manual de cómo se manipulan earnings. Con casos reales (Enron, WorldCom, Olympus).")],
    videos=[
        Video(title="How to Spot Accounting Fraud (Schilit)",
              channel="CFA Institute", minutes=45,
              url="",
              why="El autor de Financial Shenanigans explica los patrones."),
    ],
    quotes=[
        Quote(text="Beware of geeks bearing formulas.",
              author="Warren Buffett",
              source="Berkshire 2008 letter (sobre derivatives, aplica a accounting tricks)"),
        _Q_MUNGER_INCENTIVES,
        Quote(text="Cash is a fact. Profit is an opinion.",
              author="Alfred Rappaport",
              source="Creating Shareholder Value (1986)"),
    ],
))


# ---------- Yield Curve ----------
_add(Lesson(
    slug="yield_curve",
    label=_label_for("yield_curve"),
    category=_cat_for("yield_curve"),
    hook=_hook_for("yield_curve"),
    definition=(
        "La yield curve es el gráfico de tasas de interés de bonos del "
        "tesoro a distintos plazos (3M, 2Y, 10Y, 30Y). Su forma refleja "
        "expectativas del mercado sobre inflación, crecimiento y "
        "política monetaria.\n\n"
        "Formas típicas:\n"
        "  · **Normal** (upward sloping): tasas largas > cortas. Indica "
        "expansión económica esperada.\n"
        "  · **Flat**: largas ≈ cortas. Incertidumbre o transición.\n"
        "  · **Inverted**: cortas > largas. Mercado espera recesión y "
        "cortes de tasas → tasas largas bajan.\n"
        "  · **Steepening**: el spread (10Y − 2Y) se amplía. Típicamente "
        "ocurre en early recovery."
    ),
    why_matters=(
        "La curva invertida 2Y/10Y predijo **9 de las últimas 10 "
        "recesiones US** en los 60 años previos a 2024. Es el "
        "indicador macro con mejor track record empírico. Más allá del "
        "predictivo, su forma drivea: spreads de crédito, márgenes de "
        "bancos (NIM), valuación de growth stocks (sensibles a tasas "
        "largas), refinancing risk corporate."
    ),
    how_pros_analyze=(
        "1. **2Y/10Y spread**: el más vigilado. <0 = inversión.\n"
        "2. **3M/10Y spread**: el preferido de la Fed (NY Fed model). "
        "Más persistente que el 2Y/10Y.\n"
        "3. **Re-steepening después de inversión**: cuando la curva "
        "vuelve a positiva DESPUÉS de estar invertida, históricamente "
        "la recesión es inminente (los cortes de tasas ya empezaron).\n"
        "4. **Forward curve**: descuenta lo que el mercado espera de "
        "tasas. Comparar con dot plot de la Fed para detectar gaps de "
        "expectativas.\n"
        "5. **Term premium**: la prima por mantener bonos largos vs "
        "rollear cortos. Negativo en gran parte de 2010-2020 → era "
        "raro históricamente."
    ),
    key_metrics=[
        ("2Y/10Y spread",
         "Predictivo de recesión cuando <0 por 3+ meses. Inversión "
         "típicamente precede recesión 12-18 meses."),
        ("3M/10Y spread",
         "Versión NY Fed. Más sensible a Fed funds que el 2Y/10Y."),
        ("10Y yield (nivel)",
         "Driver de discount rate para equities. >5% históricamente "
         "presiona multiples."),
        ("Real 10Y yield",
         "Nominal − inflation expectations (TIPS). Drive de growth stocks."),
        ("Curve shape (Δ slope MoM)",
         "Cambios bruscos = cambio de régimen de mercado."),
    ],
    bullish_vs_bearish=[
        ("Curva normal (10Y − 2Y > 100bp)",
         "Curva invertida (10Y − 2Y < 0) por 3+ meses"),
        ("Steepening tras corte de Fed (re-acceleration play)",
         "Re-steepening post-inversión (recession imminent)"),
        ("Real yields bajos sostenibles",
         "Real yields subiendo bruscamente (presiona growth equities)"),
        ("Spreads HY apretados acompañando curva normal",
         "HY spreads ampliándose con curva invertida = stress"),
    ],
    valuation_impact=(
        "Tasa larga sube → discount rate sube → presente value de cash "
        "flows lejanos cae más → growth stocks sufren más que value. "
        "Es exactamente lo que pasó en 2022: el 10Y pasó de 1.5% a 4.5% "
        "y el Nasdaq cayó 33% mientras el S&P value cayó solo 6%. "
        "También: una curva invertida típicamente comprime los márgenes "
        "de los bancos (NIM) porque toman corto y prestan largo."
    ),
    case_study=(
        "**2007 — curva invertida**: 2Y/10Y se invirtió en julio 2006, "
        "permaneció invertida hasta junio 2007. Recesión comenzó "
        "diciembre 2007 — exactamente el lag típico de 12-18 meses. "
        "El mercado bursátil tocó peak en octubre 2007, 3 meses antes "
        "de la recesión.\n\n"
        "**2022-2024 — el debate**: la curva 2Y/10Y se invirtió en "
        "julio 2022 — la inversión más prolongada en décadas. Muchos "
        "esperaban recesión en 2023; la economía resistió. La "
        "regla 'inverted curve predicts recession' tiene que evaluarse "
        "junto a otros indicators (claims, ISM, Sahm rule)."
    ),
    common_mistakes=[
        "Asumir que la curva invertida implica recesión inminente. El lag es 12-18 meses, a veces más.",
        "Mirar solo el 2Y/10Y sin chequear el 3M/10Y. Pueden diverger.",
        "Confundir la SEÑAL de inversión con la CAUSA. La inversión no causa recesión, la anticipa.",
        "Ignorar el contexto: la inversión bajo QT/QE distorts term premium.",
        "Pasar por alto el efecto NIM en bancos — una curva plana/invertida los exprime independiente del nivel.",
    ],
    mental_model=(
        "La curva es la voz colectiva del mercado de bonos diciéndote "
        "qué espera. Cuando el mercado paga MENOS por bloquear capital "
        "10 años que 2 años, está apostando explícitamente a que las "
        "tasas cortas bajarán — es decir, que la Fed va a cortar — es "
        "decir, que viene recesión o desaceleración. Es el consenso de "
        "trillones de dólares de bond traders. Cuando contradice tu "
        "tesis equity, pensá dos veces antes de descartarlo."
    ),
    books=[_BOOK_DALIO_PRINCIPLES, _BOOK_MARKS_MARKET_CYCLE,
           _BOOK_JPM_GUIDE,
           Book(title="The Bond King",
                author="Mary Childs", year=2022,
                chapter_hint="Caps. sobre PIMCO + Fed policy",
                why="Cómo los bond markets reaccionan a Fed — desde adentro de PIMCO con Bill Gross.")],
    videos=[
        Video(title="The Yield Curve: A Recession Indicator?",
              channel="The Plain Bagel", minutes=15, url="",
              why="Intro clara con ejemplos históricos."),
        Video(title="Ray Dalio Explains the Economic Machine",
              channel="Ray Dalio", minutes=30,
              url="https://www.youtube.com/watch?v=PHe0bXAIuk0",
              why="No es sobre yield curve directo pero es contexto perfecto para entender por qué la curva refleja ciclos."),
    ],
    quotes=[
        Quote(text="The yield curve has predicted recessions remarkably "
                   "well — but timing is the question, not direction.",
              author="Campbell Harvey",
              source="Duke / NBER (descubridor del predictivo de la 3M/10Y, 1986)"),
        Quote(text="Markets can stay irrational longer than you can stay "
                   "solvent.",
              author="John Maynard Keynes",
              source="(atribuido — aplica al timing de la curva)"),
    ],
))


# ---------- Inflation ----------
_add(Lesson(
    slug="inflation",
    label=_label_for("inflation"),
    category=_cat_for("inflation"),
    hook=_hook_for("inflation"),
    definition=(
        "Inflación es la tasa a la cual sube el nivel general de "
        "precios — y por tanto cae el poder adquisitivo del dinero. "
        "Se mide con índices que ponderan canastas de bienes (CPI, "
        "PCE, PPI) o agregados macro (GDP deflator).\n\n"
        "Distinción clave:\n"
        "  · **Headline**: incluye todo (energía + alimentos). Volátil.\n"
        "  · **Core**: excluye energía + alimentos. Lo que mira la Fed.\n"
        "  · **Sticky core**: items que cambian precio infrecuentemente "
        "(rent, services). Captura tendencia subyacente.\n"
        "  · **Expectativas**: lo que consumidores/mercado esperan (TIPS "
        "spread, U-Michigan survey). Las expectativas se auto-cumplen."
    ),
    why_matters=(
        "Inflación es el driver #1 de la política monetaria, que a su "
        "vez drivea tasas, multiples y rotación sector. Inflación alta "
        "y persistente comprime los multiples de growth (cash flows "
        "lejanos valen menos) y beneficia commodities, value, real "
        "assets. El error de la Fed de 2021 ('transitory') costó "
        "credibilidad y forzó el ciclo de tightening más agresivo en "
        "40 años — con consecuencias para todo equity en 2022."
    ),
    how_pros_analyze=(
        "1. **Headline vs core**: la Fed actúa sobre core. El mercado "
        "reacciona a headline.\n"
        "2. **Goods vs services**: post-COVID, goods se desinflactó "
        "primero, services siguen siendo el componente pegajoso.\n"
        "3. **Shelter lag**: el componente de rent en CPI tiene 9-12 "
        "meses de lag vs los precios reales de mercado. Conocer esto "
        "te permite anticipar el ritmo de desinflación.\n"
        "4. **Expectativas**: si los breakevens TIPS suben, el mercado "
        "duda que la Fed gane la batalla. Esa duda se auto-cumple.\n"
        "5. **Wage growth vs productivity**: si wages > productivity, "
        "presiona márgenes y/o se traduce en precios."
    ),
    key_metrics=[
        ("CPI YoY (%)",
         "Headline. >3% considerada 'alta' por estándares de la Fed."),
        ("Core CPI YoY (%)",
         "Lo que la Fed targetea. Objetivo: cerca de 2%."),
        ("PCE Core YoY (%)",
         "Versión Fed-preferred del core. Pondera diferente que CPI."),
        ("Breakeven 5Y / 10Y (TIPS)",
         "Expectativas de inflación implícitas. Anchor cuando son "
         "estables; problema cuando se mueven."),
        ("Wage growth (Atlanta Fed Wage Tracker)",
         "Driver fundamental de inflación de servicios."),
    ],
    bullish_vs_bearish=[
        ("Core CPI desacelerando hacia 2% sin recesión",
         "Core CPI estancado en 3-4% (sticky)"),
        ("Breakevens TIPS anclados <2.5%",
         "Breakevens desanclando >3%"),
        ("Wage growth converging a productividad",
         "Wage-price spiral evident"),
        ("Goods + services desinflactando en sincronía",
         "Solo goods desinflactan, services persistentes"),
    ],
    valuation_impact=(
        "Inflación alta → la Fed sube tasas → discount rate sube → "
        "presione multiples (P/E). Es matemático: si el 10Y pasa de "
        "2% a 5%, el present value de un cash flow en año 10 cae "
        "~25%. Tech / growth (cash flows lejanos) sufren más que "
        "value (cash flows cercanos). Empresas con pricing power "
        "(consumer staples premium, semiconductores líderes) "
        "amortiguan; commodity-takers (utilities reguladas) "
        "sufren porque no pueden trasladar costos rápido."
    ),
    case_study=(
        "**1970s — la gran inflación**: CPI llegó a 14% en 1980. "
        "Volcker subió Fed funds a 20%, causó recesión doble en "
        "1980-82, ancla las expectativas. Lección: bajar inflación "
        "una vez desanclada cuesta una recesión.\n\n"
        "**2021-2024 — el ciclo post-COVID**: CPI tocó 9.1% en "
        "junio 2022, el peak en 40 años. La Fed subió Fed funds de "
        "0 a 5.5% en 18 meses — el tightening más agresivo desde "
        "Volcker. El S&P cayó 19% en 2022; el growth tech cayó "
        "33%. Para 2024 CPI volvió a ~3% pero todavía no al 2% "
        "target."
    ),
    common_mistakes=[
        "Confiar en una única lectura mensual. Hay que ver tendencia 3-6 meses.",
        "Confundir headline con core. La Fed reacciona a core.",
        "Asumir que la desinflación es lineal. Tiene baches (ver 1974, 2024).",
        "Olvidar que el shelter en CPI tiene lag — los datos siempre van detrás de la realidad.",
        "Pasar por alto el efecto de la base (base effects) — un mes bajo en el comparable inflacta el YoY del año siguiente.",
    ],
    mental_model=(
        "Marks: 'los inversores se obsesionan con datos puntuales y "
        "pierden de vista el ciclo'. Inflación no es un número del mes — "
        "es una fuerza que se mueve como el clima. Mirá tendencia, "
        "expectativas y components. Y recordá la lección de Volcker: "
        "una vez que se desancla, sale carísima volverla a anclar."
    ),
    books=[_BOOK_DALIO_PRINCIPLES, _BOOK_MARKS_MARKET_CYCLE,
           Book(title="The Lords of Easy Money",
                author="Christopher Leonard", year=2022,
                chapter_hint="Cap. 9-12 — la Fed pre y post COVID",
                why="Cómo decidió la Fed sus políticas pre-inflacionarias.")],
    videos=[
        Video(title="What Causes Inflation",
              channel="Federal Reserve / Plain Bagel", minutes=15,
              url="",
              why="Intro accesible."),
        Video(title="The Fed Is Behind the Curve",
              channel="Real Vision / Bloomberg",
              minutes=30, url="",
              why="Crítica de la respuesta tardía de la Fed 2021-22."),
    ],
    quotes=[
        Quote(text="Inflation is always and everywhere a monetary "
                   "phenomenon.",
              author="Milton Friedman",
              source="The Counter-Revolution in Monetary Theory (1970)"),
        Quote(text="The biggest mistake the Fed can make is to think "
                   "they can fine-tune their way out of inflation.",
              author="Paul Volcker (paráfrasis)",
              source="Volcker memoir 'Keeping at It'"),
    ],
))


# ---------- Capital Allocation ----------
_add(Lesson(
    slug="capital_allocation",
    label=_label_for("capital_allocation"),
    category=_cat_for("capital_allocation"),
    hook=_hook_for("capital_allocation"),
    definition=(
        "Capital allocation es cómo el management distribuye los "
        "recursos generados por el negocio entre 5 opciones:\n\n"
        "  1. **Reinvertir en el negocio** (organic capex, R&D)\n"
        "  2. **M&A** (acquisitions)\n"
        "  3. **Recomprar acciones** (buybacks)\n"
        "  4. **Pagar dividendos**\n"
        "  5. **Pagar deuda / acumular cash**\n\n"
        "Cada dólar puede ir a una sola opción. La decisión correcta "
        "es la que maximiza valor por acción a largo plazo — no la que "
        "maximiza ego del CEO o tamaño absoluto."
    ),
    why_matters=(
        "Buffett: 'capital allocation es la responsabilidad #1 del "
        "CEO'. Una empresa con economía buena puede ser destruida por "
        "mala asignación de capital — y una mediocre puede ser "
        "transformada por una buena. El track record de capital "
        "allocation de un CEO predice mejor el retorno futuro que "
        "casi cualquier otro factor cualitativo."
    ),
    how_pros_analyze=(
        "1. **Order of preference debería ser**: reinvertir si ROIC > "
        "WACC; M&A si ROIC sintético > WACC + premium; buybacks si "
        "stock < intrinsic; dividendos si nada de lo anterior aplica.\n"
        "2. **Track record M&A**: cuántas acquisitions hizo, retornos "
        "sobre capital invertido en cada una. La industria promedio "
        "destruye valor en M&A (1+1=1.8). Pocos CEOs son creadores "
        "consistentes (Singleton en Teledyne, Buffett, Malone).\n"
        "3. **Buybacks timing**: ¿el management recompra arriba o "
        "abajo del intrinsic? Recomprar cerca de máximos destruye "
        "valor. AIG y Lehman recompraron heavily antes de 2008.\n"
        "4. **Dividend policy**: estable + creciente = madurez "
        "ordenada. Recortar dividendo = señal de stress / cambio "
        "de capital allocation.\n"
        "5. **Capital intensity vs ROIC**: ¿el negocio NECESITA todo "
        "ese capex? Si no, lo que sobra debería volver a accionistas."
    ),
    key_metrics=[
        ("CapEx / Revenue (%)",
         "Comparar vs peers. Anómalamente alto = capex bingo."),
        ("Buybacks netos / FCF (%)",
         "Si >70% sustained = empresa madura priorizando shareholder returns."),
        ("Dividend payout ratio",
         "Dividendos / NI. 30-60% típico mature. >80% = poco margen para mal año."),
        ("M&A: 5y avg IRR",
         "Difícil de calcular ex-post pero crítico. Schiller / Sirower research dice <50% de deals crea valor."),
        ("Cash on balance sheet vs uses",
         "Cash excesivo sin plan = capital lazy. Apple lo devolvió vía buybacks."),
    ],
    bullish_vs_bearish=[
        ("Buybacks consistentes cerca de mínimos",
         "Buybacks máximos cerca de máximos (Lehman, AIG pre-2008)"),
        ("M&A disciplinada (raras, bolt-on, ROIC > WACC)",
         "M&A frecuente, transformacional, premium >30%"),
        ("Dividendos crecientes 10+ años",
         "Cortes de dividendo o congelamientos repetidos"),
        ("Reinversión cuando ROIC > WACC; devuelve cash cuando no",
         "Reinvierte aunque ROIC declina (capital aggression sin retorno)"),
        ("CEO con track record claro (Bezos, Singleton, Malone)",
         "CEO empire-builder sin disciplina de retornos"),
    ],
    valuation_impact=(
        "Una empresa con buen capital allocation amerita multiples "
        "más altos que un par con misma economía pero peor allocator. "
        "Berkshire cotiza a P/B premium parte por capital allocation "
        "de Buffett. Liberty Media (Malone) cotiza con descuento al "
        "intrinsic SOTP pero el descuento se cierra periódicamente "
        "porque Malone allocate-a bien. En DCF, la diferencia se "
        "manifiesta vía RR (reinvestment rate) más bajo → más FCF "
        "disponible → más valor."
    ),
    case_study=(
        "**Henry Singleton — Teledyne (1960-1990)**: el caso de estudio "
        "más estudiado en capital allocation. Recompró 90% de las "
        "acciones outstanding cuando el stock estaba barato. ROIC "
        "compuesto de los accionistas: ~25% anual durante 30 años. "
        "Buffett y Munger lo citan como el mejor allocator que vieron.\n\n"
        "**Contraejemplo — AOL Time Warner (2001)**: el mega-deal "
        "destruyó >$200B en valor en pocos años. Combinó dos negocios "
        "con economía declinante en un management con egos enormes y "
        "synergies inexistentes. Caso clásico de M&A transformacional "
        "fallida."
    ),
    common_mistakes=[
        "Premiar al CEO por revenue growth (cualquiera lo logra emitiendo deuda) sin verificar ROIC.",
        "Aplaudir dividends sin chequear que están cubiertos por FCF sostenible.",
        "Olvidar que un buyback caro es destrucción de valor. No todo buyback es bueno.",
        "Pasar por alto que las M&A grandes destruyen valor 60%+ de las veces (consenso académico).",
        "Confundir cash en el balance con conservadurismo. Cash lazy es valor erosionándose vs inflación.",
    ],
    mental_model=(
        "Buffett: 'el test definitivo de la administración es lo que pasa con "
        "cada dólar de retained earnings'. Imaginá que el CEO viene cada año "
        "a vos con $100M y te dice qué va a hacer. ¿Esperarías que esos "
        "$100M en su mano valgan más o menos en 5 años? Esa pregunta separa "
        "los grandes allocators de los mediocres."
    ),
    books=[_BOOK_BUFFETT_LETTERS,
           Book(title="The Outsiders",
                author="William Thorndike", year=2012,
                chapter_hint="Caps. 2-9 — 8 CEOs de capital allocation extraordinario",
                why="Estudio de Singleton, Buffett, Malone, Murphy, etc. Lectura obligada."),
           Book(title="The Essays of Warren Buffett",
                author="Cunningham (ed.)",
                year=2013,
                chapter_hint="Parte VII — 'Accounting and Valuation'",
                why="Buffett organizado por temas. Capital allocation está bien separado.")],
    videos=[
        Video(title="The Outsiders CEOs · Thorndike Interview",
              channel="Capital Allocators (Ted Seides)",
              minutes=60, url="",
              why="Entrevista profunda con el autor del libro."),
        _VIDEO_BUFFETT_1996,
    ],
    quotes=[
        Quote(text="The test of managers is whether they generate at "
                   "least $1 of market value for every dollar of "
                   "retained earnings.",
              author="Warren Buffett",
              source="Berkshire 1983 letter"),
        _Q_MUNGER_INCENTIVES,
        Quote(text="The only thing that matters in capital allocation is "
                   "investment IRR — and most CEOs don't think about it.",
              author="Henry Singleton (paráfrasis)",
              source="Singleton's Teledyne shareholder letters"),
    ],
))


# ---------- Business Cycles ----------
_add(Lesson(
    slug="business_cycles",
    label=_label_for("business_cycles"),
    category=_cat_for("business_cycles"),
    hook=_hook_for("business_cycles"),
    definition=(
        "Los ciclos económicos son fluctuaciones recurrentes en "
        "actividad económica con 4 fases típicas:\n\n"
        "  1. **Early expansion**: salida de recesión. Crecimiento "
        "acelera, tasas bajas, sentimiento aún cauteloso.\n"
        "  2. **Mid expansion**: crecimiento sostenido, márgenes pico, "
        "Fed neutral o tightening.\n"
        "  3. **Late expansion**: signos de overheating, inflación "
        "presiona, Fed restrictiva, yield curve plana o invertida.\n"
        "  4. **Contraction / recession**: crecimiento negativo, Fed "
        "corta, equities caen, spreads de crédito amplían.\n\n"
        "Duración típica post-WWII: expansión 65 meses promedio, "
        "recesión 11 meses."
    ),
    why_matters=(
        "Cada sector / factor performa distinto en cada fase. Comprar "
        "ciclicas en early expansion históricamente da retornos 2-3x "
        "el S&P. Comprarlas en late expansion da un drawdown brutal "
        "12-18 meses después. Saber dónde estás en el ciclo no es "
        "timing perfecto — es ajustar exposición y exigir mayor margin "
        "of safety cuando los riesgos se acumulan."
    ),
    how_pros_analyze=(
        "1. **Leading indicators**: yield curve, ISM new orders, "
        "building permits, Conference Board LEI. Anticipan 6-12 meses.\n"
        "2. **Coincident**: NFP, industrial production, retail sales. "
        "Confirman dónde estás ahora.\n"
        "3. **Lagging**: unemployment rate, core CPI. Cofirman después.\n"
        "4. **Credit conditions**: HY spreads, bank lending surveys. "
        "El crédito tightens antes que la actividad real cae.\n"
        "5. **Sentiment surveys (AAII, fund manager survey de BofA)**: "
        "extremos suelen marcar fin de ciclo."
    ),
    key_metrics=[
        ("ISM Manufacturing PMI",
         "Por debajo de 50 = contracción manufacturera. <45 sostained = recession warning."),
        ("Yield curve 2Y/10Y",
         "Inversión predice recesión 12-18 meses adelante."),
        ("Sahm Rule",
         "Si 3M moving avg unemployment sube ≥0.5pp vs los previos 12 meses → recesión empezó."),
        ("LEI YoY (%)",
         "Conference Board Leading Economic Index. Negativo sostenido = recesión próxima."),
        ("HY credit spread (bp)",
         "Amplía antes de recesión. >700bp = stress severo."),
    ],
    bullish_vs_bearish=[
        ("Early expansion: PMI subiendo desde <50, curva normalizando",
         "Late expansion: PMI bajando desde peak, curva invertida"),
        ("Sentimiento bearish extremo (fin de bear market típico)",
         "Sentimiento bullish extremo (fin de bull market típico)"),
        ("Crédito easy (spreads tightening)",
         "Crédito tightening (spreads widening + bank lending surveys negativas)"),
        ("Margen incremental positivo (operating leverage activo)",
         "Margen incremental negativo (operating deleverage)"),
    ],
    valuation_impact=(
        "El P/E del S&P comprime durante late cycle y se expande "
        "durante early cycle — eso es la mitad del retorno total. "
        "Ciclicas (industrials, materials, consumer disc) outperforman "
        "early-cycle 30-50% vs defensives (utilities, staples, "
        "healthcare). En late cycle, lo inverso. Comprar growth "
        "(cash flows lejanos) en early cycle es ganador; en late "
        "cycle es perdedor cuando las tasas suben."
    ),
    case_study=(
        "**2009-2020 — el ciclo más largo de la historia US**: "
        "129 meses de expansión sin recesión técnica. Cualquiera que "
        "haya predicho recesión desde 2014 perdió 200%+ de gains. "
        "Lección: timing perfecto es imposible; gestionar exposición "
        "es factible.\n\n"
        "**2020 — la recesión más corta de la historia**: oficialmente "
        "2 meses (febrero-abril 2020). El estímulo fiscal y monetario "
        "fue tan masivo que la fase de contracción se comprimió. "
        "Lección: el playbook clásico puede no aplicar cuando hay "
        "intervención policy extrema."
    ),
    common_mistakes=[
        "Predecir la recesión 'mañana' por años. El timing exacto es elusivo.",
        "Reaccionar al ciclo en titulares (recession 'oficial' se anuncia 6 meses tarde).",
        "Asumir que los ciclos son iguales — el ciclo post-COVID fue atípico por scale fiscal.",
        "Cargar ciclicas a fin de ciclo solo porque el P/E parece barato (suelen estar baratas en peak earnings).",
        "Ignorar que la Fed cambia su reaction function cada ciclo (post-Volcker, post-Greenspan, post-COVID).",
    ],
    mental_model=(
        "Marks: 'la mayoría de inversores se olvida que los ciclos "
        "existen — hasta que están en el medio de uno doloroso'. "
        "Pensá en el ciclo no como 'cuándo' sino como 'cómo me "
        "preparo'. En late cycle: subí calidad, bajá leverage, exigí "
        "más MoS. En early cycle: aceptá más riesgo, más beta. No "
        "tenés que pegarle al pico — solo cambiar la postura."
    ),
    books=[_BOOK_MARKS_MARKET_CYCLE, _BOOK_DALIO_PRINCIPLES,
           Book(title="This Time Is Different",
                author="Reinhart & Rogoff", year=2009,
                chapter_hint="Parte I — Financial crises across 800 years",
                why="Historia de crisis para entender que los ciclos sí se repiten.")],
    videos=[
        Video(title="Ray Dalio · How the Economic Machine Works",
              channel="Ray Dalio", minutes=30,
              url="https://www.youtube.com/watch?v=PHe0bXAIuk0",
              why="El video macro más visto de la última década. 100% recomendado."),
        Video(title="Howard Marks on Cycles",
              channel="Oaktree Capital", minutes=45,
              url="",
              why="Marks explica su filosofía sobre cycles a un grupo de inversores institucionales."),
    ],
    quotes=[
        Quote(text="The fact that I keep an eye on cycles certainly does "
                   "not mean I think the future is predictable.",
              author="Howard Marks",
              source="Mastering the Market Cycle"),
        Quote(text="There are decades where nothing happens and there "
                   "are weeks where decades happen.",
              author="Vladimir Lenin (atribuido)",
              source="Aplica a los puntos de inflexión del ciclo"),
        _Q_MARKS_RISK,
    ],
))


# ============================================================
# Stubs for the remaining topics — books + videos + quotes only
# ============================================================
def _stub(slug: str, books: list[Book], videos: list[Video],
          quotes: list[Quote]) -> None:
    """Lección parcial: solo materiales recomendados. La página lo
    renderiza como 'contenido completo pendiente — mientras tanto,
    estos son los recursos para empezar'."""
    _add(Lesson(
        slug=slug, label=_label_for(slug), category=_cat_for(slug),
        hook=_hook_for(slug), books=books, videos=videos, quotes=quotes,
    ))


# ============================================================
# Batch 1 — Empresas core lessons
# ============================================================

# ---------- Revenue growth ----------
_add(Lesson(
    slug="revenue_growth",
    label=_label_for("revenue_growth"),
    category=_cat_for("revenue_growth"),
    hook=_hook_for("revenue_growth"),
    definition=(
        "Revenue growth es el crecimiento de la facturación de una "
        "empresa a través del tiempo. Parece simple pero la pregunta "
        "real no es cuánto creció — es **cómo**. Los analistas separan "
        "el crecimiento en componentes:\n\n"
        "  · **Orgánico**: el negocio core vendió más (más volumen, "
        "más precios, o ambos).\n"
        "  · **M&A**: vino de acquisitions — comprar revenue, no "
        "generarlo.\n"
        "  · **FX**: monedas locales se apreciaron vs USD reporting.\n"
        "  · **Mix / pricing**: cambiaron qué venden o a qué precio "
        "(distinto de volumen).\n\n"
        "Una empresa que crece 20% por adquisiciones y 0% orgánico es "
        "muy distinta de una que crece 20% orgánico — aunque el "
        "número reportado sea idéntico."
    ),
    why_matters=(
        "El valor de un negocio depende del crecimiento orgánico "
        "sostenible — no del crecimiento total. M&A en exceso suele "
        "destruir valor (estudios académicos coinciden: 60%+ de los "
        "deals fallan). FX gains no son repetibles. Pricing power "
        "es escalable; volumen tiene techo físico. Saber qué tipo de "
        "growth tenés en el reporte cambia completamente la valuación."
    ),
    how_pros_analyze=(
        "1. **Decomposition obligatoria**: reportes 10-K y earnings "
        "calls suelen dar 'organic growth ex-FX ex-M&A'. Buscar ese "
        "número, no el headline.\n"
        "2. **Pricing vs volume**: empresas grandes suelen reportar "
        "ambos. Coca-Cola por ejemplo da volume growth + price/mix "
        "growth por geografía. Pricing power consistente = moat.\n"
        "3. **Quality of growth**: ¿el growth viene con márgenes "
        "estables o se compra con descuentos? Revenue creciendo pero "
        "márgenes erosionándose = mala calidad.\n"
        "4. **Comparables sectoriales**: 10% growth en software es "
        "modesto; en utilities es excepcional. Hay que normalizar.\n"
        "5. **Trend, no point**: una empresa con CAGR estable 8% por "
        "10 años es más valiosa que una con un año de 30% y otros "
        "estancados — aunque el promedio sea igual."
    ),
    key_metrics=[
        ("Revenue YoY (%)",
         "Crecimiento reportado vs año anterior. Headline obvious."),
        ("Organic revenue growth (%)",
         "El que descuenta M&A y FX. Lo que mide el negocio real."),
        ("Volume vs price/mix split",
         "En empresas grandes ambos son reportados. Pricing power = "
         "price/mix consistentemente positivo."),
        ("Revenue CAGR 5y",
         "Trend de mediano plazo. Suaviza años outlier."),
        ("Same-store / same-customer growth",
         "Para retail (SSS) y SaaS (NRR). Mide cómo crece la base "
         "existente, no el efecto net-new."),
    ],
    bullish_vs_bearish=[
        ("Crecimiento orgánico ≥ headline (poco M&A)",
         "Headline alto pero orgánico cerca de 0 (todo es M&A)"),
        ("Pricing + volume ambos positivos",
         "Crece solo por descuentos / pricing negativo"),
        ("Same-store sales positivo consistente",
         "Crece solo por aperturas / SSS negativo"),
        ("Mix shifting hacia productos premium",
         "Mix shifting hacia low-margin commodity"),
        ("Aceleración orgánica en mercados maduros",
         "Desaceleración orgánica oculta por adquisiciones"),
    ],
    valuation_impact=(
        "Revenue growth alimenta directo el DCF como input top-line. "
        "Pero los multiples dependen MÁS del growth QUALITY que de su "
        "magnitud. Una empresa con 8% orgánico estable amerita P/S "
        "más alto que una con 15% mixto (50% M&A). Damodaran: 'el "
        "growth que crea valor es solo el que viene con ROIC > WACC'. "
        "Si una empresa crece comprando otras a múltiples altos, "
        "está destruyendo valor aunque revenue suba."
    ),
    case_study=(
        "**Constellation Software (CSU.TO)**: la masterclass de "
        "growth-by-M&A bien hecha. Revenue creció ~20% CAGR durante "
        "20 años casi enteramente por acquisitions — PERO cada deal "
        "se hace con disciplina IRR strict (>20%). El stock multiplicó "
        "100x desde 2006. Lección: M&A NO es inherentemente malo, lo "
        "malo es la M&A indisciplinada.\n\n"
        "**Contraejemplo — Kraft-Heinz 2015-2019**: el merger prometió "
        "synergies + revenue growth. Resultado: revenue stagnated 4 "
        "años, márgenes cayeron, en 2019 tomaron impairment de $15B "
        "(reconociendo que las marcas valían menos). Buffett admitió "
        "públicamente que sobrepagó."
    ),
    common_mistakes=[
        "Celebrar revenue growth headline sin verificar cuánto es orgánico.",
        "Asumir que más growth = más valor. Growth con ROIC < WACC destruye valor.",
        "Confundir un trimestre con una tendencia. Un beat aislado no establece growth sostenible.",
        "Ignorar el efecto FX cuando la empresa reporta en USD pero opera multinacional.",
        "Pasar por alto que el crecimiento de same-store es el verdadero indicador para retail / SaaS.",
    ],
    mental_model=(
        "Buffett: 'crecimiento solo tiene valor cuando ocurre con retornos "
        "sobre capital atractivos'. Tu pregunta no debe ser '¿está "
        "creciendo?' sino '¿con qué calidad crece y cuánto tiempo "
        "puede sostenerlo?'. Una empresa que crece 8% al 25% ROIC vale "
        "más que una que crece 15% al 8% ROIC. Cada vez que veas un "
        "headline de revenue growth, pensá: orgánico, sostenible, y "
        "con qué retorno marginal sobre el capital invertido."
    ),
    books=[_BOOK_DAMODARAN_VALUATION, _BOOK_LYNCH, _BOOK_FISHER,
           _BOOK_MCKINSEY_VALUATION],
    videos=[_VIDEO_DAMODARAN_VALUATION],
    quotes=[_Q_LYNCH_INVERT, _Q_DAMODARAN_STORY,
            Quote(text="Growth is a component in the value of a business "
                       "— but a growth that destroys value is anti-growth.",
                  author="Aswath Damodaran",
                  source="Damodaran NYU lectures")],
))

# ---------- Margins ----------
_add(Lesson(
    slug="margins",
    label=_label_for("margins"),
    category=_cat_for("margins"),
    hook=_hook_for("margins"),
    definition=(
        "Los márgenes miden cuánto se queda la empresa de cada dólar "
        "vendido, en cada etapa del estado de resultados:\n\n"
        "  · **Gross margin** = (Revenue − COGS) / Revenue. Lo que "
        "queda después del costo directo de producción.\n"
        "  · **Operating margin** = EBIT / Revenue. Después de OPEX "
        "(R&D, marketing, G&A). El margen del negocio core.\n"
        "  · **EBITDA margin** = (EBIT + D&A) / Revenue. Operating "
        "ajustado por capital intensity.\n"
        "  · **Net margin** = Net Income / Revenue. El bottom-line "
        "después de intereses, impuestos y todo lo demás.\n\n"
        "Cada margen cuenta una parte distinta de la historia. Mirar "
        "uno solo es como diagnosticar a un paciente con un solo "
        "análisis."
    ),
    why_matters=(
        "Los márgenes son la huella digital de la calidad del negocio. "
        "Una empresa con gross margin 70% (software, marcas, "
        "farma) tiene fundamentos distintos a una con 30% (retail, "
        "manufactura). Los márgenes expansivos en el tiempo señalan "
        "pricing power, escalabilidad o ventaja competitiva creciente. "
        "Márgenes que se comprimen son la primera señal de deterioro "
        "competitivo — antes de que aparezca en revenue."
    ),
    how_pros_analyze=(
        "1. **Gross margin first**: es el más cercano al producto. "
        "Erosión sostenida = competencia o commoditización.\n"
        "2. **Operating margin vs gross**: la diferencia es OPEX. "
        "Empresas en growth deliberadamente sacrifican op margin para "
        "ganar share (Amazon clásico). Empresas maduras lo expanden.\n"
        "3. **Comparison vs peers**: margins solo importan vs "
        "competidores del mismo modelo. Apple op margin 30% vs Dell "
        "8% — la diferencia no es operacional, es estructural.\n"
        "4. **Trend 10y, not 1y**: márgenes oscilan con cycle. La "
        "tendencia subyacente importa más que el punto.\n"
        "5. **Decomposición del cambio**: si net margin sube 100bp, "
        "¿es por gross margin, OPEX leverage, mix de productos, o "
        "tax rate? Cada explicación implica calidad distinta."
    ),
    key_metrics=[
        ("Gross margin (%)",
         "Producto / mix. >70% software & brand · 30-50% industriales · "
         "<20% commoditizado."),
        ("Operating margin (%)",
         "Salud del negocio core. Mature blue chip: 15-30%."),
        ("EBITDA margin (%)",
         "Capital intensity-adjusted. Permite comparar telecoms vs "
         "software."),
        ("Net margin (%)",
         "Después de todo. Sensible a leverage y tax."),
        ("Incremental margin",
         "ΔOp Income / ΔRevenue. Mide operating leverage. >30% indica "
         "leverage fuerte."),
    ],
    bullish_vs_bearish=[
        ("Gross margin expandiendo 5+ años",
         "Gross margin erosionándose (commoditización / competencia)"),
        ("Op margin > gross margin proxy del sector",
         "Op margin sub-peer (ineficiencia OPEX)"),
        ("Incremental margin alto (operating leverage)",
         "Crece revenue pero op income estancado (deleverage)"),
        ("Margin recovery post-shock (resilient)",
         "Margins nunca recuperan (cambio estructural)"),
        ("Pricing power demostrado (price contribution positivo)",
         "Margens estables solo por cost-cutting (sin pricing)"),
    ],
    valuation_impact=(
        "En el DCF, el margen operativo determina el NOPAT y por tanto "
        "el FCF. Una expansión de 200bp en op margin puede agregar "
        "15-25% al intrinsic value. Pero más importante: márgenes "
        "consistentemente altos justifican multiples más altos. "
        "Software cotiza a P/S 8-15x porque sus márgenes operativos "
        "son 25-40%; retail cotiza a P/S 0.5-2x porque sus márgenes "
        "son 5-10%."
    ),
    case_study=(
        "**Apple FY2024**: gross margin 46%, op margin 31%. Empezó "
        "como empresa de hardware (gross margin típico hw <30%). El "
        "shift hacia servicios (gross margin >70%) elevó el blended "
        "gross margin de 38% (2018) a 46% (2024). El mercado pagó "
        "ese mix shift con expansión de multiple — pasó de P/E 14 a "
        "P/E 28+ en el mismo período.\n\n"
        "**Contraejemplo — General Electric 2015-2020**: op margin "
        "bajó de 14% a 6% mientras revenue se estancó. La empresa "
        "que era 'GE Brand' pasó a ser commoditized industrial. "
        "Stock perdió 60%."
    ),
    common_mistakes=[
        "Comparar márgenes entre industrias. Software vs manufactura son juegos distintos.",
        "Ignorar que márgenes en cyclical companies oscilan — no comprar en el peak ni vender en el trough.",
        "Confundir margin expansion vía cost-cutting con margin expansion vía pricing. La segunda es sostenible, la primera no.",
        "Pasar por alto el efecto del tax rate en net margin (cambios en jurisdicciones, deferred taxes).",
        "Asumir que margen alto = barrera de entrada. A veces solo indica que no hay competencia AÚN.",
    ],
    mental_model=(
        "Pensá los márgenes como las huellas que deja el modelo de "
        "negocio. Software te muestra 75% gross margin porque copiar "
        "código cuesta cero. Retail te muestra 25% porque cada item "
        "tiene costo. Cuando un margen se mueve fuera de su rango "
        "histórico, **eso es información** — algo cambió: el mix, la "
        "competencia, los costos. El analista pregunta '¿qué cambió?' "
        "antes de '¿es bueno o malo?'."
    ),
    books=[_BOOK_MCKINSEY_VALUATION, _BOOK_BUFFETT_LETTERS,
           _BOOK_DAMODARAN_VALUATION],
    videos=[_VIDEO_BUFFETT_1996, _VIDEO_DAMODARAN_CORPFIN],
    quotes=[_Q_BUFFETT_MOAT,
            Quote(text="The single most important decision in evaluating "
                       "a business is pricing power.",
                  author="Warren Buffett",
                  source="2010 FCIC interview"),
            _Q_DAMODARAN_STORY],
))

# ---------- Operating leverage ----------
_add(Lesson(
    slug="operating_leverage",
    label=_label_for("operating_leverage"),
    category=_cat_for("operating_leverage"),
    hook=_hook_for("operating_leverage"),
    definition=(
        "Operating leverage es la sensibilidad del operating income a "
        "cambios en revenue. Una empresa con costos fijos altos y "
        "variables bajos tiene **alto operating leverage**: pequeños "
        "cambios en revenue producen movimientos amplificados en OI.\n\n"
        "Cuantitativamente: **Operating leverage = % Δ EBIT / % Δ Revenue**.\n\n"
        "Una empresa con 2x operating leverage: revenue +10% → EBIT +20%.\n"
        "Una empresa con 0.5x: revenue +10% → EBIT +5%.\n\n"
        "El leverage opera en ambas direcciones — amplifica también "
        "las caídas."
    ),
    why_matters=(
        "Es la razón por la que el mismo crecimiento de revenue mueve "
        "muy distinto los EPS de distintos modelos. Software, "
        "exchanges (CME, ICE), media — alto fixed cost, casi todo "
        "incremental revenue va al bottom line. Retail, restaurants, "
        "shipping — alto variable cost, growth modesto en EPS. "
        "Entender el operating leverage te dice qué esperar de los "
        "earnings cuando revenue acelera (o se desacelera)."
    ),
    how_pros_analyze=(
        "1. **Incremental margin**: ΔEBIT / ΔRevenue año a año. Si una "
        "empresa muestra 40-60% incremental margin sostenido, alto "
        "operating leverage.\n"
        "2. **Fixed vs variable cost mix**: difícil de extraer del "
        "10-K pero suele estar en earnings calls. Software: ~80% fixed. "
        "Retail: ~30% fixed (rent + corporate G&A).\n"
        "3. **Break-even analysis**: punto donde EBIT = 0. Empresas "
        "con high operating leverage tienen break-even alto pero "
        "todo lo que está arriba se traduce en EBIT.\n"
        "4. **Operating leverage en bajadas**: durante recesión, "
        "alto OP también amplifica las pérdidas. Hay que respetar "
        "que el leverage es simétrico.\n"
        "5. **Mature companies**: una vez maduras, el operating "
        "leverage se agota. Mantener growth requiere más OPEX."
    ),
    key_metrics=[
        ("Degree of operating leverage (DOL)",
         "Contribution margin / Operating income. >2x = high. <1.2x = low."),
        ("Incremental operating margin (%)",
         "ΔEBIT / ΔRevenue YoY. Sostained 40%+ = leverage muy alto."),
        ("Fixed cost ratio",
         "Fixed / Total OPEX. Difícil de obtener pero clave."),
        ("Break-even revenue",
         "Revenue level needed to cover all costs. Para evaluar "
         "downside risk."),
        ("Revenue per employee",
         "Proxy de capital intensity. >$500K = high leverage; <$200K = low."),
    ],
    bullish_vs_bearish=[
        ("Incremental margin >40% sostenido",
         "Incremental margin <20% / revenue crece pero EBIT no"),
        ("Revenue crece + OPEX casi flat (high leverage)",
         "Revenue crece + OPEX crece igual o más (no leverage)"),
        ("Modelo escalable (software, exchanges)",
         "Modelo human-intensive (consultoría, retail)"),
        ("Recovery post-recesión rápida (leverage al alza)",
         "Recovery post-recesión lenta (sin re-leverage)"),
    ],
    valuation_impact=(
        "Las empresas con alto operating leverage merecen multiples "
        "MÁS altos cuando crecen y multiples MÁS bajos cuando "
        "decrecen — el mercado paga por la convexity. Microsoft (high "
        "OP) cotiza P/E 30+ con 12% growth; Walmart (low OP) cotiza "
        "P/E 25 con 5% growth. La diferencia es operating leverage. "
        "En DCF, modelar márgenes que se expanden con escala es la "
        "forma técnica de capturar OP."
    ),
    case_study=(
        "**Meta Platforms 2022-2024**: en 2022 revenue cayó 1% pero "
        "operating margin colapsó de 40% a 25% — el operating "
        "leverage operó al revés. En 2023-2024 Zuck hizo cost-cutting "
        "agresivo ('year of efficiency'), revenue se recuperó +16% y "
        "op margin volvió a 41%. El stock 4x desde el bottom — un "
        "case study clásico de cómo el operating leverage simétrico "
        "drivea retornos.\n\n"
        "**Contraejemplo — Boeing 2019-2024**: high operating leverage "
        "(plantas, R&D, certificación). Cuando el 737 MAX se "
        "groundeó, revenue cayó y los costos fijos siguieron. EBIT "
        "fue negativo 5 años seguidos. Recovery lenta porque cada "
        "avión adicional importa muchísimo."
    ),
    common_mistakes=[
        "Confundir operating leverage con financial leverage. El primero es operativo (costos fijos vs variables), el segundo es financiero (deuda).",
        "Asumir que alto operating leverage es siempre bueno. Es bueno con revenue creciendo, es brutal con revenue cayendo.",
        "Olvidar que el operating leverage se 'agota' a escala. Microsoft no tiene el mismo OP marginal que hace 20 años.",
        "Pasar por alto que el OPEX no es 100% fijo — incluye componentes variables (bonuses, marketing performance-based).",
        "Modelar revenue growth lineal sin ajustar márgenes — pierde toda la convexity del modelo.",
    ],
    mental_model=(
        "Imaginá una empresa como una palanca física. El operating "
        "leverage es el ratio de la palanca. Algunas empresas son "
        "palancas largas (alto leverage) — pequeños movimientos abajo "
        "producen grandes movimientos arriba. Otras son palancas "
        "cortas (bajo leverage). Cuando estimás el EBIT futuro, no "
        "asumas que crece proporcionalmente con revenue — depende del "
        "largo de la palanca."
    ),
    books=[_BOOK_MCKINSEY_VALUATION, _BOOK_DAMODARAN_VALUATION,
           _BOOK_CFA],
    videos=[_VIDEO_DAMODARAN_CORPFIN],
    quotes=[_Q_DAMODARAN_STORY,
            Quote(text="In businesses with high operating leverage, modest "
                       "changes in revenue can produce dramatic changes in "
                       "profits — for better or for worse.",
                  author="Tim Koller (McKinsey)",
                  source="Valuation, 7th ed.")],
))

# ---------- ROE / DuPont ----------
_add(Lesson(
    slug="roe",
    label=_label_for("roe"),
    category=_cat_for("roe"),
    hook=_hook_for("roe"),
    definition=(
        "Return on Equity (ROE) = Net Income / Total Equity. Mide "
        "cuánta ganancia genera la empresa por cada dólar de patrimonio "
        "neto. Es la métrica favorita del shareholder porque mide "
        "el retorno sobre **su** capital — no sobre el capital total.\n\n"
        "Pero ROE solo te dice POCO. La descomposición DuPont lo abre "
        "en sus tres drivers:\n\n"
        "**ROE = Net margin × Asset turnover × Equity multiplier**\n\n"
        "  · Net margin = NI / Revenue (rentabilidad)\n"
        "  · Asset turnover = Revenue / Total Assets (eficiencia)\n"
        "  · Equity multiplier = Total Assets / Equity (leverage)\n\n"
        "Dos empresas con ROE 20% pueden tener fundamentos opuestos."
    ),
    why_matters=(
        "ROE es el indicador más usado por inversores y el más fácil "
        "de manipular sin malicia. Una empresa puede inflar ROE "
        "tomando deuda (equity multiplier sube) — pero esa misma "
        "deuda la vuelve más frágil. DuPont te permite distinguir un "
        "ROE de alta calidad (alto net margin, baja deuda) de uno de "
        "baja calidad (basado en leverage). Es la diferencia entre "
        "Visa y un banco regional pre-2008."
    ),
    how_pros_analyze=(
        "1. **DuPont decomposition obligatoria**. ROE 25% con margin 25% "
        "/ turnover 1.0 / leverage 1.0 es muy distinto a ROE 25% con "
        "margin 5% / turnover 1.0 / leverage 5.0.\n"
        "2. **Compare ROE vs Cost of Equity (Ke)**: ROE > Ke = "
        "creación de valor para shareholders. ROE < Ke = destrucción.\n"
        "3. **Sustainability**: si ROE depende del leverage, es "
        "frágil — un mal año puede wipear el equity.\n"
        "4. **Banks**: tienen leverage estructural ~10x. ROE 15% en "
        "banco vs 15% en tech no son iguales. Para bancos comparar "
        "**ROTE** (return on tangible equity).\n"
        "5. **Industry comparison**: utilities tienen ROE 10% pero "
        "regulado y estable; tech 25% pero volátil. Hay que normalizar."
    ),
    key_metrics=[
        ("ROE (%)",
         "Net Income / Average Equity. >15% bueno · >25% excelente "
         "· <10% subpar."),
        ("ROE − Cost of Equity",
         "Spread de creación de valor. >5pp = sólido moat."),
        ("Net margin (%)",
         "Driver de rentabilidad en DuPont."),
        ("Asset turnover",
         "Driver de eficiencia en DuPont. Retailers >2x, "
         "industriales <1x."),
        ("Equity multiplier",
         "Driver de leverage. >3x considerar leverage-driven; >5x = "
         "fragilidad."),
        ("ROTE — Return on Tangible Equity",
         "Excluye goodwill. Esencial para bancos / empresas "
         "M&A-heavy."),
    ],
    bullish_vs_bearish=[
        ("ROE >20% sostenido 10y con leverage modesto",
         "ROE alto pero impulsado solo por leverage (>4x multiplier)"),
        ("DuPont: alto net margin + alta eficiencia",
         "DuPont: bajo margin + alta deuda — fragilidad"),
        ("ROE > Cost of Equity (spread positivo)",
         "ROE < Cost of Equity — destrucción de valor"),
        ("ROTE alto (calidad real)",
         "ROE alto pero ROTE bajo (goodwill enmascara economía pobre)"),
    ],
    valuation_impact=(
        "Empresas con ROE > Ke crean valor — el book value debería "
        "cotizar a P/B > 1. Visa cotiza P/B 12x porque su ROE es ~50% "
        "vs Ke ~9%. Bancos cotizan P/B 1.0-1.5x porque ROE ~12% vs "
        "Ke ~10%. La fórmula simplificada: **P/B = (ROE − g) / (Ke − g)**. "
        "Un ROE estable y alto justifica multiples premium; un ROE "
        "volátil y dependiente de leverage merece descuento."
    ),
    case_study=(
        "**Lehman Brothers 2006**: reportaba ROE 25%+ — looked "
        "amazing. DuPont decomposition revelaba: net margin 7%, asset "
        "turnover bajo, equity multiplier ~30x. Tres veces el "
        "leverage típico de un banco. Cuando los assets cayeron 3%, "
        "el equity entero se evaporó (3% × 30 = 100%). ROE = fragilidad.\n\n"
        "**Contraejemplo — Visa**: ROE ~50% con net margin 50%+, "
        "equity multiplier <2x. La calidad del ROE es real — no "
        "depende de leverage. Stock 20x desde IPO 2008."
    ),
    common_mistakes=[
        "Comparar ROE entre industrias sin ajustar por leverage estructural.",
        "Celebrar ROE alto sin descomponer en DuPont — puede ser puro leverage.",
        "Usar ROE en bancos. Para bancos usar ROTE (excluye goodwill).",
        "Olvidar que un cash buyback aumenta ROE artificialmente (reduce equity).",
        "Ignorar que ROE puede ser >100% (e.g. Lowe's después de buybacks agresivos) — el equity es residual.",
    ],
    mental_model=(
        "ROE responde una pregunta: '¿cuánto retorno gana la empresa "
        "sobre el capital que YO aporto?' Pero la pregunta importante "
        "es 'cómo lo gana'. Una empresa que rinde 25% sin deuda es "
        "una máquina de compounding. Una que rinde 25% con leverage "
        "10x es una bomba de tiempo. DuPont separa la señal del ruido."
    ),
    books=[_BOOK_MCKINSEY_VALUATION, _BOOK_CFA, _BOOK_DAMODARAN_VALUATION,
           _BOOK_BUFFETT_LETTERS],
    videos=[_VIDEO_DAMODARAN_CORPFIN],
    quotes=[_Q_BUFFETT_MOAT,
            Quote(text="The primary test of managerial economic "
                       "performance is the achievement of a high earnings "
                       "rate on equity capital employed.",
                  author="Warren Buffett",
                  source="Berkshire 1979 letter"),
            _Q_MUNGER_INCENTIVES],
))

# ---------- Debt analysis ----------
_add(Lesson(
    slug="debt_analysis",
    label=_label_for("debt_analysis"),
    category=_cat_for("debt_analysis"),
    hook=_hook_for("debt_analysis"),
    definition=(
        "Análisis de deuda es evaluar la solvencia y la "
        "sustentabilidad de la estructura de capital de una empresa. "
        "No es solo 'cuánta deuda tiene', sino:\n\n"
        "  · **Coverage**: ¿la genera suficiente caja para pagar "
        "intereses y principal?\n"
        "  · **Maturity profile**: ¿cuándo vence cada tranche?\n"
        "  · **Refinancing risk**: ¿en qué condiciones tendrá que "
        "rollover su deuda?\n"
        "  · **Covenants**: ¿qué le impide hacer la deuda?\n"
        "  · **Currency mix**: ¿deuda en moneda local o foreign?\n\n"
        "La deuda no es buena ni mala. Es una herramienta que "
        "amplifica retornos cuando va bien y amplifica problemas "
        "cuando va mal."
    ),
    why_matters=(
        "La deuda mata empresas. Hasta empresas de calidad. Lehman, "
        "AIG, GE Capital, WeWork, Evergrande, Credit Suisse — "
        "todas tenían un problema de balance que se hizo crisis de "
        "solvencia. Buffett: 'cuando combinás ignorancia con apalanca-"
        "miento obtenés resultados muy interesantes'. Saber leer un "
        "balance debt no es opcional para un equity analyst — la "
        "deuda decide quién sobrevive un downturn."
    ),
    how_pros_analyze=(
        "1. **Net debt / EBITDA**: el ratio más común. <2x = "
        "conservador, 2-4x = típico, >5x = riesgo material.\n"
        "2. **Interest coverage (EBITDA / Interest)**: >5x cómodo, "
        "<2x = stress. Mide capacidad de servir deuda.\n"
        "3. **Maturity wall**: ¿hay tranches grandes vendiendo en los "
        "próximos 12-24 meses? Visualizar el maturity schedule del 10-K.\n"
        "4. **Fixed vs floating rate mix**: en alza de tasas, la "
        "deuda floating se vuelve más cara YoY. % fixed = protección.\n"
        "5. **Off-balance-sheet**: operating leases (post-IFRS 16 ya "
        "están en balance), pension underfunded, supply chain "
        "financing escondida.\n"
        "6. **Credit ratings (Moody's, S&P)**: investment grade vs "
        "high yield. Cross-over downgrades disparan ventas forzadas.\n"
        "7. **Spread sobre treasuries**: el mercado de bonos te dice "
        "cómo ve el riesgo. Spread ampliándose = warning."
    ),
    key_metrics=[
        ("Net debt / EBITDA",
         "<2x conservador · 2-4x normal · >5x stress · >7x distress"),
        ("Interest coverage (EBITDA / Interest)",
         ">8x cómodo · 4-8x normal · 2-4x atención · <2x stress"),
        ("Debt / Equity",
         "Conservador <0.5 · normal 0.5-1.5 · agresivo >2"),
        ("Current ratio (Current Assets / Current Liab)",
         ">1.5 cómodo · 1-1.5 ok · <1 stress (no puede cubrir corto plazo)"),
        ("Maturity wall % (próximos 24m)",
         "<20% de la deuda en próximos 2 años = ok. >40% = "
         "refinancing risk material."),
        ("% Fixed-rate debt",
         "Más alto = menos sensitivity a rates. <50% en alza de tasas "
         "= EPS pressure."),
    ],
    bullish_vs_bearish=[
        ("Net debt / EBITDA <2x",
         "Net debt / EBITDA >5x"),
        ("Interest coverage >8x",
         "Interest coverage <2x"),
        ("Maturity wall <20% próximos 2y",
         "Maturity wall >40% próximos 2y"),
        ("Investment grade (BBB- o mejor)",
         "High yield (BB+ o peor)"),
        ("Mayor parte deuda fixed-rate",
         "Mayor parte floating en alza de tasas"),
        ("Credit spread tightening",
         "Credit spread widening (mercado pricea más riesgo)"),
    ],
    valuation_impact=(
        "La deuda alta inflados ROE / EPS / share buyback capacity en "
        "el corto plazo — pero comprime el multiple porque el mercado "
        "exige más retorno por el riesgo. En DCF, la deuda reduce el "
        "WACC inicialmente (debt es más barato que equity), pero "
        "después de cierto punto el costo de equity explota (Modigliani-"
        "Miller con bankruptcy costs). El sweet spot es leverage moderado. "
        "Empresas con balance fortress (Apple, Microsoft) merecen "
        "multiples premium por la optionality."
    ),
    case_study=(
        "**Boeing 2019-2024**: 737 MAX grounding + COVID = revenue "
        "colapsó. Deuda pasó de $14B (2018) a $58B (2020 peak). "
        "Interest coverage cayó de 25x a 2x. Stock perdió 65%. "
        "Lección: una empresa con high operating leverage + high "
        "financial leverage está doble-expuesta.\n\n"
        "**Caso limpio — Microsoft 2024**: $74B cash vs $51B debt = "
        "$23B net cash. Interest coverage >50x. Esto le permite hacer "
        "la mayor adquisición tech (Activision $69B) sin estrés. "
        "Balance fortress = optionality."
    ),
    common_mistakes=[
        "Mirar solo el ratio Debt/Equity sin chequear interest coverage.",
        "Ignorar el maturity wall — una empresa puede ser solvente y aún así colapsar si no puede refinanciar en mal momento.",
        "Olvidar la deuda off-balance-sheet (pensions, leases, supply chain financing).",
        "Asumir que la deuda en moneda fuerte de una empresa EM es segura. Devaluation puede multiplicar la deuda en moneda local.",
        "Pasar por alto los covenants — un breach puede acelerar toda la deuda.",
    ],
    mental_model=(
        "Munger: 'el primer principio del éxito a largo plazo es no "
        "quebrar'. La deuda es la herramienta más eficaz para "
        "quebrar. Cuando analizás una empresa, hacé el ejercicio de "
        "stress-test mental: ¿qué pasa si revenue cae 30% por 2 años? "
        "¿el balance lo soporta? Las empresas que sobreviven todo "
        "ciclo son las que tienen balance fortress. Las que vuelan "
        "alto en bull markets pero quiebran en recesiones — son las "
        "leveraged."
    ),
    books=[_BOOK_SECURITY_ANALYSIS, _BOOK_DALIO_PRINCIPLES,
           _BOOK_KLARMAN_MOS, _BOOK_BUFFETT_LETTERS],
    videos=[_VIDEO_DAMODARAN_CORPFIN,
            Video(title="Ray Dalio · How Debt Cycles Work",
                  channel="Bridgewater / Principles", minutes=15,
                  url="",
                  why="Dalio sobre el ciclo de deuda — relevante para "
                       "entender cuándo el leverage se vuelve sistémico.")],
    quotes=[_Q_GRAHAM_MOS,
            Quote(text="Volatility is far from synonymous with risk. "
                       "Real risk arises from the combination of "
                       "leverage and uncertainty.",
                  author="Warren Buffett",
                  source="Berkshire 2014 letter"),
            Quote(text="It's only when the tide goes out that you "
                       "learn who's been swimming naked.",
                  author="Warren Buffett",
                  source="Berkshire 2001 letter")],
))

# ---------- Dilution ----------
_add(Lesson(
    slug="dilution",
    label=_label_for("dilution"),
    category=_cat_for("dilution"),
    hook=_hook_for("dilution"),
    definition=(
        "Dilución es la reducción del porcentaje de ownership de un "
        "accionista cuando la empresa emite nuevas acciones. Las dos "
        "fuentes más comunes:\n\n"
        "  · **Stock-based compensation (SBC)**: equity entregado a "
        "empleados como parte de su pago. Más usado en tech.\n"
        "  · **Capital raises / secondary offerings**: la empresa "
        "emite acciones para financiar M&A, capex o pagar deuda.\n\n"
        "El efecto: vos tenías 1% de la empresa, ahora tenés 0.95% — "
        "tus future cash flows por acción se diluyeron. El EPS "
        "denominador crece, comprimiendo la métrica."
    ),
    why_matters=(
        "La dilución es el costo escondido del growth. Tech companies "
        "muestran 'adjusted EPS' que excluye SBC — pero SBC es un costo "
        "real, simplemente no en cash. Mary Buffett dijo: 'el SBC es la "
        "única forma de que el management le robe directamente a los "
        "accionistas y lo llame compensation'. Una empresa que crece "
        "20% en revenue pero diluye 6% por año en acciones, crece solo "
        "14% por share — y eso es lo que vos ganás."
    ),
    how_pros_analyze=(
        "1. **Tracking de shares outstanding**: 5-10 años. ¿Sube por "
        "SBC + raises o baja por buybacks? El neto importa.\n"
        "2. **SBC / Revenue (%)**: en tech, 5-15% es típico. >20% es "
        "alarmante. Snowflake 30% en 2022 — destruía valor real.\n"
        "3. **SBC / FCF**: si SBC es 50% de FCF, la mitad del 'cash "
        "earned' es realmente dilución encubierta.\n"
        "4. **Buybacks netos**: empresa madura. Buybacks > SBC = "
        "shareholder-friendly. Buybacks < SBC = solo cosmético "
        "(compra acciones pero emite más).\n"
        "5. **Dilution per year (CAGR)**: % crecimiento anual de "
        "shares outstanding. >2% sostenido es problemático."
    ),
    key_metrics=[
        ("Shares outstanding · trend 10y",
         "Subiendo = dilución. Bajando = empresa retorna capital."),
        ("SBC / Revenue (%)",
         "Tech: <5% bueno · 5-15% típico · >15% alarmante."),
        ("SBC / FCF (%)",
         "<25% manageable. >50% = la mitad del FCF es dilución."),
        ("Net buyback (shares retired − shares issued)",
         "Positivo = neto reductor. Negativo = neto dilutivo."),
        ("Dilution per year (%)",
         "ΔShares Out YoY. >2% sostenido es preocupante."),
        ("Diluted vs basic EPS",
         "Gap mide la dilución latent (options + RSUs). Un gap >5% "
         "es alto."),
    ],
    bullish_vs_bearish=[
        ("Shares outstanding bajando 1-3% anual (buybacks netos)",
         "Shares outstanding subiendo >2% anual (dilución estructural)"),
        ("SBC / Revenue <10% en tech",
         "SBC / Revenue >20% (Snowflake-style)"),
        ("Buybacks > SBC (real retorno)",
         "Buybacks solo igualan SBC (cosmético)"),
        ("Capital raises raros y a precios premium",
         "Capital raises frecuentes a descuento"),
        ("Diluted EPS converge con basic",
         "Gap diluted-basic creciendo año a año"),
    ],
    valuation_impact=(
        "El intrinsic value SIEMPRE se calcula sobre shares diluidos "
        "(option + RSU + convertibles fully diluted), no sobre shares "
        "actuales. Un DCF que ignora SBC sobreestima el valor por "
        "5-20% en tech. La regla simple: EPS sostenible debería "
        "incluir SBC como expense (Damodaran insiste en esto). Una "
        "empresa que reporta 'adjusted EPS' inflado por exclusion de "
        "SBC está engañando."
    ),
    case_study=(
        "**Snowflake 2021-2024**: revenue creció ~50% CAGR pero "
        "shares outstanding también creció ~10% YoY por SBC. "
        "GAAP EPS siempre negativo, 'adjusted' positivo — la "
        "diferencia era casi enteramente SBC. Stock cayó 60% en 2022 "
        "cuando el mercado empezó a valorar SBC como costo real.\n\n"
        "**Contraejemplo — Apple**: shares outstanding cayó de "
        "26B (2012) a 15B (2024) — recompró 42% de la empresa. "
        "Vos comprabas 1 share en 2012, hoy representa 1.7x del "
        "ownership de entonces. Esa es la opuesta de dilución: "
        "compounding del per-share value."
    ),
    common_mistakes=[
        "Confiar en 'adjusted EPS' que excluye SBC. SBC es un costo real.",
        "Celebrar buybacks sin chequear que netean el SBC. Muchos solo lo igualan.",
        "Ignorar la dilución por options/warrants in-the-money que aún no se ejercieron.",
        "Asumir que capital raises son siempre malos. En empresas growth raise a multiples premium pueden ser accretive.",
        "Pasar por alto convertible debt — eventualmente se convierte a equity.",
    ],
    mental_model=(
        "Buffett mira shares outstanding cada año. Si vos tenés 1% de "
        "una empresa hoy y dentro de 5 años tenés 1.2% (porque la "
        "empresa recompró acciones), entonces creciste tu ownership "
        "aunque no compraste más. Eso es compounding silencioso. Lo "
        "opuesto: si tu 1% se vuelve 0.8% en 5 años por dilución, "
        "perdiste 20% de tu pie del pastel sin venderlo. La dilución "
        "es el robo más sutil al accionista."
    ),
    books=[_BOOK_BUFFETT_LETTERS, _BOOK_DAMODARAN_VALUATION,
           Book(title="The Outsiders", author="William Thorndike",
                year=2012, chapter_hint="Cómo allocators great evitan dilución",
                why="Los CEOs analizados todos compartían un patrón: "
                     "recompras a precios bajos, raises a precios altos."),
           _BOOK_INTELLIGENT_INVESTOR],
    videos=[_VIDEO_BUFFETT_1996, _VIDEO_DAMODARAN_CORPFIN],
    quotes=[
        Quote(text="If options aren't a form of compensation, what are "
                   "they? If compensation isn't an expense, what is it? "
                   "And, if expenses shouldn't go into the calculation "
                   "of earnings, where in the world should they go?",
              author="Warren Buffett",
              source="Berkshire 1998 letter"),
        _Q_BUFFETT_PRICE_VALUE,
        Quote(text="Diluting existing shareholders to compensate "
                   "employees is fine — as long as everyone is honest "
                   "about the cost.",
              author="Mary Buffett",
              source="Buffettology"),
    ],
))
_stub("unit_economics",
      [_BOOK_FISHER,
       Book(title="The Lean Startup", author="Eric Ries", year=2011,
            chapter_hint="Caps. 6-9 (build-measure-learn)",
            why="Aunque es de startups, define unit economics modernos.")],
      [], [_Q_LYNCH_INVERT])
# ---------- Pricing power ----------
_add(Lesson(
    slug="pricing_power",
    label=_label_for("pricing_power"),
    category=_cat_for("pricing_power"),
    hook=_hook_for("pricing_power"),
    definition=(
        "Pricing power es la capacidad de una empresa de subir precios "
        "sin perder volumen materialmente. No es 'tener precios altos' "
        "— es **poder subirlos cuando hace falta** sin que los "
        "clientes se vayan.\n\n"
        "Test simple (Buffett): 'si podés aumentar el precio 10% sin "
        "perder ningún cliente, tenés un excelente negocio. Si para "
        "eso tenés que rezar antes de hacerlo, es un negocio "
        "terrible.'\n\n"
        "Pricing power es **la manifestación financiera del moat**. "
        "Donde hay pricing power, hay competitive advantage; donde "
        "no, hay commoditización."
    ),
    why_matters=(
        "En entorno inflacionario, pricing power es la única defensa. "
        "Empresas sin pricing power ven los costos subir + los "
        "márgenes caer (margen comprimido). Empresas con pricing "
        "power pasan los costos al consumidor + márgenes estables. "
        "Por eso en los 1970s las pocas empresas que prosperaron — "
        "Coca-Cola, Disney, See's Candy — eran las que podían subir "
        "precios sin justificarse. Buffett las llamó 'inflation hedges'."
    ),
    how_pros_analyze=(
        "1. **Track record de price increases**: ¿la empresa aumentó "
        "precios above-inflation en los últimos 10 años? See's Candy "
        "lo hizo cada año durante décadas.\n"
        "2. **Volume durante price increases**: si subieron precios "
        "y volume se mantuvo o creció, pricing power real. Si volume "
        "cayó proporcionalmente, no hay PP.\n"
        "3. **Gross margin trend en recesiones**: empresas sin "
        "pricing power suelen perder margin en downturn. Las con PP "
        "lo mantienen o expanden.\n"
        "4. **Mix shift hacia premium**: ¿la empresa puede vender "
        "más high-end? Lululemon, Apple — sí. Walmart — limitado.\n"
        "5. **Customer concentration**: si tu top 3 clientes son "
        "50% del revenue, ellos tienen pricing power sobre vos.\n"
        "6. **Switching costs**: alto switching = pricing power "
        "estructural (ERP software, banking core systems)."
    ),
    key_metrics=[
        ("Price contribution to revenue growth (%)",
         "Empresas grandes lo reportan. Pricing positivo 5+ años = PP "
         "demostrado."),
        ("Gross margin trend",
         "Estable o expansivo con costos subiendo = PP. Cae con "
         "inflación = no hay PP."),
        ("Price elasticity",
         "Difícil de calcular exacto pero proxies: volume reaction a "
         "price increases."),
        ("Customer concentration (top 10 %)",
         "<30% = pricing power propio · >50% = clientes tienen poder."),
        ("Brand premium vs commodity",
         "Apple iPhone $1200 vs Android genérico $200 mismo hardware = "
         "PP de marca."),
    ],
    bullish_vs_bearish=[
        ("Aumenta precios above-inflation sin perder volume",
         "Tiene que descontar para mantener volume"),
        ("Gross margin estable o expansiva durante inflación",
         "Gross margin se comprime con cost inflation"),
        ("Mix shift hacia productos premium",
         "Mix shift hacia low-end / value tier"),
        ("Pocos competidores con producto diferenciado",
         "Many competitors, producto comoditizado"),
        ("Switching costs altos (data, integración, certificación)",
         "Producto fácilmente sustituible"),
    ],
    valuation_impact=(
        "Pricing power justifica multiples MÁS altos por dos razones: "
        "(1) márgenes más altos en bottom line, (2) earnings más "
        "predecibles (la empresa puede defender el cash flow en "
        "downturns). En DCF, asumir pricing power te permite modelar "
        "EBITDA margins crecientes — pero solo es legítimo si hay "
        "evidencia histórica. Una empresa con PP demostrado merece "
        "premium de 20-40% en P/E vs un peer commodity-like."
    ),
    case_study=(
        "**Disney parks 1955-2020**: ticket price de Disneyland en "
        "1955: $1. En 2020: ~$150. Un aumento de 4.6% CAGR "
        "consistente — por encima de inflation US (3.2% CAGR mismo "
        "período). Visitors per year crecieron de 3.6M a 18M. Pricing + "
        "volume both up. Pricing power textbook.\n\n"
        "**Contraejemplo — airlines pre-bankruptcy**: la industria "
        "tenía cero pricing power por décadas. Cualquier intento de "
        "subir precios resultaba en que un competidor mantenía y "
        "robaba market share. Después de las múltiples bankruptcies "
        "y consolidación 2005-2015, industria pasó de 8+ jugadores "
        "a 4 → pricing power emergió. Los multiples siguieron."
    ),
    common_mistakes=[
        "Confundir precios altos con pricing power. Una empresa puede tener precios premium pero no poder subirlos.",
        "Asumir PP basado en marca sin verificar el track record cuantitativo.",
        "Ignorar el efecto de competencia futura. PP histórico no garantiza PP futuro (Kodak, Sears).",
        "Pasar por alto PP en B2B services. Software ERP, cloud hyperscalers tienen PP por switching costs.",
        "No considerar que en deflación / recesión, PP de luxury bienes se erosiona (Tiffany pre-LVMH).",
    ],
    mental_model=(
        "Buffett: 'si podés subir precios sin reuniones interminables "
        "y sin preocuparte por perder clientes, tenés un gran negocio. "
        "Si para subir 1 centavo tenés que rezar al cielo, tenés un "
        "negocio terrible'. Pricing power es la prueba más limpia de "
        "moat — no requiere modelos complejos, solo mirar el "
        "historial de precios y de volume."
    ),
    books=[_BOOK_BUFFETT_LETTERS, _BOOK_FISHER, _BOOK_MCKINSEY_VALUATION,
           Book(title="The Pricing Strategy Handbook",
                author="Thomas Nagle", year=2016,
                chapter_hint="Caps. 1-4",
                why="Manual técnico de pricing strategy.")],
    videos=[_VIDEO_BUFFETT_1996,
            Video(title="Buffett on Pricing Power",
                  channel="Berkshire annual meeting clips", minutes=8,
                  url="",
                  why="Clip clásico donde Buffett explica See's "
                       "Candy como case study.")],
    quotes=[
        Quote(text="The single most important decision in evaluating "
                   "a business is pricing power. If you've got the "
                   "power to raise prices without losing business to a "
                   "competitor, you've got a very good business.",
              author="Warren Buffett",
              source="FCIC interview 2010"),
        _Q_BUFFETT_MOAT,
        Quote(text="See's Candies was the first 'great' business we "
                   "ever bought. We paid $25 million for it in 1972 — "
                   "and over the years we've taken out something close "
                   "to $2 billion in pre-tax earnings.",
              author="Warren Buffett",
              source="Berkshire 2007 letter"),
    ],
))
_stub("guidance",
      [_BOOK_BUFFETT_LETTERS, _BOOK_LYNCH],
      [_VIDEO_BUFFETT_1996], [_Q_LYNCH_INVERT, _Q_MUNGER_INCENTIVES])
# ---------- Cyclicality ----------
_add(Lesson(
    slug="cyclicality",
    label=_label_for("cyclicality"),
    category=_cat_for("cyclicality"),
    hook=_hook_for("cyclicality"),
    definition=(
        "Una empresa es cíclica cuando sus earnings, márgenes y ROIC "
        "fluctúan significativamente con el ciclo económico — no por "
        "decisiones internas sino por demanda externa que sube y baja. "
        "Industrias cíclicas clásicas:\n\n"
        "  · **Materiales**: aceros, químicos, miners\n"
        "  · **Industriales**: capex equipment, machinery, autos\n"
        "  · **Energía**: oil & gas (precio del subyacente)\n"
        "  · **Semis**: super-cíclica por inventory cycle\n"
        "  · **Consumer discretionary**: hoteles, cruceros, luxury\n"
        "  · **Bancos**: por credit cycle\n\n"
        "El problema crítico: en peak earnings se ven baratas (P/E "
        "bajo) y en trough caras (P/E alto o negativo). El value trap "
        "más clásico es comprar cíclicas en el peak."
    ),
    why_matters=(
        "Cíclicas representan ~25% del S&P. Si no las podés valuar, "
        "perdés un cuarto del mercado. Pero el error más común del "
        "retail es aplicar P/E o ROIC point-in-time sin normalizar "
        "por ciclo. Una acerera con P/E 6 en peak earnings cae 60% "
        "cuando los earnings se normalizan. Buffett evita la mayoría "
        "de cíclicas porque dice que 'predecir el ciclo es difícil "
        "y comprar empresas predecibles es mejor'."
    ),
    how_pros_analyze=(
        "1. **Through-the-cycle earnings**: promediar EPS de los "
        "últimos 7-10 años (cubrir un ciclo completo). Damodaran usa "
        "esto para EPV en cíclicas.\n"
        "2. **Normalized ROIC**: ROIC promedio del ciclo, no spot. "
        "Mineras pueden tener ROIC 30% en peak y -10% en trough — "
        "el normalizado es ~12%.\n"
        "3. **Shiller P/E (CAPE)**: P/E sobre earnings ajustados por "
        "inflation y promediados 10 años. Útil para mercados completos "
        "y cíclicas individuales.\n"
        "4. **Commodity correlation**: en miners / energy, el "
        "precio del subyacente (oro, petróleo, cobre) drivea TODO. "
        "Forecast del precio = forecast del earnings.\n"
        "5. **Capacity discipline**: ¿la industria está sumando "
        "capacidad agresivamente (peak) o cortando capex (trough)? "
        "Capex cycle leads earnings cycle.\n"
        "6. **Position en el ciclo**: late cycle indicators "
        "(margins record, capex en peak, inventory build) anticipan "
        "el turn."
    ),
    key_metrics=[
        ("Through-cycle EPS",
         "Promedio EPS 7-10 años. Más estable que EPS LTM."),
        ("Normalized ROIC (10y avg)",
         "ROIC promedio del ciclo. Compare vs WACC."),
        ("Shiller P/E (CAPE)",
         "Precio / EPS ajustado inflation 10y. <15 cheap · 15-25 fair · "
         ">30 expensive."),
        ("Commodity / Volume sensitivity",
         "% Δ EBIT per % Δ commodity / volume. Mide el operating "
         "leverage cíclico."),
        ("Position in cycle (qualitative)",
         "Early-mid-late-trough. Late + recovering = best buy point."),
    ],
    bullish_vs_bearish=[
        ("P/E alto en trough (earnings deprimidos, recovery próxima)",
         "P/E bajo en peak (value trap clásico)"),
        ("CAPE / through-cycle P/E razonable",
         "Spot P/E bajo pero CAPE elevado"),
        ("Capacity discipline (cuts capex en trough)",
         "Capacity adds en peak (preparándose para crash)"),
        ("Sector trough con sentiment bearish (capitulation)",
         "Sector peak con sentiment euphoric"),
        ("Balance fortress que sobrevive trough",
         "Leverage alto en peak (no podrá soportar trough)"),
    ],
    valuation_impact=(
        "Aplicar DCF a cíclicas usando peak earnings sobreestima por "
        "30-50%; usando trough earnings subestima. La técnica correcta "
        "es **normalize**: EBIT margin promedio del ciclo, asumir "
        "ROIC normalizado, modelar reversion. Multiples sobre cíclicas "
        "deben usar through-cycle earnings — Shiller's CAPE es la "
        "versión index-wide del concepto. En cíclicas extremas (oil "
        "& gas, miners), valuación basada en NAV de reservas + cost "
        "curve es más útil que earnings multiples."
    ),
    case_study=(
        "**ArcelorMittal 2008**: la acerera más grande del mundo. En "
        "2007 (peak del cycle) reportaba EPS $7 y cotizaba P/E 9 — "
        "se veía como bargain absoluto. 2008-2009 EPS colapsó a -$1, "
        "el stock cayó 80%. Lección: P/E 9 sobre peak earnings es "
        "más caro que P/E 25 sobre normalized earnings.\n\n"
        "**Caso clásico — Oil majors 2020**: en abril 2020, oil cayó "
        "a $-37 (negative). XOM, CVX cotizaban como nunca habían "
        "estado en décadas, dividend yield 10%+. Los que compraron "
        "ese trough hicieron 5x en 2 años. Los que vendieron en el "
        "peak de 2007 ($147 oil) hicieron lo mismo al revés."
    ),
    common_mistakes=[
        "Aplicar P/E point-in-time. Siempre usar through-cycle earnings en cíclicas.",
        "Comprar cíclicas en peak earnings (cuando se ven baratas). El P/E bajo es señal de RIESGO, no de oportunidad.",
        "Vender cíclicas en trough (cuando se ven caras). El P/E alto refleja earnings deprimidos temporalmente.",
        "Asumir que el management va a ser disciplinado en capacity. Casi nunca lo es — los CEOs construyen en peak.",
        "Ignorar el balance. Una cíclica con high leverage en peak es prácticamente garantizada de stress en trough.",
    ],
    mental_model=(
        "Marks: 'el inversor exitoso no es el que pega al peak o al "
        "trough — es el que evita comprar en el peak'. Para cíclicas, "
        "la mentalidad es contraria: cuando el sentimiento es eufórico "
        "y los multiples bajos, vendé; cuando el sentimiento es "
        "depresivo y los multiples altos (por earnings deprimidos), "
        "comprá. Es psicológicamente difícil pero matemáticamente "
        "correcto."
    ),
    books=[_BOOK_MARKS_MARKET_CYCLE, _BOOK_DAMODARAN_VALUATION,
           _BOOK_MARKS_MOST_IMPORTANT, _BOOK_DALIO_PRINCIPLES],
    videos=[Video(title="Howard Marks · You Can't Predict, You Can Prepare",
                  channel="Oaktree", minutes=45, url="",
                  why="Filosofía de invertir en cíclicas sin "
                       "predecir el timing exacto.")],
    quotes=[
        _Q_MARKS_RISK,
        Quote(text="The greatest mistake you can make in cyclical "
                   "industries is to extrapolate the current "
                   "conditions indefinitely.",
              author="Howard Marks",
              source="Mastering the Market Cycle"),
        _Q_BUFFETT_PRICE_VALUE,
    ],
))
# ---------- Competitive advantages ----------
_add(Lesson(
    slug="competitive_advantages",
    label=_label_for("competitive_advantages"),
    category=_cat_for("competitive_advantages"),
    hook=_hook_for("competitive_advantages"),
    definition=(
        "Una ventaja competitiva (CA) es cualquier factor que le "
        "permite a una empresa generar **rentabilidad superior al "
        "costo de capital de forma sostenida**, mientras enfrenta "
        "competencia. Moats (lección aparte) son las ventajas "
        "**estructurales y duraderas**; competitive advantages "
        "incluye también las temporales (first-mover, execution, "
        "speed).\n\n"
        "Bruce Greenwald (Columbia) sintetizó las únicas tres "
        "fuentes reales de CA sostenibles:\n\n"
        "  1. **Supply-side advantages** (costos): producción más "
        "barata por escala, tech propietaria, acceso a recursos.\n"
        "  2. **Demand-side advantages** (clientes): switching costs, "
        "habit, network effects, search costs.\n"
        "  3. **Economies of scale**: cuando los fixed costs son "
        "grandes y un competidor más grande pueda lograr menor "
        "costo unitario."
    ),
    why_matters=(
        "Sin CA, los retornos altos atraen competencia hasta que "
        "convergen al WACC. CON CA, los retornos persisten — y eso "
        "es lo que distingue una empresa que compounding 30 años "
        "de una que se vuelve mediocre en 10. Identificar la "
        "**fuente exacta** de la CA es crucial: 'Apple tiene moat' "
        "es vago — ¿es brand, switching cost (iCloud + App Store), "
        "ecosystem effect, o supply chain dominance? Cada una "
        "implica una amenaza distinta y una durabilidad distinta."
    ),
    how_pros_analyze=(
        "1. **Greenwald test**: ¿esta CA es verdaderamente "
        "estructural o solo execution? Execution es replicable; "
        "estructural no.\n"
        "2. **Source identification**: scale economies, network "
        "effects, switching costs, brand, regulatory licenses. "
        "Múltiples al mismo tiempo = moat más ancho.\n"
        "3. **Durability test**: ¿qué tendría que pasar para que "
        "esta CA se erosione? Si la respuesta es 'tech disruption' "
        "→ tech moats son CORTOS. Si es 'cambio cultural de "
        "consumidor' → décadas.\n"
        "4. **Measurement vía ROIC durability**: ROIC > WACC durante "
        "10+ años es prueba empírica de CA real.\n"
        "5. **Watch erosion signals**: market share loss, "
        "pricing power compresión, capex requirement creciendo "
        "para sostener share."
    ),
    key_metrics=[
        ("ROIC > WACC duration",
         "Cuántos años consecutivos. >10 años = CA estructural."),
        ("Market share trend",
         "Estable / creciendo = CA funcional. Decreciendo = CA "
         "erosionándose."),
        ("Gross margin durability",
         "Margen alto y estable through cycles = pricing power = CA."),
        ("Customer retention (NRR en SaaS, churn en consumer)",
         "Alta retention = switching costs / brand habits."),
        ("Capex per unit of growth",
         "Bajo = scale economies. Subiendo = CA debilitándose "
         "(necesita más inversión para mismos retornos)."),
    ],
    bullish_vs_bearish=[
        ("Multiple CA sources simultáneas (network + scale + brand)",
         "Una sola CA o difusa"),
        ("ROIC > WACC 10+ años consecutivos",
         "ROIC > WACC erratic / declining"),
        ("Market share estable o creciendo",
         "Market share erosionándose con tiempo"),
        ("CA replicable solo con capital infinito",
         "CA imitable con execution decente"),
        ("Switching costs estructurales (data, regulación)",
         "Switching costs convenience-based (fáciles de superar)"),
    ],
    valuation_impact=(
        "Las empresas con CA real merecen DCF con competitive "
        "advantage period (CAP) más largo y ROIC steady-state más "
        "alto. Damodaran asume típicamente 5-10 años de CAP; "
        "empresas con CA structural pueden tener 15-25. Esta sola "
        "assumption puede agregar 30-60% al intrinsic value. En "
        "multiples: P/E premium de 30-100% vs sector average para "
        "empresas con moat demostrado."
    ),
    case_study=(
        "**ASML — el monopolio EUV**: única empresa del mundo que "
        "produce EUV lithography (la maquinaria para hacer chips "
        "<7nm). Switching cost técnico imposible — los fabs (TSMC, "
        "Samsung, Intel) DEBEN comprarles. ROIC 30%+ consistente. "
        "Stock 30x en una década. CA structural definitiva: monopolio "
        "tecnológico + regulatory moat (US/Netherlands restringe "
        "exports a China).\n\n"
        "**Contraejemplo — Kodak**: tenía CA aparentemente "
        "indestructible (brand, distribución, patents en film). Pero "
        "la CA era específica de UNA tecnología (chemical film). "
        "Cuando llegó digital, la CA evaporó en una década. Bankrupt "
        "2012. Lección: las CA basadas en tecnología específica son "
        "frágiles ante paradigm shifts."
    ),
    common_mistakes=[
        "Confundir 'empresa grande' con 'empresa con moat'. Sears, Kodak, Nokia fueron gigantes sin CA estructural.",
        "Asumir que la CA es permanente. Hay que validar que sigue intacta cada año.",
        "Identificar CA solo por la narrativa. Hay que verificarlo empíricamente con ROIC > WACC duradero.",
        "Subestimar las CA invisible (regulación, certificaciones, distribution networks).",
        "Pasar por alto que en tech, las CA se erosionan más rápido que en consumer / financials.",
    ],
    mental_model=(
        "Buffett: 'la mejor metáfora para una gran empresa es un castillo "
        "con un foso ancho. El foso es la competitive advantage. Lo que "
        "buscás es un foso que sea Profundo, Ancho, Y que la dirección "
        "esté ensanchándolo continuamente'. Pensá en cada empresa que "
        "analizás: ¿cuál es exactamente el foso? Si no podés "
        "identificarlo en una oración, capaz no existe."
    ),
    books=[_BOOK_BUFFETT_LETTERS, _BOOK_FISHER,
           Book(title="Competition Demystified",
                author="Bruce Greenwald", year=2005,
                chapter_hint="Toda la parte II — los 3 tipos de CA",
                why="El framework más riguroso para identificar CA "
                     "reales vs falsas."),
           Book(title="7 Powers", author="Hamilton Helmer", year=2016,
                chapter_hint="Cap. 1-7 — los 7 tipos de power",
                why="Framework moderno: scale economies, network "
                     "economies, counter-positioning, switching costs, "
                     "branding, cornered resource, process power.")],
    videos=[_VIDEO_BUFFETT_1996,
            Video(title="Hamilton Helmer · 7 Powers",
                  channel="Talks at Google", minutes=60,
                  url="",
                  why="El autor explica los 7 tipos de power business.")],
    quotes=[
        _Q_BUFFETT_MOAT,
        Quote(text="There are only three genuine sources of competitive "
                   "advantage: supply, demand, and economies of scale. "
                   "Everything else is execution.",
              author="Bruce Greenwald",
              source="Competition Demystified"),
        Quote(text="In the absence of a strategy, hard work is just "
                   "running on a treadmill.",
              author="Hamilton Helmer",
              source="7 Powers"),
    ],
))
_stub("saas_metrics",
      [Book(title="The SaaS Playbook", author="Rob Walling", year=2022,
            chapter_hint="Caps. 1-4", why="Métricas SaaS modernas claras.")],
      [Video(title="Rule of 40 and Why It Matters",
             channel="Bessemer Venture Partners", minutes=12,
             url="", why="VC explica las métricas que miran en SaaS.")],
      [])
_stub("banking_metrics",
      [_BOOK_CFA, _BOOK_DAMODARAN_VALUATION],
      [], [])
_stub("insurance_metrics",
      [_BOOK_BUFFETT_LETTERS,
       Book(title="The Davis Dynasty", author="John Rothchild", year=2001,
            chapter_hint="Sobre Shelby Davis y el negocio de insurance",
            why="Cómo pensar insurance como business.")],
      [_VIDEO_BUFFETT_1996], [])
_stub("semis_metrics",
      [Book(title="Chip War", author="Chris Miller", year=2022,
            chapter_hint="Caps. sobre TSMC + ASML",
            why="Historia + estructura de la industria semis.")],
      [], [])
_stub("consumer_brands",
      [_BOOK_BUFFETT_LETTERS, _BOOK_FISHER],
      [_VIDEO_BUFFETT_1996], [_Q_BUFFETT_MOAT])
_stub("network_effects",
      [Book(title="The Cold Start Problem", author="Andrew Chen", year=2021,
            chapter_hint="Toda la parte I",
            why="Cómo se construyen y se rompen los network effects.")],
      [], [])

# Valuación (stubs)
_stub("multiples_overview",
      [_BOOK_DAMODARAN_VALUATION, _BOOK_MCKINSEY_VALUATION],
      [_VIDEO_DAMODARAN_VALUATION], [_Q_DAMODARAN_STORY])
# ---------- EV/EBITDA ----------
_add(Lesson(
    slug="ev_ebitda",
    label=_label_for("ev_ebitda"),
    category=_cat_for("ev_ebitda"),
    hook=_hook_for("ev_ebitda"),
    definition=(
        "EV/EBITDA = Enterprise Value / EBITDA. Mide cuántas veces el "
        "EBITDA anual paga el COMPRADOR ENTERO de la empresa (asumiendo "
        "que también asume la deuda).\n\n"
        "  · **Enterprise Value** = Market Cap + Total Debt − Cash + "
        "Minority Interest. Es el costo de comprar el negocio COMPLETO, "
        "no solo el equity.\n"
        "  · **EBITDA** = Earnings Before Interest, Taxes, Depreciation, "
        "Amortization. El cash operating earnings antes de capital "
        "structure y D&A.\n\n"
        "Es preferido en M&A y para empresas con leverage variable: "
        "neutraliza el efecto del capital structure (EV incluye deuda, "
        "EBITDA es pre-interest), permitiendo comparar manzanas con "
        "manzanas entre empresas con distinta capital structure."
    ),
    why_matters=(
        "P/E se afecta por capital structure (interest expense + tax). "
        "Dos empresas idénticas operacionalmente pero con distinta deuda "
        "tendrán P/E distintos — pero el mismo EV/EBITDA. Por eso "
        "EV/EBITDA es el múltiplo de elección en industrias con "
        "diversidad de leverage (industriales, telecom, M&A "
        "comparables). Críticos como Buffett y Munger lo desprecian "
        "('EBITDA omite el D&A que es real cost') pero los private "
        "equity lo usan como religion."
    ),
    how_pros_analyze=(
        "1. **EV calculation correcta**: market cap (todas las clases "
        "de shares) + total debt (no solo long-term) + minority "
        "interest + preferred − cash & marketable securities − "
        "investments. Si te olvidás minority interest o preferred, "
        "subestimás EV.\n"
        "2. **Compare vs peers, no aislado**. EV/EBITDA 8x es "
        "expensive en utilities (típico 6x) y cheap en software "
        "(típico 18x).\n"
        "3. **Forward EBITDA**: para growth companies, usar NTM "
        "EBITDA refleja mejor.\n"
        "4. **Adjusted EBITDA**: empresas reportan 'adjusted EBITDA' "
        "excluyendo SBC, restructurings, etc. Validar que las "
        "adjustments son razonables. SBC NUNCA debería excluirse.\n"
        "5. **Watch EBITDA margin trend**: si EBITDA margin se "
        "comprime, el multiple debería bajar simultáneamente."
    ),
    key_metrics=[
        ("EV / EBITDA LTM",
         "Industriales ~10x · software ~18x · utilities ~9x · "
         "energy ~5-8x · consumer staples ~14x."),
        ("EV / EBITDA forward (NTM)",
         "Preferido para growth. Usar consensus estimates."),
        ("EBITDA margin (%)",
         "Determina la calidad del EBITDA. >30% capital-light, "
         "<15% capital-intensive."),
        ("EV / FCFF",
         "Una alternativa que SÍ deduce D&A & CapEx — más honesta para "
         "empresas capital-intensive."),
        ("Net debt / EBITDA",
         "El leverage. <2x conservador · >5x stress."),
    ],
    bullish_vs_bearish=[
        ("EV/EBITDA < peer median con EBITDA growth",
         "EV/EBITDA premium pero EBITDA estancado"),
        ("Adjusted EBITDA cercano a reported (ajustes mínimos)",
         "Adjusted EBITDA >>> GAAP EBITDA (ajustes agresivos)"),
        ("EBITDA margin estable o expansive",
         "EBITDA margin contracting (debilidad operacional)"),
        ("EV calculation incluye todo (minority, preferred)",
         "Análisis usa solo equity / ignora minority — subestima EV"),
        ("EV/FCFF y EV/EBITDA convergen",
         "Gap grande EV/FCFF >> EV/EBITDA (capex eating EBITDA)"),
    ],
    valuation_impact=(
        "El intrinsic EV/EBITDA se deriva de: ROIC, growth, "
        "reinvestment rate. **Implied EV/EBITDA ≈ (1 − tax) × "
        "(1 − reinvestment) / (WACC − g)**. Una empresa con ROIC alto "
        "+ growth alto + WACC bajo justifica EV/EBITDA 20x+. Por eso "
        "Visa cotiza ~25x EV/EBITDA — los fundamentals lo soportan. "
        "Cuando el multiple actual > implied, hay sobre-valuación; "
        "cuando < implied, oportunidad."
    ),
    case_study=(
        "**M&A de TXU Energy 2007 → bankruptcy 2014**: KKR + TPG "
        "compraron Texas energy company por $45B (incluye assumed "
        "debt) — el LBO más grande de la historia. EV/EBITDA del "
        "deal: ~12x. Tesis: natural gas iba a subir. Natural gas "
        "cayó. Con 7x leverage no había margen para error. "
        "Bankrupted en 2014. Lección: EV/EBITDA alto + leverage alto "
        "= cero margin of safety.\n\n"
        "**Caso clásico — Tobacco companies pre-Master Settlement 1998**: "
        "cotizaban EV/EBITDA ~5x cuando el resto del consumer staples "
        "estaba ~12x. Mercado descontaba litigation risk. Los que "
        "compraron en el bottom ganaron 10-20x en la siguiente "
        "década. Multiple expansion (de 5x a 12x) fue la mitad del "
        "retorno."
    ),
    common_mistakes=[
        "Olvidar minority interest y preferred en el cálculo de EV.",
        "Comparar EV/EBITDA entre industrias (utilities vs software no son comparables).",
        "Usar 'adjusted EBITDA' sin validar las ajustments. SBC es un costo real.",
        "Aplicar EV/EBITDA a financials (bancos, aseguradoras). No tiene sentido — debt es input no debt.",
        "Ignorar que high-capex industries (telecom, miners) tienen EBITDA inflado vs FCF. EV/FCFF es más honesto.",
    ],
    mental_model=(
        "Munger: 'cada vez que escucho EBITDA pienso bullshit "
        "earnings'. Su punto: D&A es un costo real (la maquinaria se "
        "deprecia, hay que reemplazarla). EBITDA es útil para "
        "comparar capital structures distintos, pero NUNCA debería "
        "ser el único múltiplo. Siempre cross-check con EV/FCFF y "
        "ROIC. Si EV/EBITDA dice 'cheap' pero EV/FCFF dice 'caro', "
        "creé al EV/FCFF."
    ),
    books=[_BOOK_DAMODARAN_VALUATION, _BOOK_MCKINSEY_VALUATION,
           _BOOK_CFA],
    videos=[_VIDEO_DAMODARAN_VALUATION],
    quotes=[
        _Q_DAMODARAN_STORY,
        Quote(text="Every time I hear EBITDA I substitute it with "
                   "'bullshit earnings'. Depreciation is a real cost.",
              author="Charlie Munger",
              source="Berkshire annual meeting (multiple)"),
        Quote(text="EBITDA is what management would like you to focus "
                   "on. Operating cash flow is what they don't.",
              author="Aswath Damodaran",
              source="Damodaran NYU lectures"),
    ],
))
# ---------- P/E ratio ----------
_add(Lesson(
    slug="pe_ratio",
    label=_label_for("pe_ratio"),
    category=_cat_for("pe_ratio"),
    hook=_hook_for("pe_ratio"),
    definition=(
        "Price-to-Earnings (P/E) = Price per Share / EPS. Dice "
        "cuántos años de earnings actuales pagarías por una acción "
        "si los earnings se mantuvieran constantes. Es el múltiplo "
        "más conocido y más mal usado.\n\n"
        "Variantes críticas:\n"
        "  · **Trailing P/E (LTM)**: sobre earnings últimos 12 meses. "
        "Histórico, no proyecta nada.\n"
        "  · **Forward P/E**: sobre estimates del próximo año. "
        "Refleja expectativas.\n"
        "  · **Shiller / CAPE**: sobre earnings promediados 10 años "
        "ajustados por inflation. Smooth cyclicality.\n"
        "  · **Ex-cash P/E**: P/E ajustado por cash neto en balance.\n\n"
        "Históricamente el S&P promedió P/E ~16. Pero el promedio "
        "esconde rangos: 7 en 1980, 33 en 2000, 26 en 2024."
    ),
    why_matters=(
        "P/E es el atajo mental que el 90% del mercado usa para "
        "decidir 'barato vs caro'. Lo problemático: P/E aisle no "
        "dice casi nada sin contexto. Una P/E 30 puede ser barato "
        "(growth alto + ROIC alto) o caro (peak earnings + sin "
        "growth). Y P/E 5 puede ser ganga (mispricing) o trampa "
        "(value trap en peak cíclico). Saber CUÁNDO P/E aplica y "
        "cuándo no es lo que separa a un analista de un screener."
    ),
    how_pros_analyze=(
        "1. **No usar P/E aislado**. Siempre combinar con: growth "
        "(PEG), ROIC, quality of earnings.\n"
        "2. **Compare vs historical own**: ¿la empresa cotiza a "
        "P/E 28 que es 1 std arriba de su 10y mean? Eso es "
        "información.\n"
        "3. **Forward vs trailing**: forward P/E es preferible para "
        "growth companies; trailing para mature stable.\n"
        "4. **Adjust for non-recurring**: si EPS LTM incluye un "
        "one-time gain, P/E parece bajo pero es engañoso.\n"
        "5. **Cyclicality check**: en cyclical companies, usar CAPE "
        "/ through-cycle earnings, NUNCA trailing.\n"
        "6. **No usar en empresas con earnings negativos o "
        "volátiles**. P/E meaningful requiere earnings positivos y "
        "predecibles."
    ),
    key_metrics=[
        ("Trailing P/E (LTM)",
         "S&P promedio histórico ~16. >25 expensive · <12 cheap "
         "(con contexto)."),
        ("Forward P/E (NTM)",
         "Sobre estimates próximos 12m. Más útil para growth."),
        ("Shiller P/E (CAPE)",
         "Earnings 10y ajustados inflation. <15 cheap · >30 "
         "expensive."),
        ("P/E relative to history",
         "Z-score del P/E actual vs 10y propio. >1 std = expensive."),
        ("P/E relative to peers",
         "Premium / discount vs sector median."),
    ],
    bullish_vs_bearish=[
        ("P/E forward < historical avg con ROIC sólido",
         "P/E LTM bajo en cyclical peak (value trap)"),
        ("P/E ajustado por cash/leverage razonable",
         "P/E sobre EPS inflado por one-time / SBC excluido"),
        ("P/E vs growth: PEG <1.5 con calidad",
         "P/E premium pero growth desacelerando"),
        ("Shiller CAPE razonable",
         "Spot P/E bajo pero CAPE elevado (peak)"),
        ("Quality of earnings alto (FCF conversion >80%)",
         "EPS inflado por accruals (low quality earnings)"),
    ],
    valuation_impact=(
        "P/E es un proxy, no un valor intrínseco. El P/E justificado "
        "se deriva del Gordon growth model: **P/E = payout × (1+g) / "
        "(Ke − g)**. Una empresa con payout 50%, growth 8%, Ke 9% "
        "tiene P/E justificado = 50% × 1.08 / (0.09 − 0.08) = 54x. "
        "Esto explica por qué growth + low Ke + sustainable payout "
        "= multiples altos. Cuando el mercado paga P/E muy alto, "
        "tenés que verificar que los tres componentes lo soporten."
    ),
    case_study=(
        "**Nvidia 2023**: cotizaba a forward P/E ~25 después del "
        "rally. Si miras solo P/E, parecía expensive. Pero earnings "
        "estaban creciendo >100% YoY por AI demand. Un PEG <1 = "
        "still cheap given growth. Los que vendieron por 'P/E "
        "alto' perdieron otros 3x.\n\n"
        "**Contraejemplo — Ford 2022**: trailing P/E 4. Looked like "
        "absurd bargain. Pero earnings estaban en peak (post-COVID "
        "auto shortage + pricing power temporal). Cuando se "
        "normalizó, EPS cayó 60% y el P/E 'subió' a 12 sin que el "
        "stock se moviera. Classic value trap por usar P/E LTM en "
        "cyclical en peak."
    ),
    common_mistakes=[
        "Comparar P/E entre industrias sin ajustar. Software P/E 30 ≠ utilities P/E 30.",
        "Usar P/E LTM en cyclicals. Siempre normalizar.",
        "Ignorar la diferencia entre P/E (sobre EPS LTM) y forward P/E. Pueden diverger 30%+.",
        "Confiar en 'adjusted EPS' inflado por exclusion de SBC. Usar GAAP EPS o ajustar manualmente.",
        "Asumir que P/E bajo siempre es barato. A veces es CAUSA — la empresa se está deteriorando.",
    ],
    mental_model=(
        "Damodaran: 'P/E es la métrica más fácil de calcular y la más "
        "fácil de malinterpretar'. Antes de usar P/E, preguntate: "
        "¿los E son sostenibles? ¿son representativos del ciclo? "
        "¿de qué calidad? ¿están inflados por one-time / contabilidad? "
        "El P/E es útil DESPUÉS de responder esas preguntas — antes, "
        "es solo un ratio."
    ),
    books=[_BOOK_INTELLIGENT_INVESTOR, _BOOK_DAMODARAN_VALUATION,
           _BOOK_MCKINSEY_VALUATION],
    videos=[_VIDEO_DAMODARAN_VALUATION,
            Video(title="The Trouble with P/E Ratios",
                  channel="Aswath Damodaran", minutes=30, url="",
                  why="Damodaran explica las trampas más comunes.")],
    quotes=[
        _Q_BUFFETT_PRICE_VALUE,
        _Q_DAMODARAN_STORY,
        Quote(text="The P/E ratio is the price of a dream. If the "
                   "dream is real, the multiple is justified. If not, "
                   "it's a bubble.",
              author="Aswath Damodaran",
              source="Investment Valuation"),
    ],
))
_stub("peg",
      [_BOOK_LYNCH, _BOOK_DAMODARAN_VALUATION],
      [], [_Q_LYNCH_INVERT])
_stub("sotp",
      [_BOOK_DAMODARAN_VALUATION, _BOOK_MCKINSEY_VALUATION],
      [], [])
# ---------- Terminal value ----------
_add(Lesson(
    slug="terminal_value",
    label=_label_for("terminal_value"),
    category=_cat_for("terminal_value"),
    hook=_hook_for("terminal_value"),
    definition=(
        "Terminal value (TV) es el valor presente de todos los cash "
        "flows MÁS ALLÁ del período explícito del DCF. Si modelás "
        "FCF años 1-10, el TV captura años 11 hasta infinito.\n\n"
        "Las dos metodologías:\n\n"
        "**1. Gordon Growth (perpetuity)**: TV = FCF_n+1 / (WACC − g)\n"
        "  · Asume crecimiento perpetuo a tasa g (típicamente 2-3%).\n"
        "  · Sencillo pero ULTRA-sensible a g.\n\n"
        "**2. Exit multiple**: TV = EBITDA_n × Multiple\n"
        "  · Asume que en año n vendés la empresa a un multiple "
        "razonable.\n"
        "  · Más práctico pero introduce circularidad (el multiple "
        "futuro depende del mismo growth/WACC del DCF).\n\n"
        "En un DCF típico, el TV representa 60-80% del valor total. "
        "Pequeñas variaciones en assumptions de TV mueven mucho el "
        "intrinsic."
    ),
    why_matters=(
        "El TV es donde casi todo el valor de un DCF reside. Una "
        "diferencia de 50bp en g terminal o 100bp en WACC cambia el "
        "TV 15-25%, y por tanto el intrinsic value en proporción. "
        "Por eso Damodaran insiste: 'el TV no es un afterthought, es "
        "la mitad del modelo'. Y por eso un DCF con TV mal pensado "
        "no vale el papel donde está impreso."
    ),
    how_pros_analyze=(
        "1. **g terminal cap**: NO puede ser > growth nominal del PIB "
        "del país (~3-4% en developed markets, ~5-7% EM). Una empresa "
        "no puede crecer indefinidamente más rápido que la economía — "
        "eventualmente absorbería todo.\n"
        "2. **TV % of total PV**: si TV > 75% del valor total, el "
        "DCF es básicamente una apuesta sobre la perpetuidad. "
        "Reducir el período explícito o cuestionar assumptions.\n"
        "3. **Implied multiple check**: calcular el multiple "
        "implícito del TV. Si TV / EBITDA_n implica P/E 50x, ¿es "
        "razonable para una empresa madura?\n"
        "4. **Steady-state ROIC**: en el TV, asumir ROIC = WACC + "
        "small premium (Koller). ROIC steady-state >25% es asumir "
        "moat extraordinario perpetuo.\n"
        "5. **Reinvestment rate consistency**: si g = 3%, ROIC = "
        "12%, entonces reinvestment rate = 3/12 = 25%. FCF = NOPAT × "
        "(1 − 25%). Los tres componentes (g, ROIC, RR) deben ser "
        "consistentes."
    ),
    key_metrics=[
        ("g terminal (%)",
         "Cap: nominal GDP growth (~2-4% developed). Más es agresivo."),
        ("TV / Total PV (%)",
         ">75% = casi todo en perpetuidad (frágil). <60% = OK."),
        ("Implied steady-state ROIC",
         ">25% requiere moat extraordinario justificado. 10-15% es "
         "típico."),
        ("Reinvestment rate (g / ROIC)",
         "Debería estar 25-50% de NOPAT. >75% sustainability cuestionable."),
        ("Exit multiple implied",
         "Si exit multiple > current multiple del sector, expansión "
         "asumida (frágil)."),
    ],
    bullish_vs_bearish=[
        ("TV / PV ≤ 65% (forecast explícito carga el peso)",
         "TV / PV > 80% (toda la valuación es la perpetuidad)"),
        ("g terminal ≤ nominal GDP",
         "g terminal > nominal GDP (matemáticamente imposible "
         "long-term)"),
        ("Implied steady ROIC 10-15% (plausible)",
         "Implied steady ROIC >25% sin moat estructural"),
        ("Exit multiple razonable vs sector",
         "Exit multiple > sector premium implícito"),
    ],
    valuation_impact=(
        "TV mueve TODO el intrinsic value. Sensitivity: en un DCF "
        "típico, +50bp en g terminal → +12-18% intrinsic. +100bp en "
        "WACC → -15-25% intrinsic. Por eso una matriz de sensitivity "
        "WACC × g terminal es obligatoria — no para presentar 'cuánto "
        "vale' sino para mostrar 'cuán fragil es el modelo a las "
        "assumptions'."
    ),
    case_study=(
        "**Tesla 2020-2024**: muchos DCFs publicados en 2020-2021 "
        "asumían g terminal 4-5% (above-GDP) + steady ROIC 20%+. "
        "Justificaban valuaciones $1T+. Damodaran público mostró "
        "que con assumptions más sobrias (g = 2.5%, ROIC = 12%), el "
        "intrinsic era ~$200-300/share. El stock corrigió de $400 a "
        "$120 en 2022. La mayoría del rerating fue ajustar el "
        "TV assumptions, no las del forecast explícito.\n\n"
        "**Caso clásico — Disney late 1990s**: DCFs con TV "
        "asumiendo 6% growth perpetuo + ROIC 18%. Cuando los "
        "earnings se estabilizaron y growth normalizó al 3-4%, el "
        "stock se estancó por una década. Lección: TV optimista = "
        "tiempo lateral mientras los fundamentals validan o no la "
        "tesis."
    ),
    common_mistakes=[
        "Asumir g terminal > nominal GDP growth. Matemáticamente roto a largo plazo.",
        "Permitir que TV > 80% del PV total — el modelo es una apuesta sobre la perpetuidad, no análisis.",
        "Usar exit multiple sin verificar que sea consistente con WACC, g y ROIC asumidos (circularidad).",
        "Asumir ROIC steady-state alto (>20%) sin moat estructural justificado. La competencia eventualmente convergerá ROIC al WACC.",
        "No hacer sensitivity sobre TV. Es la assumption más importante; presentar un point estimate es ingenuo.",
    ],
    mental_model=(
        "Damodaran: 'in valuation, the terminal value is where "
        "dreams come true and models come undone'. Pensá el TV no "
        "como 'la respuesta' sino como 'la apuesta'. Cada DCF está "
        "implícitamente apostando a una combinación de growth + ROIC "
        "+ WACC para los próximos infinitos años. Si esa apuesta es "
        "razonable, el DCF tiene valor. Si requiere assumptions "
        "agresivas, tu intrinsic value es solo papel."
    ),
    books=[_BOOK_DAMODARAN_VALUATION, _BOOK_MCKINSEY_VALUATION,
           _BOOK_KLARMAN_MOS],
    videos=[_VIDEO_DAMODARAN_VALUATION,
            Video(title="Terminal Value: The Most Important Number "
                       "in DCF",
                  channel="Aswath Damodaran", minutes=45, url="",
                  why="Damodaran enseña cómo NO arruinar tu DCF "
                       "con un TV malo.")],
    quotes=[
        _Q_DAMODARAN_STORY,
        Quote(text="The terminal value is the most important number "
                   "in your DCF and the one most likely to be wrong.",
              author="Aswath Damodaran",
              source="Investment Valuation"),
        Quote(text="If your terminal growth rate exceeds the growth "
                   "rate of the economy, you're implicitly assuming "
                   "your company will eventually become the entire "
                   "economy.",
              author="Tim Koller (McKinsey)",
              source="Valuation, 7th ed."),
    ],
))
_stub("sensitivity_analysis",
      [_BOOK_MCKINSEY_VALUATION], [_VIDEO_DAMODARAN_VALUATION], [])
_stub("scenario_analysis",
      [_BOOK_MARKS_MOST_IMPORTANT, _BOOK_KLARMAN_MOS],
      [], [_Q_MARKS_RISK])
_stub("intrinsic_value",
      [_BOOK_INTELLIGENT_INVESTOR, _BOOK_BUFFETT_LETTERS, _BOOK_DAMODARAN_VALUATION],
      [_VIDEO_BUFFETT_1996], [_Q_BUFFETT_PRICE_VALUE])

# Sectores (stubs)
_stub("sector_banks",
      [_BOOK_DAMODARAN_VALUATION, _BOOK_DALIO_PRINCIPLES],
      [], [])
_stub("sector_tech",
      [Book(title="The Innovator's Dilemma", author="Clayton Christensen",
            year=1997, chapter_hint="Toda la parte I",
            why="Por qué las empresas tech grandes pierden contra disruptores.")],
      [], [])
_stub("sector_utilities",
      [_BOOK_CFA, _BOOK_DAMODARAN_VALUATION], [], [])
_stub("sector_energy",
      [Book(title="The Prize", author="Daniel Yergin", year=1991,
            chapter_hint="Cómo se forma el ciclo de oil",
            why="Historia + estructura de la industria energética.")],
      [], [])
_stub("sector_consumer",
      [_BOOK_FISHER, _BOOK_BUFFETT_LETTERS], [_VIDEO_BUFFETT_1996],
      [_Q_BUFFETT_MOAT])
_stub("sector_industrials",
      [_BOOK_MCKINSEY_VALUATION, _BOOK_MARKS_MARKET_CYCLE], [], [])
_stub("sector_healthcare",
      [_BOOK_FISHER, _BOOK_DAMODARAN_VALUATION], [], [])
_stub("sector_semis",
      [Book(title="Chip War", author="Chris Miller", year=2022,
            chapter_hint="Estructura competitiva moderna",
            why="The book on semis right now.")],
      [], [])

# Macro (stubs)
_stub("interest_rates",
      [_BOOK_DALIO_PRINCIPLES, _BOOK_JPM_GUIDE], [], [])
_stub("credit_spreads",
      [_BOOK_MARKS_MARKET_CYCLE,
       Book(title="The Bond Book", author="Annette Thau", year=2010,
            chapter_hint="Caps. sobre HY + IG",
            why="Texto de referencia para entender bond markets.")],
      [], [_Q_MARKS_RISK])
_stub("gdp",
      [_BOOK_JPM_GUIDE, _BOOK_DALIO_PRINCIPLES], [], [])
_stub("unemployment",
      [_BOOK_DALIO_PRINCIPLES, _BOOK_JPM_GUIDE], [], [])
_stub("monetary_policy",
      [_BOOK_DALIO_PRINCIPLES,
       Book(title="The Lords of Easy Money", author="Christopher Leonard",
            year=2022, chapter_hint="Toda",
            why="La Fed desde adentro post-2008.")],
      [Video(title="How the Federal Reserve Works",
             channel="Federal Reserve", minutes=30, url="",
             why="Material oficial introductorio.")],
      [])
_stub("fiscal_policy",
      [_BOOK_DALIO_PRINCIPLES, _BOOK_JPM_GUIDE], [], [])
_stub("liquidity",
      [_BOOK_MARKS_MARKET_CYCLE, _BOOK_DALIO_PRINCIPLES], [], [])
_stub("recession_indicators",
      [_BOOK_MARKS_MARKET_CYCLE, _BOOK_DALIO_PRINCIPLES], [], [])
_stub("dollar_strength",
      [_BOOK_JPM_GUIDE], [], [])
_stub("commodity_cycles",
      [Book(title="The Prize", author="Daniel Yergin", year=1991,
            chapter_hint="Historia de ciclos de oil",
            why="Caso paradigmático de commodity cycle.")],
      [], [])

# Mercado (stubs)
_stub("risk_on_off",
      [_BOOK_MARKS_MOST_IMPORTANT, _BOOK_MARKS_MARKET_CYCLE], [],
      [_Q_MARKS_RISK])
_stub("positioning",
      [_BOOK_MARKS_MARKET_CYCLE,
       Book(title="Reminiscences of a Stock Operator",
            author="Edwin Lefèvre", year=1923, chapter_hint="Cualquiera",
            why="Cómo pensaba un trader profesional (Jesse Livermore) sobre positioning.")],
      [], [])
_stub("sentiment",
      [_BOOK_MARKS_MOST_IMPORTANT,
       Book(title="The Little Book of Behavioral Investing",
            author="James Montier", year=2010,
            chapter_hint="Caps. 1-5", why="Sesgos cognitivos en inversión.")],
      [], [_Q_MARKS_RISK])
_stub("volatility",
      [_BOOK_MARKS_MOST_IMPORTANT,
       Book(title="The Volatility Smile", author="Emanuel Derman",
            year=2016, chapter_hint="Caps. introductorios",
            why="Cómo entender vol surface — denso pero el original.")],
      [], [])
_stub("earnings_season",
      [_BOOK_LYNCH, _BOOK_BUFFETT_LETTERS],
      [_VIDEO_BUFFETT_1996], [_Q_LYNCH_INVERT])
_stub("institutional_flows",
      [_BOOK_JPM_GUIDE,
       Book(title="Pioneering Portfolio Management",
            author="David Swensen", year=2009,
            chapter_hint="Asset allocation institutional",
            why="Cómo piensa el CIO de Yale sobre flows + asset classes.")],
      [], [])
_stub("market_regimes",
      [_BOOK_MARKS_MARKET_CYCLE, _BOOK_DALIO_PRINCIPLES], [],
      [_Q_MARKS_RISK])
_stub("factor_investing",
      [Book(title="Your Complete Guide to Factor-Based Investing",
            author="Larry Swedroe", year=2016,
            chapter_hint="Caps. 1-8 — value, momentum, quality, size",
            why="Resumen accesible del literature académico.")],
      [Video(title="Ben Felix · Factor Investing",
             channel="Common Sense Investing", minutes=15, url="",
             why="El YouTuber que mejor explica factors a retail.")],
      [])
_stub("momentum",
      [Book(title="Quantitative Momentum",
            author="Wesley Gray & Jack Vogel", year=2016,
            chapter_hint="Caps. 1-4",
            why="El factor con evidence empírico más robusto, explicado.")],
      [], [])
_stub("growth_vs_value",
      [_BOOK_INTELLIGENT_INVESTOR, _BOOK_FISHER, _BOOK_BUFFETT_LETTERS],
      [_VIDEO_BUFFETT_1996], [_Q_BUFFETT_PRICE_VALUE])


# ============================================================
# Public API
# ============================================================
def get_lesson(slug: str) -> Optional[Lesson]:
    """Devuelve la Lesson para un slug, o None si no existe."""
    return _LESSONS.get(slug)


def n_complete() -> int:
    """Cuántas lecciones tienen contenido completo (no solo stub)."""
    return sum(1 for l in _LESSONS.values() if l.is_complete)


def n_total() -> int:
    return len(_LESSONS)
