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


# Empresas (stubs)
_stub("revenue_growth",
      [_BOOK_DAMODARAN_VALUATION, _BOOK_LYNCH, _BOOK_FISHER],
      [_VIDEO_DAMODARAN_VALUATION],
      [_Q_LYNCH_INVERT, _Q_DAMODARAN_STORY])
_stub("margins",
      [_BOOK_MCKINSEY_VALUATION, _BOOK_BUFFETT_LETTERS],
      [_VIDEO_BUFFETT_1996],
      [_Q_BUFFETT_MOAT])
_stub("operating_leverage",
      [_BOOK_MCKINSEY_VALUATION, _BOOK_DAMODARAN_VALUATION],
      [_VIDEO_DAMODARAN_CORPFIN],
      [_Q_DAMODARAN_STORY])
_stub("roe",
      [_BOOK_MCKINSEY_VALUATION, _BOOK_CFA],
      [_VIDEO_DAMODARAN_CORPFIN],
      [_Q_BUFFETT_MOAT])
_stub("debt_analysis",
      [_BOOK_SECURITY_ANALYSIS, _BOOK_DALIO_PRINCIPLES, _BOOK_KLARMAN_MOS],
      [_VIDEO_DAMODARAN_CORPFIN],
      [_Q_GRAHAM_MOS])
_stub("dilution",
      [_BOOK_BUFFETT_LETTERS, _BOOK_DAMODARAN_VALUATION],
      [_VIDEO_BUFFETT_1996], [_Q_BUFFETT_PRICE_VALUE])
_stub("unit_economics",
      [_BOOK_FISHER,
       Book(title="The Lean Startup", author="Eric Ries", year=2011,
            chapter_hint="Caps. 6-9 (build-measure-learn)",
            why="Aunque es de startups, define unit economics modernos.")],
      [], [_Q_LYNCH_INVERT])
_stub("pricing_power",
      [_BOOK_BUFFETT_LETTERS, _BOOK_FISHER, _BOOK_MCKINSEY_VALUATION],
      [_VIDEO_BUFFETT_1996], [_Q_BUFFETT_MOAT])
_stub("guidance",
      [_BOOK_BUFFETT_LETTERS, _BOOK_LYNCH],
      [_VIDEO_BUFFETT_1996], [_Q_LYNCH_INVERT, _Q_MUNGER_INCENTIVES])
_stub("cyclicality",
      [_BOOK_MARKS_MARKET_CYCLE, _BOOK_DAMODARAN_VALUATION],
      [], [_Q_MARKS_RISK])
_stub("competitive_advantages",
      [_BOOK_BUFFETT_LETTERS, _BOOK_FISHER,
       Book(title="Competition Demystified", author="Bruce Greenwald",
            year=2005, chapter_hint="Toda la parte II",
            why="Marco analítico riguroso de moats, desde Columbia.")],
      [_VIDEO_BUFFETT_1996], [_Q_BUFFETT_MOAT])
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
_stub("ev_ebitda",
      [_BOOK_DAMODARAN_VALUATION, _BOOK_MCKINSEY_VALUATION],
      [_VIDEO_DAMODARAN_VALUATION], [_Q_DAMODARAN_STORY])
_stub("pe_ratio",
      [_BOOK_INTELLIGENT_INVESTOR, _BOOK_DAMODARAN_VALUATION],
      [_VIDEO_DAMODARAN_VALUATION], [_Q_BUFFETT_PRICE_VALUE])
_stub("peg",
      [_BOOK_LYNCH, _BOOK_DAMODARAN_VALUATION],
      [], [_Q_LYNCH_INVERT])
_stub("sotp",
      [_BOOK_DAMODARAN_VALUATION, _BOOK_MCKINSEY_VALUATION],
      [], [])
_stub("terminal_value",
      [_BOOK_DAMODARAN_VALUATION, _BOOK_MCKINSEY_VALUATION],
      [_VIDEO_DAMODARAN_VALUATION], [_Q_DAMODARAN_STORY])
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
