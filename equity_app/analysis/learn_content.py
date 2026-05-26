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
# ---------- Unit economics ----------
_add(Lesson(
    slug="unit_economics",
    label=_label_for("unit_economics"),
    category=_cat_for("unit_economics"),
    hook=_hook_for("unit_economics"),
    definition=(
        "Unit economics es el análisis de la rentabilidad de UNA "
        "transacción o UN cliente — antes de mirar los costos fijos "
        "corporativos. Pregunta: ¿cada cliente / producto / orden "
        "individualmente genera contribution margin positivo?\n\n"
        "Las métricas centrales en SaaS / consumer subscription:\n"
        "  · **CAC** (Customer Acquisition Cost): cuánto cuesta "
        "adquirir UN cliente nuevo.\n"
        "  · **LTV** (Lifetime Value): cuánto cash genera ese cliente "
        "durante su vida útil.\n"
        "  · **Payback period**: meses para que CAC se recupere con "
        "gross profit del cliente.\n"
        "  · **LTV/CAC ratio**: ≥3x considerado sano.\n\n"
        "Para empresas de hardware / retail: contribution margin "
        "por unidad y break-even volume."
    ),
    why_matters=(
        "Una empresa puede crecer revenue rápidamente y aún perder "
        "más plata cuanto más vende — si las unit economics son "
        "negativas. Es exactamente lo que pasó con MoviePass, "
        "Casper, Blue Apron, varias DTCs y miles de SaaS pre-IPO. "
        "Unit economics positivas son el filtro #1 antes de evaluar "
        "growth — sin ellas, el crecimiento es destrucción de capital."
    ),
    how_pros_analyze=(
        "1. **Fully-loaded CAC**: incluir TODO el costo de marketing "
        "+ sales + onboarding. Muchas empresas reportan 'paid CAC' "
        "(solo ads) — subestimar el total real.\n"
        "2. **LTV calculation realistic**: usar churn observable, no "
        "wishful thinking. Y descontar future cash flows (LTV NPV).\n"
        "3. **Cohort analysis**: trackear cohorts (mes/año de "
        "adquisición) separadamente. Permite ver si cohorts nuevos "
        "son mejores o peores que los antiguos.\n"
        "4. **Payback period**: <12 meses es excellent. >24 meses = "
        "stress (necesitás mucho capital working hasta recuperar el "
        "CAC).\n"
        "5. **Contribution margin per unit (no SaaS)**: para retail, "
        "DTCs, fintechs, mirar cuántas unidades necesitás para "
        "cubrir fixed costs.\n"
        "6. **Scale economies en CAC**: ¿el CAC crece con scale "
        "(saturación de mercado) o baja (network effects)?"
    ),
    key_metrics=[
        ("CAC (USD)",
         "Costo fully-loaded de adquirir 1 cliente. Comparar vs LTV."),
        ("LTV (USD)",
         "Lifetime value. = Avg revenue × gross margin × avg "
         "customer lifespan."),
        ("LTV / CAC ratio",
         ">3x healthy · 1-3x marginal · <1x destrucción de valor."),
        ("Payback period (months)",
         "<12m excellent · 12-24m OK · >24m capital-hungry."),
        ("Contribution margin per unit",
         "Para hardware/retail. Negativo = perdés en cada unidad."),
        ("Cohort retention curve",
         "% de cohort retenido después de N meses. Curva estable = "
         "sticky product."),
    ],
    bullish_vs_bearish=[
        ("LTV/CAC >3x sostenido en múltiples cohorts",
         "LTV/CAC <2x o cayendo cohort over cohort"),
        ("Payback period <12 meses",
         "Payback >24 meses (capital intensity disfrazada)"),
        ("CAC bajando con scale (network effects)",
         "CAC subiendo con scale (saturación del canal)"),
        ("Cohorts nuevos mejoran (NRR >100%)",
         "Cohorts nuevos peores (signs de mercado saturándose)"),
        ("Mix de canales orgánicos (low CAC)",
         "Crecimiento 100% paid (alto CAC, frágil ante ad costs)"),
    ],
    valuation_impact=(
        "Para SaaS / DTC pre-IPO, unit economics es la BASE de la "
        "valuación. Una empresa con LTV/CAC 5x puede sostenibly "
        "spendar en marketing — su growth es escalable. Una con LTV/CAC "
        "1.5x está quemando capital — su 'growth' termina cuando se "
        "acaba el cash. Damodaran insiste: **growth sin unit "
        "economics positivas no agrega valor, lo destruye**. En DCF, "
        "modelar contribution margin por cohort y la trayectoria del "
        "CAC con scale."
    ),
    case_study=(
        "**Netflix early-2010s**: LTV/CAC ~5x. Cada usuario nuevo "
        "costaba ~$50 en adquisición, generaba ~$250 en LTV "
        "(ARPU × tenure × margin). Eso justificaba gastar agresivo "
        "en marketing + contenido. Stock 50x desde 2012.\n\n"
        "**Contraejemplo — MoviePass 2017-2019**: cobraba $10/mes, "
        "le pagaba al cine $10-15 por película, usuario "
        "promedio veía 3+ films/mes. Contribution margin **negativa** "
        "($-30 por usuario/mes). Más usuarios = más pérdidas. La "
        "empresa explotó cuando el cash se acabó. Caso de unit "
        "economics suicidas escondidas detrás de 'growth'."
    ),
    common_mistakes=[
        "Usar 'paid CAC' (solo ads) en vez de fully-loaded CAC.",
        "Calcular LTV con churn assumptions optimistas no validadas en cohorts reales.",
        "Confundir gross margin alto con unit economics positivas. Gross margin no incluye CAC.",
        "Ignorar que LTV es un FUTURE value — necesita ser descontado al presente.",
        "Asumir que CAC se mantendrá constante con scale. Casi siempre sube (saturación).",
    ],
    mental_model=(
        "Pregunta filosófica del unit economics analyst: 'si la "
        "empresa parase de crecer mañana, ¿el cliente que ya tiene "
        "le da plata?'. Si la respuesta es sí, podés evaluar growth. "
        "Si la respuesta es no, **el growth ES el problema**, no la "
        "solución. Lynch: 'know what you own' — saber unit economics "
        "es la base de saber qué tenés."
    ),
    books=[_BOOK_FISHER,
           Book(title="The Lean Startup", author="Eric Ries", year=2011,
                chapter_hint="Caps. 6-9 (build-measure-learn)",
                why="Define unit economics modernos para startups."),
           Book(title="The SaaS Metrics Handbook", author="David Skok",
                year=2019, chapter_hint="LTV, CAC, magic number",
                why="Texto referencia de SaaS metrics — Skok es el VC "
                     "que popularizó LTV/CAC."),
           _BOOK_DAMODARAN_VALUATION],
    videos=[
        Video(title="David Skok · SaaS Metrics That Matter",
              channel="Matrix Partners", minutes=30, url="",
              why="El framework de SaaS metrics explicado por su autor."),
    ],
    quotes=[
        _Q_LYNCH_INVERT,
        Quote(text="A company that loses money on every sale cannot "
                   "make it up on volume.",
              author="Anónimo / Silicon Valley adage",
              source="Folklore inversión (versión cínica del "
                     "growth-at-all-costs)"),
        _Q_DAMODARAN_STORY,
    ],
))
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
# ---------- Guidance ----------
_add(Lesson(
    slug="guidance",
    label=_label_for("guidance"),
    category=_cat_for("guidance"),
    hook=_hook_for("guidance"),
    definition=(
        "Guidance es la proyección que el management hace público "
        "sobre revenue, márgenes y EPS futuros — típicamente "
        "trimestre o año adelante. Aparece en earnings releases, "
        "conference calls e investor days.\n\n"
        "Tipos:\n"
        "  · **Quantitative guidance**: rango específico de número "
        "(revenue $5.0-5.2B, EPS $1.20-1.25).\n"
        "  · **Directional guidance**: 'esperamos mid-single-digit "
        "growth' sin compromiso numérico.\n"
        "  · **Withdrawal**: pulled guidance — señal de "
        "incertidumbre o stress (COVID 2020, todos retiraron "
        "guidance).\n\n"
        "Buffett y muchos value investors desconfían del guidance — "
        "pero el mercado reacciona violentamente a desvíos."
    ),
    why_matters=(
        "Las acciones se mueven más por desvíos de guidance que por "
        "los earnings absolutos. Empresa beats EPS pero lowers "
        "guidance → stock cae 10%. Empresa misses EPS pero raises "
        "guidance → stock sube. Saber leer el guidance — qué dice, "
        "qué omite, cómo se compara al consensus — es la mitad del "
        "análisis de earnings season."
    ),
    how_pros_analyze=(
        "1. **Compare vs consensus**: el sell-side reúne estimates. "
        "Una empresa que guide 'in line' suena positivo pero si el "
        "consensus estaba ya un poco arriba, en realidad es "
        "downward revision implícita.\n"
        "2. **Components matter**: revenue guidance high, margin "
        "guidance low. Mix matters. Saber cuál driver está stressed.\n"
        "3. **Range width**: rango angosto = confianza, rango ancho "
        "= incertidumbre.\n"
        "4. **Hedging language**: 'subject to FX', 'assuming "
        "macroeconomic stability'. Los caveats son la verdad.\n"
        "5. **History of guide → result**: ¿la empresa históricamente "
        "guides conservative (beat-and-raise) o aggressive (miss)? "
        "Patrones se repiten.\n"
        "6. **Multi-year outlook**: empresas que dan 3y framework "
        "(NVDA, ASML) revelan strategy. Las que no dan = "
        "incertidumbre interna."
    ),
    key_metrics=[
        ("Guidance vs consensus (delta)",
         "Beat: guide > consensus (bullish). Miss: < consensus."),
        ("Guidance range width (%)",
         "(High − Low) / Midpoint. <5% = high confidence; >15% = "
         "low confidence."),
        ("Guide revision frequency",
         "¿Se actualiza mid-quarter? Frecuentes revisions = "
         "volatility in the business."),
        ("Beat-and-raise pattern",
         "% de trimestres con beat + guide-up vs miss + guide-down. "
         "Alto sostenido = management conservador y disciplinado."),
        ("Guidance hit rate (3y history)",
         "% de tiempo que la empresa cumple su own guidance."),
    ],
    bullish_vs_bearish=[
        ("Guidance above consensus, range angosto",
         "Guidance below consensus, range ancho"),
        ("Pattern de beat-and-raise consistente",
         "Pattern de miss-and-lower (management overpromising)"),
        ("Caveats mínimos, language confident",
         "Heavy hedging, 'subject to' múltiples"),
        ("Multi-year framework con milestones",
         "No quantitative guidance (señal de no-visibilidad)"),
        ("Guide se mantiene mid-quarter sin updates",
         "Pre-announce / negative guide mid-quarter"),
    ],
    valuation_impact=(
        "Forward earnings estimates (consensus) drivean directamente "
        "forward multiples. Cuando guidance baja, los forecasts "
        "bajan, el forward P/E sube — y multiple compression sigue. "
        "Empresas con guidance creíble (beat-and-raise pattern) "
        "merecen multiples premium porque tienen menos earnings "
        "risk. Empresas con miss frecuente tienen multiples "
        "comprimidos como descuento por unreliability."
    ),
    case_study=(
        "**Nvidia 2023 Q2**: revenue guidance $11B vs consensus $7B. "
        "Una de las mayores guides-ups en historia tech ($4B "
        "delta). Stock saltó 28% en una sesión. Demostró que la "
        "data center AI demand era genuina, no narrativa.\n\n"
        "**Contraejemplo — Nike 2024**: lowered FY24 guidance dos "
        "trimestres seguidos. Stock cayó 30% acumulado. La señal "
        "subyacente: el moat de Nike erosionándose ante New Balance, "
        "On Running, Hoka — guidance es donde aparece primero el "
        "cambio competitivo, antes de que se vea en revenue absoluto."
    ),
    common_mistakes=[
        "Mirar solo el headline beat/miss sin chequear guidance forward.",
        "Asumir que guide-up siempre = bullish. A veces es 'low bar' después de cut anterior.",
        "Ignorar los hedging caveats en el guidance ('assuming FX neutral', 'subject to').",
        "Confiar en management que históricamente guides aggressive y misses (Tesla en muchos años, biotechs en general).",
        "Olvidar que el mercado pricea el FORWARD, no el LTM. Guide-down con beat-LTM = caída del stock.",
    ],
    mental_model=(
        "Lynch: 'know what you own and know why you own it'. Saber "
        "qué hace una empresa NO alcanza — necesitás saber qué dice "
        "su management sobre el futuro y si históricamente cumple. "
        "Munger: 'show me the incentive'. Management que guides "
        "aggressive tiene incentivos cortoplacistas (option packages). "
        "Management que guides conservative (Buffett-style) tiene "
        "incentivos longplacistas."
    ),
    books=[_BOOK_BUFFETT_LETTERS, _BOOK_LYNCH,
           Book(title="Earnings Magic and the Unbalance Sheet",
                author="Gary Giroux", year=2006,
                chapter_hint="Sobre el efecto de guidance en "
                              "earnings management",
                why="Cómo el guidance crea presión para "
                     "earnings management.")],
    videos=[_VIDEO_BUFFETT_1996,
            Video(title="Reading Between the Lines of Earnings Calls",
                  channel="CFA Institute", minutes=30, url="",
                  why="Cómo decodificar el lenguaje de management.")],
    quotes=[
        _Q_LYNCH_INVERT,
        _Q_MUNGER_INCENTIVES,
        Quote(text="Charlie and I have never given guidance on earnings "
                   "and never will. We think it's a misleading practice "
                   "that encourages playing games with quarterly numbers.",
              author="Warren Buffett",
              source="Berkshire 2002 letter"),
    ],
))
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
# ---------- SaaS metrics ----------
_add(Lesson(
    slug="saas_metrics",
    label=_label_for("saas_metrics"),
    category=_cat_for("saas_metrics"),
    hook=_hook_for("saas_metrics"),
    definition=(
        "SaaS (Software-as-a-Service) requiere métricas distintas a "
        "las clásicas por su modelo de revenue recurrente:\n\n"
        "  · **ARR** (Annual Recurring Revenue): revenue subscription "
        "anualizado.\n"
        "  · **NRR** (Net Revenue Retention): cómo expande la base "
        "existente — incluye upsell, downsell, churn. >120% = "
        "best-in-class.\n"
        "  · **GRR** (Gross Revenue Retention): retention puro, sin "
        "upsell. >90% saludable.\n"
        "  · **Magic Number**: net new ARR / S&M spend. >1.0 = "
        "marketing eficiente.\n"
        "  · **Rule of 40**: growth % + FCF margin %. ≥40 = healthy "
        "balance entre growth e profitability.\n\n"
        "Estas métricas reemplazan o complementan revenue growth + "
        "margin clásicos."
    ),
    why_matters=(
        "SaaS public companies con NRR alta (>120%) cotizan a múltiples "
        "premium (15-25x EV/Revenue) vs las con NRR mediocres "
        "(<105%) que cotizan 5-10x. Para entender si Snowflake "
        "merece P/S 30 o si es burbuja, hay que mirar NRR (~158%) y "
        "Magic Number (~1.5). Saber estas métricas separa el "
        "research SaaS de las generalidades."
    ),
    how_pros_analyze=(
        "1. **NRR > 120% = expansion moat real**: el cliente paga "
        "más año tras año. Significa switching costs altos + value "
        "expansion (más usuarios, más módulos).\n"
        "2. **GRR > 90% sticky**: si solo NRR alta pero GRR baja, "
        "están perdiendo customers pero expandiendo los que quedan — "
        "frágil.\n"
        "3. **Magic Number ≥1**: cada dólar en S&M trae ≥$1 en ARR "
        "nuevo. <0.5 = marketing ineficiente, growth requiere mucho "
        "capital.\n"
        "4. **CAC payback en meses**: <12 meses = best-in-class · "
        "12-24 = OK · >24 = capital-hungry.\n"
        "5. **Rule of 40**: growth% + FCF margin% ≥ 40 indica que "
        "están balanceando growth + profitability. Empresas elite "
        "(Salesforce, ServiceNow) sostienen >50.\n"
        "6. **Cohort analysis**: tracking cohorts permite ver si NRR "
        "está mejorando o empeorando con cada nueva camada."
    ),
    key_metrics=[
        ("ARR (USD)",
         "Annual Recurring Revenue. La cifra absoluta."),
        ("Net Revenue Retention (NRR) %",
         "<100% empresas en problemas · 100-115% normal · "
         ">120% best-in-class · >140% Snowflake-tier."),
        ("Gross Revenue Retention (GRR) %",
         ">90% sticky · 85-90% OK · <85% leakage problemática."),
        ("Magic Number",
         "Net new ARR / S&M spend en quarter. >1 efficient · "
         "0.5-1 OK · <0.5 burning cash."),
        ("Rule of 40",
         "Growth% + FCF margin%. ≥40 healthy · ≥50 elite."),
        ("CAC payback period (months)",
         "<12 excellent · 12-24 OK · >24 capital intensive."),
    ],
    bullish_vs_bearish=[
        ("NRR >120% sostenido (expansión genuina)",
         "NRR <105% o declining (saturación / churn)"),
        ("GRR >90% (sticky product)",
         "GRR <85% (leakage estructural)"),
        ("Magic Number >1",
         "Magic Number <0.5 (marketing ineficiente)"),
        ("Rule of 40 sostenido >40",
         "Rule of 40 <30 (ni growth ni profit)"),
        ("Logo retention alto (no solo $ retention)",
         "Empresa pierde logos pero retiene $ por upsell — frágil"),
    ],
    valuation_impact=(
        "Los SaaS multiples están dirigidos por NRR + growth: "
        "**EV/Revenue ≈ growth × NRR factor**. Snowflake con 30%+ "
        "growth y NRR 158% justifica P/S 20x; Zoom con 5% growth y "
        "NRR 105% cotiza P/S 5x. Cuando NRR cae 10pp, el multiple "
        "se comprime materialmente. El forecast de FCF requiere "
        "modelar cohort dynamics — no se puede simplificar a 'X% "
        "growth, Y% margin'."
    ),
    case_study=(
        "**Snowflake 2020-2024**: IPO con NRR 158% — la más alta "
        "ever en SaaS public. Justificó P/S inicial 80x+. NRR cayó "
        "gradualmente a 127% (2024) y el P/S se comprimió a 15x. El "
        "multiple compression fue ~80% del retorno negativo del "
        "stock. Lección: NRR es el driver clave del SaaS multiple.\n\n"
        "**Caso clásico — Salesforce**: NRR estable ~108-115% por "
        "20 años con scale masivo. Rule of 40 consistente >40. "
        "Multiple stable ~7-10x P/S. Compounded 80x desde IPO 2004."
    ),
    common_mistakes=[
        "Mirar solo revenue growth sin NRR. Empresa puede crecer 30% mientras pierde clientes (solo se sostienen con new logos).",
        "Confundir NRR con GRR. NRR alta con GRR baja = expansion masking churn.",
        "Ignorar la diferencia entre Billings (lo facturado) y Revenue (lo reconocido). Billings forward = pipeline.",
        "Usar 'adjusted FCF' que excluye SBC. SBC en SaaS es ENORME y real.",
        "Aplicar SaaS metrics a empresas que no son verdaderamente SaaS (algo de Zoom no es SaaS, es transactional).",
    ],
    mental_model=(
        "El SaaS analyst piensa cohorts, no agregados. Una empresa "
        "con NRR 130% es una máquina que cada año extrae más "
        "valor de la misma base — sin necesitar nuevos clientes. "
        "Eso es compounding contractual. Una empresa con NRR <100% "
        "está obligada a correr en treadmill — vender nuevos para "
        "compensar los que pierde. La diferencia es estructural, no "
        "ejecutiva."
    ),
    books=[
        Book(title="The SaaS Playbook", author="Rob Walling", year=2022,
             chapter_hint="Caps. 1-4", why="Métricas SaaS modernas claras."),
        Book(title="From Impossible to Inevitable",
             author="Aaron Ross & Jason Lemkin", year=2016,
             chapter_hint="Caps. sobre Hypergrowth",
             why="El libro que estandarizó las métricas SaaS modernas."),
        _BOOK_DAMODARAN_VALUATION,
    ],
    videos=[
        Video(title="Rule of 40 and Why It Matters",
              channel="Bessemer Venture Partners", minutes=12, url="",
              why="VC explica las métricas que miran en SaaS."),
        Video(title="David Skok · SaaS Metrics 2.0",
              channel="Matrix Partners", minutes=45, url="",
              why="El framework de SaaS metrics actualizado por su autor."),
    ],
    quotes=[
        Quote(text="In SaaS, the customer cohort is the unit of "
                   "analysis. If your cohorts are improving, you're "
                   "compounding. If they're decaying, you're "
                   "treadmilling.",
              author="David Skok",
              source="Matrix Partners SaaS Metrics blog"),
        _Q_LYNCH_INVERT,
        _Q_DAMODARAN_STORY,
    ],
))
# ---------- Banking metrics ----------
_add(Lesson(
    slug="banking_metrics",
    label=_label_for("banking_metrics"),
    category=_cat_for("banking_metrics"),
    hook=_hook_for("banking_metrics"),
    definition=(
        "Los bancos requieren un toolkit completamente distinto de "
        "métricas porque su balance ES su negocio (capital regulado, "
        "leverage estructural ~10x, asset-liability matching). Las "
        "métricas centrales:\n\n"
        "  · **NIM** (Net Interest Margin): (Interest income − "
        "interest expense) / Average Earning Assets. El margen del "
        "core lending business.\n"
        "  · **Efficiency ratio**: OpEx / Revenue. <60% bueno · "
        ">70% ineficiente.\n"
        "  · **NPL** (Non-Performing Loans): % del loan book en "
        "default.\n"
        "  · **CET1** (Common Equity Tier 1): capital de mejor "
        "calidad sobre RWA. Regulatorio mínimo ~10%, banks elite "
        ">13%.\n"
        "  · **ROTE / ROE**: return on tangible / total equity.\n"
        "  · **CASA ratio**: deposits low-cost (current + savings) "
        "sobre total deposits. Más CASA = menor cost of funds."
    ),
    why_matters=(
        "Aplicar DCF o P/E como en cualquier otra empresa a un banco "
        "es ingenuidad — funcionalmente roto. Bancos viven en "
        "P/TBV, ROTE, NIM, credit losses. Pre-2008 los analistas que "
        "no entendían el sistema bancario perdieron fortunas — "
        "Lehman cotizaba a P/E 'razonable' justo antes de quebrar. "
        "El que sabía leer CET1, NPL, asset-liability mismatch vio "
        "venir la crisis."
    ),
    how_pros_analyze=(
        "1. **NIM trend with rate cycle**: NIM expande con tasas "
        "subiendo, comprime con tasas bajando (asumiendo "
        "asset-sensitive). Verificar el rate sensitivity.\n"
        "2. **Asset quality**: NPLs creciendo = early warning. "
        "Provisions for credit losses (PCL) prosean cuántos pierden "
        "expected.\n"
        "3. **Capital adequacy**: CET1 > regulatory minimum + buffer "
        "para dividends / buybacks. Bancos US deben mantener "
        "stressed CET1 >5% post-stress.\n"
        "4. **Loan growth vs economy**: bancos creciendo loans 15% "
        "anual en economía 3% growth → potencial credit cycle "
        "deterioration ahead.\n"
        "5. **Deposit franchise**: CASA ratio + customer "
        "concentration. Sticky retail deposits = competitive "
        "advantage; flighty corporate deposits = fragile.\n"
        "6. **Off-balance-sheet exposures**: derivatives, "
        "securitizations, SPEs. Pre-2008 era la zona oculta."
    ),
    key_metrics=[
        ("NIM (%)",
         "US large-cap banks ~3% · EM banks 4-6% · investment "
         "banks <2%."),
        ("Efficiency ratio (%)",
         "<55% best · 55-65% normal · >70% inefficient."),
        ("NPL ratio (%)",
         "<1% clean · 1-3% normal · >3% stress · >5% distress."),
        ("CET1 ratio (%)",
         "Regulatorio: ~7-10%. Banks elite >13%. <8% restricted "
         "dividends."),
        ("ROTE (%)",
         ">15% excellent · 10-15% good · <10% subpar."),
        ("Loan-to-Deposit ratio",
         "<80% conservador · 80-100% normal · >100% funding-dependent."),
        ("CASA ratio (%)",
         "% deposits low-cost. >40% strong franchise · <25% expensive funding."),
    ],
    bullish_vs_bearish=[
        ("NIM expandiendo con tasas subiendo",
         "NIM comprimiendo (mismatch en asset/liability)"),
        ("NPL ratio estable o bajando",
         "NPL ratio subiendo + provisions aumentando"),
        ("CET1 buffer cómodo sobre regulatory",
         "CET1 cerca de mínimo regulatorio (no margen)"),
        ("ROTE >15% sostenido",
         "ROTE <10% (no cubre cost of equity)"),
        ("CASA ratio alto (deposits sticky)",
         "Dependencia de wholesale funding (costoso, flighty)"),
        ("Loan growth ~ GDP growth",
         "Loan growth >> GDP (riesgo de credit cycle)"),
    ],
    valuation_impact=(
        "Bancos cotizan en P/TBV (Price-to-Tangible Book Value), no "
        "P/E como otras empresas. Fórmula: **P/TBV justificado = "
        "(ROTE − g) / (Ke − g)**. Un banco con ROTE 15%, growth 3%, "
        "Ke 10% justifica P/TBV = (0.15−0.03)/(0.10−0.03) = 1.7x. "
        "JPM cotiza P/TBV ~2x porque ROTE 18%+; Citigroup ~0.8x "
        "porque ROTE 7%. La regla simple: **ROTE > Ke → P/TBV > 1**, "
        "**ROTE < Ke → P/TBV < 1**."
    ),
    case_study=(
        "**JPMorgan 2008-2024**: ROTE consistente 15%+ a pesar de la "
        "crisis. CET1 13%+. NIM resiliente con rate cycles. P/TBV "
        "stayed >1.5x. Compounded 5x desde 2009 lows. Caso de "
        "balance sheet + management discipline + scale economies "
        "en banking.\n\n"
        "**Contraejemplo — Silicon Valley Bank (SVB) 2023**: NIM "
        "looked OK pero deposit franchise era 90%+ uninsured "
        "corporate (frágil). Asset-liability mismatch enorme "
        "(bonos largos vs depósitos demandables). Cuando los rates "
        "subieron, las losses unrealized en HTM securities ($16B+) "
        "wiped el equity. Bank run en 48h. Lección: NIM headline "
        "puede esconder fragilidad estructural."
    ),
    common_mistakes=[
        "Aplicar DCF / P/E a bancos. Modelo equivocado, usar P/TBV + RI + DDM.",
        "Mirar solo ROE sin ROTE. ROE incluye goodwill que distorsiona.",
        "Ignorar el asset-liability mismatch. Es la causa más común de bank failures.",
        "Confiar en NPL ratios sin contexto del ciclo. NPLs lag credit deterioration por 6-12 meses.",
        "Pasar por alto que CET1 cerca de minimum = no buybacks / dividend cuts coming.",
    ],
    mental_model=(
        "Buffett (sobre bancos): 'banking is a wonderful business — "
        "if you don't do anything stupid'. Los bancos hacen plata "
        "tomando deposits baratos y prestando a tasas mayores. Lo "
        "estúpido: leverage excesivo, asset-liability mismatch, "
        "exposure a credit cycles que no entendés. Un banco bien "
        "gestionado compounde a 12-15% ROTE durante décadas. Uno "
        "mal gestionado puede wipear todo el equity en un trimestre."
    ),
    books=[_BOOK_CFA, _BOOK_DAMODARAN_VALUATION, _BOOK_BUFFETT_LETTERS,
           Book(title="Bank Investing: A Practitioner's Field Guide",
                author="Jeffrey Davis", year=2021,
                chapter_hint="Toda la parte sobre frameworks",
                why="Manual moderno escrito por un bank analyst.")],
    videos=[
        Video(title="How to Analyze a Bank Stock",
              channel="The Plain Bagel", minutes=15, url="",
              why="Intro accesible a P/TBV + ROTE."),
    ],
    quotes=[
        Quote(text="Banking has been a very good business for a very "
                   "long time. It's not necessary to do brilliant "
                   "things — just don't do dumb things.",
              author="Warren Buffett",
              source="Berkshire annual meeting 1990s"),
        Quote(text="The four most dangerous words in investing are: "
                   "'this time it's different' — and that applies to "
                   "banks in spades.",
              author="John Templeton",
              source="(atribuido)"),
        _Q_BUFFETT_PRICE_VALUE,
    ],
))
# ---------- Insurance metrics ----------
_add(Lesson(
    slug="insurance_metrics",
    label=_label_for("insurance_metrics"),
    category=_cat_for("insurance_metrics"),
    hook=_hook_for("insurance_metrics"),
    definition=(
        "Las aseguradoras hacen plata de DOS fuentes:\n\n"
        "  · **Underwriting profit**: primas cobradas − claims + "
        "expenses. Margen del seguro propiamente dicho.\n"
        "  · **Investment income**: yield del 'float' (primas "
        "cobradas pero no aún pagadas en claims). Buffett construyó "
        "Berkshire sobre este concepto.\n\n"
        "Métricas centrales:\n"
        "  · **Combined ratio**: (Claims + Expenses) / Premiums. "
        "<100% = underwriting profitable · >100% = underwriting loss.\n"
        "  · **Loss ratio**: Claims / Premiums.\n"
        "  · **Expense ratio**: OpEx / Premiums.\n"
        "  · **Float**: liabilities (claims reserves + unearned "
        "premiums) − cash held against them. Capital ajeno que la "
        "aseguradora invierte.\n"
        "  · **Reserves adequacy**: cuán bien estimó claims futuras."
    ),
    why_matters=(
        "Buffett: 'el negocio de seguros, bien manejado, genera "
        "float al costo de menos que zero — significa que te pagan "
        "para mantener capital ajeno'. Esa es la fundación de "
        "Berkshire. Una aseguradora con combined ratio <95% genera "
        "underwriting profit + float gratis. Una con combined ratio "
        ">105% paga por el privilegio de tener float — modelo "
        "destructor de valor."
    ),
    how_pros_analyze=(
        "1. **Combined ratio < 100% = underwriting disciplinado**. "
        "Sostenido <95% es excelente.\n"
        "2. **Loss ratio vs expense ratio**: alto loss ratio = "
        "claims underestimated o underwriting agresivo. Alto expense "
        "= ineficiencia operacional.\n"
        "3. **Reserve development**: ¿reservas estimadas hace 3 años "
        "fueron suficientes? Adverse development (reservas "
        "insuficientes) es red flag.\n"
        "4. **Float growth**: float creciendo + costo bajo (combined "
        "ratio <100%) = compounding machine.\n"
        "5. **Cat exposure**: catastrophes (huracán, terremoto) "
        "pueden wipear años de underwriting profit en un trimestre. "
        "Reinsurance + diversification matter.\n"
        "6. **Book value growth**: para insurers, BV per share "
        "growth es el North Star — Buffett mide BVS de Berkshire "
        "como métrica principal."
    ),
    key_metrics=[
        ("Combined ratio (%)",
         "<95% excellent · 95-100% good · 100-105% break-even · "
         ">105% underwriting loss."),
        ("Loss ratio (%)",
         "Claims paid / Premiums. Industry average 60-70%."),
        ("Expense ratio (%)",
         "OpEx / Premiums. <30% efficient · >35% bloated."),
        ("Float ($B)",
         "Premium reserves − cash held. Crecimiento sostained = good."),
        ("Float per share growth (%)",
         "Métrica Buffett. Quiere ver crecer 10%+ anual."),
        ("Book value per share growth (%)",
         "Para insurers, BVS es el North Star. Berkshire ~10-15% "
         "CAGR históricamente."),
    ],
    bullish_vs_bearish=[
        ("Combined ratio <95% sostained",
         "Combined ratio >100% (underwriting destructive)"),
        ("Float growing + cost negativo (paid to hold)",
         "Float growing pero costo positivo (paying to hold)"),
        ("Favorable reserve development (reservas eran "
         "conservadoras)",
         "Adverse reserve development (reservas insuficientes "
         "consistentes)"),
        ("Cat exposure managed via reinsurance",
         "Heavy cat exposure no hedged"),
        ("Investment income > underwriting profit (Buffett-style)",
         "Dependent on underwriting profit (sin float economic)"),
    ],
    valuation_impact=(
        "Insurers cotizan en P/BV principalmente. Una aseguradora "
        "con combined ratio <95% sostenido + float compounding "
        "merece P/BV > 1.5x (Berkshire ~1.5x, Markel ~1.4x). "
        "Aseguradoras commodity-like cotizan P/BV ~1x. La fórmula "
        "del intrinsic incluye: book value + valor presente del "
        "spread (underwriting margin + investment yield − cost of "
        "equity). Para Berkshire específicamente, Buffett insiste "
        "que BVS subestima el valor por la goodwill no contabilizada "
        "en business operating subsidiarias."
    ),
    case_study=(
        "**Berkshire Hathaway 1967-presente**: Buffett compró "
        "National Indemnity 1967. Insurance float fue el motor del "
        "compounding de Berkshire — empezó con $39M, llegó a $164B "
        "en 2023. Combined ratio sostenido <100%, lo que significa "
        "que el float era GRATIS (cost-negative). Invirtió ese float "
        "en Coca-Cola, Apple, etc. — 4900x return desde 1967.\n\n"
        "**Contraejemplo — AIG pre-2008**: combined ratio decente "
        "pero la división AIG Financial Products escribió CDS "
        "garantizando MBS sin reservas adecuadas. Underwriting "
        "discipline cero. Cuando las MBS fallaron, AIG necesitó "
        "$182B en bailout. Lección: insurance es una caja negra si "
        "no entendés qué riesgos están underwriting."
    ),
    common_mistakes=[
        "Mirar earnings volátiles (insurance es cíclica por cats). Look at 5y avg.",
        "Ignorar reserve development. Adverse desarrollo es señal #1 de problema.",
        "Confundir combined ratio LTM con through-cycle. Un buen año no significa underwriting disciplinado.",
        "Aplicar P/E. Mejor P/BV + ROE on equity ex-investments.",
        "Pasar por alto que el investment portfolio matters tanto como underwriting. Para Berkshire, casi todo el value viene de ahí.",
    ],
    mental_model=(
        "Insurance bien manejado es 'capital ajeno gratis'. Pensá "
        "como Buffett: el float es como tener un préstamo de "
        "$164B a interés negativo. Si vos podés invertir eso a 6%+, "
        "esa diferencia es valor puro. Pero si tu underwriting es "
        "indisciplinado, el float te cuesta — y entonces todo el "
        "edge desaparece. La disciplina underwriting precede al "
        "investment skill."
    ),
    books=[_BOOK_BUFFETT_LETTERS,
           Book(title="The Davis Dynasty",
                author="John Rothchild", year=2001,
                chapter_hint="Sobre Shelby Davis y insurance",
                why="Cómo pensar insurance como business."),
           Book(title="In Praise of Doubt: How Insurance Made Buffett",
                author="Adam Mead", year=2021,
                chapter_hint="Toda la parte sobre el modelo de Berkshire",
                why="Análisis profundo del modelo insurance + float de "
                     "Berkshire.")],
    videos=[_VIDEO_BUFFETT_1996,
            Video(title="Warren Buffett Explains Insurance Float",
                  channel="Berkshire annual meeting clips",
                  minutes=10, url="",
                  why="Buffett explicando float en sus propias palabras.")],
    quotes=[
        Quote(text="Float, you say, what's that? Float is money that "
                   "doesn't belong to us, but that we get to invest. "
                   "Insurance companies receive premiums upfront and "
                   "pay claims later — and over time, the float can "
                   "be enormous.",
              author="Warren Buffett",
              source="Berkshire 1995 letter"),
        Quote(text="The most important thing in insurance is to never "
                   "let underwriting discipline lapse for the sake of "
                   "volume.",
              author="Warren Buffett",
              source="Berkshire annual letter"),
        _Q_BUFFETT_MOAT,
    ],
))
# ---------- Semis metrics ----------
_add(Lesson(
    slug="semis_metrics",
    label=_label_for("semis_metrics"),
    category=_cat_for("semis_metrics"),
    hook=_hook_for("semis_metrics"),
    definition=(
        "Semiconductores son la industria más cíclica del tech "
        "stack. Métricas específicas:\n\n"
        "  · **Inventory days**: días de inventario en hand. Subiendo = "
        "demand softening; bajando = supply tight.\n"
        "  · **Book-to-bill ratio**: orders received / orders shipped "
        "in quarter. >1 = backlog growing (bullish); <1 = "
        "destocking.\n"
        "  · **Capex intensity**: CapEx / Revenue. >25% para "
        "foundries (TSMC, Intel manufacturing); <10% fabless (Nvidia, "
        "AMD).\n"
        "  · **Design wins**: contracts a future revenue. Pipeline "
        "indicator.\n"
        "  · **Lead times**: weeks de delivery. Long lead times = "
        "tight supply (peak); short = oversupply (trough).\n"
        "  · **Wafer pricing**: precio por wafer en foundries.\n\n"
        "El ciclo típico: 18-24 meses tight → 12-18 meses correction."
    ),
    why_matters=(
        "Semis impulsan 50%+ de la innovación tech (AI, autos, IoT, "
        "consumer electronics). Pero la industria oscila violentamente "
        "— Nvidia subió 800% en 2023, AMD perdió 60% en 2022. "
        "Entender el inventory cycle, capex intensity y geopolitical "
        "risk (China-Taiwan-US) es la diferencia entre comprar en el "
        "trough vs en el peak. Y el peak típicamente sucede 6-12 "
        "meses antes de que aparezca en revenue."
    ),
    how_pros_analyze=(
        "1. **Inventory channel check**: si distribuidores reportan "
        "inventory days subiendo, demand cooling — empieza el "
        "correction.\n"
        "2. **Book-to-bill <1 para 2+ quarters = entering down-cycle**. "
        "TSMC, ASML reportan esto trimestralmente.\n"
        "3. **Lead times**: ASML EUV machines tenían lead times de "
        "18+ meses en 2022 (peak). Cuando bajan a <12 meses = supply "
        "loosening.\n"
        "4. **Geopolitical exposure**: % revenue China, % "
        "manufacturing Taiwan. Concentración alta = tail risk "
        "(export controls, conflict).\n"
        "5. **Design wins for future cycles**: chip design tarda "
        "2-3 años de revenue. Pipeline de design wins predicts 2027 "
        "revenue.\n"
        "6. **R&D intensity**: tech leaders gastan 15-25% revenue en "
        "R&D. <10% = perdiendo competitive ground."
    ),
    key_metrics=[
        ("Inventory days",
         "<60 tight · 60-100 normal · >100 destocking / overstock."),
        ("Book-to-bill ratio",
         ">1.05 expanding · 0.95-1.05 stable · <0.95 contracting."),
        ("CapEx / Revenue (%)",
         "Foundries: 25-40% · IDMs: 15-25% · fabless: <10%."),
        ("R&D / Revenue (%)",
         "Leaders 15-25% · followers 5-10%."),
        ("Gross margin (%)",
         "Foundries 50-55% · fabless leaders 65-75% (Nvidia AI 75%+)."),
        ("Lead time (weeks)",
         ">20 tight supply · 10-20 normal · <10 oversupply."),
    ],
    bullish_vs_bearish=[
        ("Book-to-bill >1.1 sostained",
         "Book-to-bill <0.9 (downcycle entering)"),
        ("Inventory days bajando + lead times extending",
         "Inventory days subiendo (destocking ahead)"),
        ("R&D intensity creciendo + design wins flowing",
         "R&D / Revenue cayendo (perdiendo competitive ground)"),
        ("Geopolitical diversification (multi-fab strategy)",
         "Single-source Taiwan / single-customer concentration"),
        ("Capex disciplinado en down-cycle",
         "Capex expansion at peak (creando next oversupply)"),
    ],
    valuation_impact=(
        "Semis cotizan muy distinto según donde estás en el ciclo. "
        "Peak earnings + peak multiples = double-whammy en downcycle. "
        "Usar through-cycle P/E + normalizar margins es esencial. "
        "Empresas con moats estructurales (ASML, TSMC, Nvidia AI) "
        "merecen premium multiples; commoditized (memory, "
        "value-tier logic) cotizan deeper-cycle."
    ),
    case_study=(
        "**Nvidia 2022-2024**: stock cayó 65% en 2022 cuando gaming "
        "+ crypto demand colapsó. Inventory days saltaron de 80 a "
        "200. Pero a finales de 2022 empezó AI demand para H100 "
        "data center chips. 2023 revenue +126%, gross margin 75%+. "
        "Stock 9x desde Oct 2022 lows. Lección: en semis, el "
        "downcycle puede ser DENTRO de un super-cycle más grande "
        "(AI compute).\n\n"
        "**Caso clásico — Intel 2014-2024**: lideró durante 30 años. "
        "Pero foundry execution failed (no podían manufacturar 7nm "
        "competitivamente vs TSMC). ROIC pasó de 22% a 4%. Capex "
        "subió a $25B/año tratando de catchup. Multiple comprimió "
        "de P/E 14 a P/E 25 sobre EPS que cayó 60%. Cuando un semi "
        "leader pierde manufacturing edge, el multiple se comprime "
        "y los earnings caen — el doble whammy del 'commoditization'."
    ),
    common_mistakes=[
        "Asumir que peak earnings = good entry. Semis pagan P/E LOW en peak y HIGH en trough — el opuesto del retail value investing.",
        "Ignorar el inventory cycle. Es el leading indicator más fuerte.",
        "Aplicar DCF con growth lineal en una industria con cycles 18-24 meses.",
        "Subestimar el geopolitical risk. TSMC Taiwan concentration es existential.",
        "Confundir AI-driven semis (Nvidia, TSMC EUV) con general semis. Son industrias distintas dentro de la misma label.",
    ],
    mental_model=(
        "Semis es la industria donde el sentiment lidera el "
        "fundamental por 6-12 meses. Cuando todos hablan de "
        "'shortage forever', el supply ya está en camino. Cuando "
        "'glut forever', la demand ya empieza a recovery. Pensá "
        "como Marks: cycles inevitables, no predecibles en timing. "
        "Pero los inventory data + book-to-bill te dan ventanas "
        "anchas."
    ),
    books=[
        Book(title="Chip War", author="Chris Miller", year=2022,
             chapter_hint="Caps. sobre TSMC + ASML",
             why="Historia + estructura de la industria semis."),
        Book(title="The Innovator's Dilemma",
             author="Clayton Christensen", year=1997,
             chapter_hint="Aplicado a semis: cómo Intel perdió mobile",
             why="Framework de disruption — muy aplicable a semis."),
        _BOOK_DAMODARAN_VALUATION,
    ],
    videos=[
        Video(title="The Semiconductor Cycle Explained",
              channel="Asianometry", minutes=20, url="",
              why="Channel especializado en semis con visuals "
                   "increíbles."),
        Video(title="Chris Miller · Chip War",
              channel="Talks at Google", minutes=60, url="",
              why="El autor explica la geopolítica de chips."),
    ],
    quotes=[
        Quote(text="In the semiconductor industry, the only constant "
                   "is cyclicality. The companies that survive are "
                   "the ones that prepare for the downcycle when "
                   "everyone is partying at the peak.",
              author="Morris Chang",
              source="Founder of TSMC, multiple interviews"),
        _Q_MARKS_RISK,
        Quote(text="If you wait until you see the recovery, you've "
                   "already missed half of it in semis.",
              author="Anonymous semi PM",
              source="Industry folklore"),
    ],
))
# ---------- Consumer brands ----------
_add(Lesson(
    slug="consumer_brands",
    label=_label_for("consumer_brands"),
    category=_cat_for("consumer_brands"),
    hook=_hook_for("consumer_brands"),
    definition=(
        "Una marca consumer es un activo intangible que permite a la "
        "empresa cobrar un PREMIUM sobre el producto comoditizado "
        "equivalente, mantener clientes fieles (lower churn), y "
        "expandir a categorías adyacentes con bajo CAC.\n\n"
        "Componentes del 'brand equity':\n"
        "  · **Awareness**: % población que conoce la marca.\n"
        "  · **Preference**: cuando hay opciones similares, ¿cuántos "
        "eligen esta?\n"
        "  · **Premium pricing power**: puede cobrar más?\n"
        "  · **Distribution moat**: presencia ubicua (Coca-Cola en "
        "200 países).\n\n"
        "Marcas grandes (Coca-Cola, Apple, Nike, LVMH) valen tanto "
        "o más que los activos físicos de la empresa."
    ),
    why_matters=(
        "Las marcas son los moats más duraderos en consumer. "
        "Coca-Cola lleva 130+ años cotizando ROIC alto. See's Candy, "
        "Disney, McDonald's, similares. Buffett dijo que 'una marca "
        "fuerte es como un castillo con foso ancho — la competencia "
        "tiene que cruzar nado'. En valuación, una marca consolidada "
        "justifica multiples premium sostenibles."
    ),
    how_pros_analyze=(
        "1. **Pricing power test**: ¿puede subir precios above-"
        "inflation sin perder volume? See's lo hizo 50 años seguidos.\n"
        "2. **Market share trend**: marcas fuertes mantienen o "
        "ganan share. Si pierden, el brand equity erosiona.\n"
        "3. **Gross margin durability**: marcas premium >50% gross. "
        "Genérico ~25%. La diferencia ES el brand premium.\n"
        "4. **Advertising intensity**: ad spend / revenue. Marcas "
        "consolidadas pueden bajarlo (no necesitan reforzar tanto). "
        "Marcas declinantes lo suben para defender share.\n"
        "5. **Geographic diversification**: una marca global vs "
        "regional tiene optionality distinta.\n"
        "6. **Generational test**: ¿la próxima generación la "
        "consume? Boomers vs Gen Z. Coca-Cola en problemas con Gen Z; "
        "Apple no."
    ),
    key_metrics=[
        ("Gross margin (%)",
         ">55% strong brand · 35-55% normal · <35% commoditized."),
        ("Operating margin (%)",
         "Premium brands 20-30%. Mass market 8-15%."),
        ("Ad spend / Revenue (%)",
         "Established brands 5-10% · declining brands 12%+ "
         "(defensive)."),
        ("Brand equity rankings",
         "Interbrand, BrandZ, Forbes — valuación tercerista. Top "
         "100 = compounders típicos."),
        ("Same-store sales (consumer retail)",
         "Healthy brand: SSS positivo 3+ years. Declining: SSS "
         "negativo sostained."),
        ("Volume vs price split",
         "Premium brands: ambos positivos. Commoditized: volume "
         "neg, price flat."),
    ],
    bullish_vs_bearish=[
        ("Gross margin >55% sostained",
         "Gross margin erosionándose (commoditization)"),
        ("Pricing positivo + volume positivo",
         "Solo crece por descuentos / promociones"),
        ("Market share estable o creciendo",
         "Market share erosionándose ante private label"),
        ("Generational reach (Boomers + Gen Z)",
         "Sin tracción en Gen Z (brand aging)"),
        ("Ad spend %  declining (no necesita reforzar)",
         "Ad spend % increasing (defensive)"),
    ],
    valuation_impact=(
        "Consumer brands cotizan a multiples premium: Coca-Cola "
        "P/E 24, P&G 25, LVMH 25 vs S&P promedio 20. El premium "
        "refleja predictability + pricing power. En recesiones, "
        "consumer staples brands son defensivos — gente sigue "
        "comprando Coca-Cola aunque pierda el trabajo. Eso justifica "
        "premium en discount rate (beta más bajo). En DCF, asumir "
        "competitive advantage period largo (20+ años) está "
        "justificado para marcas top-tier."
    ),
    case_study=(
        "**LVMH 2010-2024**: revenue 4x, op margin 26%+. La "
        "estrategia: comprar marcas establecidas (Louis Vuitton, "
        "Dior, Tiffany), aplicar disciplina operativa, mantener "
        "pricing power. Cada brand premium se compounde. Stock 8x "
        "en 14 años. Caso textbook de cómo se monetiza brand "
        "equity sin diluir el premium.\n\n"
        "**Contraejemplo — Tupperware Brands**: marca legendaria "
        "consumer 1960s-1990s. Pero el modelo (direct sales, "
        "parties) no transicionó a digital + Gen X / Millennials. "
        "Revenue stagnated 20 años, eventualmente declared "
        "bankruptcy 2024. Lección: brand equity sin relevancia "
        "generacional se erosiona — invisible hasta que es muy "
        "tarde."
    ),
    common_mistakes=[
        "Asumir que brand awareness = brand equity. Awareness alta de marca declinante (Sears, Kodak) no salva.",
        "Pagar 'brand multiples' por empresas con marca débil real (private label exposure).",
        "Ignorar el demographic shift. Brands que captura Boomers pueden estar muriendo silenciosamente con Gen Z.",
        "Confundir DTC growth con brand strength. Many DTCs crecen vía paid acquisition, no brand pull.",
        "Pasar por alto que algunas categorías son inherentemente commoditizadas (gasoline, sugar, basic apparel) — ahí brand investing no funciona.",
    ],
    mental_model=(
        "Test final de marca (Buffett): 'si te diera $100B y te "
        "dijera que destruyas Coca-Cola, ¿podrías? La respuesta es "
        "no'. La marca está en la cabeza del consumidor — "
        "tanto que no la pueden replicar con capital. Eso es el "
        "moat más duradero que existe. Pero requiere check periódico "
        "de relevancia generacional."
    ),
    books=[_BOOK_BUFFETT_LETTERS, _BOOK_FISHER,
           Book(title="Building Strong Brands",
                author="David Aaker", year=1996,
                chapter_hint="Caps. 1-6 — brand equity model",
                why="Texto académico fundacional de brand strategy."),
           Book(title="Predictably Irrational",
                author="Dan Ariely", year=2008,
                chapter_hint="Cap. 6 — el efecto del placebo en pricing",
                why="Por qué las marcas crean valor real psicológicamente.")],
    videos=[_VIDEO_BUFFETT_1996,
            Video(title="The Power of Branding — Coca-Cola Case",
                  channel="CFA Institute", minutes=45, url="",
                  why="Análisis profundo de brand equity en KO.")],
    quotes=[
        _Q_BUFFETT_MOAT,
        Quote(text="In the long run, a brand is the most valuable "
                   "asset a company can own. It outlasts factories, "
                   "patents, and people.",
              author="Howard Schultz",
              source="Pour Your Heart Into It (Starbucks)"),
        Quote(text="If you don't have a brand, you have a "
                   "commodity. And commodities compete on price.",
              author="Philip Kotler",
              source="Marketing Management (10th ed.)"),
    ],
))
# ---------- Network effects ----------
_add(Lesson(
    slug="network_effects",
    label=_label_for("network_effects"),
    category=_cat_for("network_effects"),
    hook=_hook_for("network_effects"),
    definition=(
        "Network effect ocurre cuando el valor del producto/servicio "
        "AUMENTA con cada usuario adicional. Más usuarios = más "
        "valor para todos = más razón para usar (loop reinforce).\n\n"
        "Tipos:\n"
        "  · **Direct network effect**: cada usuario nuevo agrega "
        "valor a los existentes (Telegram, WhatsApp).\n"
        "  · **Indirect / two-sided**: marketplaces donde dos lados "
        "se atraen (Uber drivers ↔ riders, Visa merchants ↔ "
        "cardholders).\n"
        "  · **Data network effect**: más usuarios = más data = "
        "mejor producto (Google, Tesla autopilot).\n"
        "  · **Social network effect**: el valor proviene de las "
        "conexiones sociales (Meta, LinkedIn).\n\n"
        "El network effect produce 'winner-takes-most' markets — "
        "típicamente 1-2 jugadores capturan 70%+ del valor."
    ),
    why_matters=(
        "Los moats más anchos de la era moderna son network effects. "
        "Microsoft (Windows + Office), Visa, Mastercard, Meta, "
        "Google, Amazon marketplace — todos compounded décadas "
        "porque cada usuario nuevo refuerza el moat. En valuación, "
        "una empresa con network effect demostrado merece "
        "competitive advantage period MUY largo (20+ años) y ROIC "
        "steady-state alto. Ignorar network effects = subestimar "
        "intrinsic value 30-50%."
    ),
    how_pros_analyze=(
        "1. **Identify the loop**: ¿qué exactamente refuerza el loop? "
        "Para Visa: más merchants accept → más razón para tener "
        "tarjeta → más cardholders → más razón para merchants "
        "accept.\n"
        "2. **Critical mass threshold**: cada network tiene un punto "
        "de inflexión donde el effect se vuelve self-sustaining. "
        "Facebook lo cruzó ~2007; Uber ~2013.\n"
        "3. **Local vs global**: Uber es network effect LOCAL (la "
        "red en SF no ayuda al user de Buenos Aires). Visa es "
        "GLOBAL. Local networks tienen menos defensibilidad.\n"
        "4. **Multi-homing**: ¿usan los users solo este o varios? "
        "Drivers Uber + Lyft simultáneamente = network effect "
        "diluido. WhatsApp single-homing (casi nadie tiene 2 chat "
        "apps) = network effect fuerte.\n"
        "5. **Reverse network effects**: cuando user growth degrada "
        "experience (Twitter pre-Musk spam, MySpace post-2008). "
        "Network effects pueden invertir."
    ),
    key_metrics=[
        ("Network density",
         "% del market potencial covered. Saturation = mature; "
         "low penetration = runway."),
        ("Engagement per user trend",
         "Si más users → más engagement por user, network effect "
         "intact. Si decreasing, deteriorating."),
        ("Multi-homing ratio",
         "% users que usan también competitors. <20% = strong; "
         ">50% = diluted."),
        ("CAC trend with scale",
         "Bajando con scale = organic + network effects fuerte. "
         "Subiendo = saturando + paying for growth."),
        ("Take rate (marketplaces)",
         "% commission. Visa 0.05% pero ubicuo; eBay 13%. "
         "Sustainability depende del moat."),
        ("Retention curve",
         "Sticky users (engagement nivela en plateau alto) = "
         "network effect strong."),
    ],
    bullish_vs_bearish=[
        ("Critical mass cruzado + organic growth",
         "Pre-critical mass / paying for every user"),
        ("Single-homing (los users solo usan este)",
         "Multi-homing rampant (el switching es cero)"),
        ("Engagement per user CRECE con scale",
         "Engagement per user DECRECE con scale (signo de saturation)"),
        ("Global network (defensible globally)",
         "Local network (vulnerable a competition local)"),
        ("Data feedback loop activo (más data → mejor product)",
         "Sin data flywheel (solo marketplace transactional)"),
    ],
    valuation_impact=(
        "Una empresa con verdadero network effect demostrado puede "
        "justificar EV/Revenue 10-20x, P/E 30-50x. Visa/Mastercard "
        "son ejemplos: P/E 30+ sustained porque el moat se "
        "ensancha cada año. Pero hay que verificar que el network "
        "effect es REAL y no narrativa. Yelp, Groupon, Pinterest "
        "fueron pitched como network effects que turned out menos "
        "defensibles. En DCF, asumir CAP de 20+ años solo después "
        "de validar el network effect empíricamente."
    ),
    case_study=(
        "**Visa 1958-presente**: el ejemplo canónico de network "
        "effect en payment. Empezó como 'BankAmericard' en una sola "
        "ciudad. Expandió bancos uno por uno hasta cruzar critical "
        "mass ~1975 (suficientes merchants + cardholders en US). "
        "Una vez cruzado, el lock-in se volvió permanente. ROIC "
        "60-85% sostenido durante 50+ años. Compounded ~16% CAGR "
        "desde IPO 2008.\n\n"
        "**Contraejemplo — MySpace 2003-2008**: tenía el network "
        "effect social más grande del mundo en 2007. Facebook tomó "
        "share en <3 años. Por qué: switching cost bajo, no "
        "investment del user en la plataforma (a diferencia de "
        "Facebook con fotos, friend tree, history). Lección: network "
        "effects sociales sin switching costs son frágiles."
    ),
    common_mistakes=[
        "Confundir 'tener muchos users' con network effect. Spotify tiene millones de users pero NO tiene network effect (más users no agrega valor a otros users).",
        "Aplicar 'network effect' a cualquier marketplace. Solo aplica si hay verdadero feedback loop.",
        "Asumir que network effects son permanentes. Tech paradigm shifts (mobile, web3) pueden disolverlos.",
        "Ignorar el reverse network effect. Demasiado growth puede degradar la experiencia (spam, low quality content).",
        "Pagar multiples de network effect sin validar empíricamente (engagement growing, organic CAC declining).",
    ],
    mental_model=(
        "Andrew Chen (a16z): 'el cold start problem es el más "
        "difícil — el chicken-and-egg de cualquier network'. Una vez "
        "resuelto, el network se vuelve casi imposible de "
        "desplazar. Pensá en cuántos competidores intentaron "
        "desplazar a Visa, Microsoft Office, Facebook social graph — "
        "casi todos fallaron. Esos moats son las opportunities "
        "compounders más valiosas del siglo XXI."
    ),
    books=[
        Book(title="The Cold Start Problem",
             author="Andrew Chen", year=2021,
             chapter_hint="Toda la parte I",
             why="Cómo se construyen y se rompen los network effects."),
        Book(title="Information Rules",
             author="Carl Shapiro & Hal Varian", year=1998,
             chapter_hint="Caps. 7-9 — network effects económicos",
             why="Texto académico fundacional, escrito por el chief "
                  "economist de Google."),
        _BOOK_BUFFETT_LETTERS,
    ],
    videos=[
        Video(title="James Currier · NFX on Network Effects",
              channel="NFX (VC)", minutes=30, url="",
              why="VC especializado en network effects explica los "
                   "13 tipos."),
        _VIDEO_BUFFETT_1996,
    ],
    quotes=[
        Quote(text="The most valuable companies of the 21st century "
                   "are those built on network effects. They compound "
                   "value faster than any other business model.",
              author="James Currier",
              source="NFX research"),
        Quote(text="Networks tip towards winners-take-most outcomes.",
              author="W. Brian Arthur",
              source="Increasing Returns and Path Dependence (1994)"),
        _Q_BUFFETT_MOAT,
    ],
))

# Valuación (stubs)
# ---------- Multiples overview ----------
_add(Lesson(
    slug="multiples_overview",
    label=_label_for("multiples_overview"),
    category=_cat_for("multiples_overview"),
    hook=_hook_for("multiples_overview"),
    definition=(
        "Los múltiplos son ratios de valuación que comparan el precio "
        "(o EV) con una métrica fundamental. Cada uno te dice algo "
        "distinto:\n\n"
        "**Equity multiples** (sobre Market Cap):\n"
        "  · **P/E** = Price / EPS — earnings-based\n"
        "  · **P/B** = Price / Book Value — asset-based\n"
        "  · **P/S** = Price / Sales — revenue-based\n"
        "  · **P/FCF** = Price / Free Cash Flow — cash-based\n\n"
        "**Enterprise multiples** (sobre EV, neutral al leverage):\n"
        "  · **EV/EBITDA** — operating cash earnings\n"
        "  · **EV/EBIT** — operating earnings (con D&A real)\n"
        "  · **EV/Revenue** — útil para growth companies sin "
        "earnings positivos\n"
        "  · **EV/FCFF** — más honesto que EV/EBITDA\n\n"
        "**Sector-specific**: P/TBV bancos, P/AUM asset managers, "
        "EV/EBITDAR airlines, P/FFO REITs."
    ),
    why_matters=(
        "Los multiples son la 'lingua franca' del valuation porque "
        "permiten comparación rápida entre empresas. Pero también "
        "son la fuente #1 de errores — usar el wrong multiple para "
        "el wrong tipo de empresa. P/E en banks, EV/EBITDA en "
        "REITs, P/B en software — todos errores comunes. Damodaran "
        "insiste: el multiple correcto depende del modelo de negocio "
        "y del estado del ciclo."
    ),
    how_pros_analyze=(
        "1. **Multiple selection driven by business model**: "
        "    · Asset-heavy → P/B, EV/EBITDA\n"
        "    · Earnings-stable → P/E\n"
        "    · High-growth no profit → P/S, EV/Revenue\n"
        "    · Cash-heavy → P/FCF, EV/FCFF\n"
        "    · Banks → P/TBV + ROTE\n"
        "    · REITs → P/FFO\n"
        "2. **Compare vs peers, no abstract**: P/E 25 es alto vs S&P "
        "(20) pero bajo vs software peers (30+).\n"
        "3. **Compare vs own history**: Z-score. ¿Estás cotizando 1 "
        "std arriba de tu propio 10y mean?\n"
        "4. **Cross-check múltiples**: si P/E dice cheap pero EV/EBITDA "
        "dice expensive, hay leverage. Si P/FCF dice cheap pero P/E "
        "dice expensive, accruals están inflando earnings.\n"
        "5. **Forward vs trailing**: forward para growth, trailing "
        "para mature stable.\n"
        "6. **Adjust for cycle**: en cyclicals usar through-cycle, "
        "no LTM."
    ),
    key_metrics=[
        ("P/E (trailing)",
         "Earnings predictable. NO bancos ni cyclicals."),
        ("P/B",
         "Asset-heavy (banks, insurers, REITs). Tangible Book "
         "preferible (ROTE)."),
        ("EV/EBITDA",
         "Comparison across capital structures. NO bancos."),
        ("EV/FCFF",
         "Más honest que EV/EBITDA (incluye CapEx)."),
        ("P/S, EV/Revenue",
         "Growth pre-profitability. Usar con NRR / unit economics."),
        ("PEG",
         "P/E ÷ growth rate. <1 cheap given growth; >2 expensive."),
    ],
    bullish_vs_bearish=[
        ("Multiple < peer median + sector avg",
         "Multiple > peer median + sector premium"),
        ("Multiple normalizado por through-cycle earnings",
         "Multiple sobre LTM peak earnings (value trap)"),
        ("Cross-check múltiples consistente",
         "Múltiples diverging (EV/EBITDA cheap, P/FCF expensive)"),
        ("Multiple < own historical Z (mean reversion play)",
         "Multiple > own historical Z (priced for perfection)"),
    ],
    valuation_impact=(
        "Los multiples son tools de TRIAGE, no de valuación final. "
        "Te dicen rápido si algo es worth deep-diving. Pero el "
        "intrinsic value real viene del DCF + fundamental análisis. "
        "Usar solo multiples = comprar 'lo barato' que típicamente "
        "es barato por razones (value traps). Combinar multiples + "
        "DCF + cualitativo = research completo."
    ),
    case_study=(
        "**Buffett comprando Apple 2016**: Apple cotizaba P/E ~10-12 "
        "(barato vs S&P P/E 18). Net cash $100B+ — ex-cash el P/E "
        "era ~7. Múltiples gritaban 'cheap'. Lo que el mercado "
        "missed: el ecosystem moat (switching cost iOS), services "
        "revenue growth, FCF generation power. Buffett pagó ~$36/share. "
        "10x return en 8 años. Multiple expansion + earnings growth.\n\n"
        "**Contraejemplo — Sears 2005-2018**: cotizaba P/B 0.4 (40% "
        "de book). 'Deep value' aparente. Lo que escondía: book era "
        "real estate sobrevalorado y inventory obsoleto. P/B "
        "engañaba. Quiebra 2018. Lección: cada multiple tiene su "
        "trampa específica."
    ),
    common_mistakes=[
        "Aplicar P/E a banks. Usar P/TBV.",
        "Aplicar EV/EBITDA a REITs. Usar P/FFO.",
        "Comparar multiples entre industrias sin ajustar.",
        "Confiar en multiple LTM en cyclicals.",
        "Ignorar que multiples pueden persist por años antes de mean-reverting.",
    ],
    mental_model=(
        "Multiples son atajos — útiles pero peligrosos. Damodaran: "
        "'a multiple is implicit DCF assumptions wrapped in a single "
        "number'. Cuando usás P/E 20, estás implícitamente asumiendo "
        "ciertas cosas sobre growth, ROIC, WACC. Antes de comprar/"
        "vender por un multiple, preguntate: ¿qué assumptions están "
        "embedded? ¿son razonables?"
    ),
    books=[_BOOK_DAMODARAN_VALUATION, _BOOK_MCKINSEY_VALUATION,
           _BOOK_CFA],
    videos=[_VIDEO_DAMODARAN_VALUATION,
            Video(title="The 5 Most Important Multiples",
                  channel="Aswath Damodaran", minutes=30, url="",
                  why="Damodaran framework para elegir multiple "
                       "correcto.")],
    quotes=[
        _Q_DAMODARAN_STORY,
        Quote(text="A multiple is a shortcut to a DCF — but every "
                   "shortcut has a price.",
              author="Aswath Damodaran",
              source="Investment Valuation"),
        _Q_BUFFETT_PRICE_VALUE,
    ],
))
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
# ---------- PEG ----------
_add(Lesson(
    slug="peg",
    label=_label_for("peg"),
    category=_cat_for("peg"),
    hook=_hook_for("peg"),
    definition=(
        "PEG (Price/Earnings to Growth) = P/E ÷ EPS growth rate. "
        "Es el intento de Peter Lynch de normalizar P/E por growth "
        "— una empresa con P/E 30 creciendo 30% (PEG = 1.0) sería "
        "comparable a una con P/E 15 creciendo 15% (también PEG 1.0). "
        "Lynch: '**a fair price for a stock is one where P/E equals "
        "growth rate** (PEG = 1)'.\n\n"
        "Versiones:\n"
        "  · **PEG simple**: P/E LTM ÷ next year EPS growth\n"
        "  · **PEG forward**: forward P/E ÷ 3-5y projected growth\n"
        "  · **PEG yield-adjusted**: (P/E) ÷ (growth + dividend yield)\n\n"
        "Regla de Lynch: PEG <1 cheap · 1-2 fair · >2 expensive."
    ),
    why_matters=(
        "PEG resuelve parcialmente la trampa del P/E aislado — "
        "growth companies con P/E alto pueden ser cheap si el "
        "growth justifica. Pero PEG mal usado es peligroso: P/E 50 "
        "con growth 50% (PEG 1) NO necesariamente es 'fair' — el "
        "growth alto rara vez es sostenible 10 años. Lynch enfocaba "
        "growth companies de mediano tamaño con visibility — no "
        "high-flying tech."
    ),
    how_pros_analyze=(
        "1. **Usar growth RATE realista**: no el peak temporal. "
        "Empresas con growth 50% en un año típicamente no lo sostienen. "
        "Usar 3-5y forward growth, no 1y.\n"
        "2. **Verificar growth quality**: ¿es orgánico o por M&A? "
        "Sostenible o cyclical?\n"
        "3. **PEG no aplica en cyclicals**: en peak earnings el growth "
        "se desploma, PEG explota.\n"
        "4. **PEG yield-adjusted** para dividend payers: añadir "
        "dividend yield al denominador.\n"
        "5. **Compare PEG vs sector**: PEG 1.0 puede ser cheap en "
        "high-growth tech (peers 2-3) y expensive en utilities "
        "(peers <1).\n"
        "6. **Watch out**: si P/E altas + growth high projected, "
        "PEG bajos. Pero proyecciones de growth tienen MUCHO error — "
        "sensitivity matters."
    ),
    key_metrics=[
        ("PEG (trailing)",
         "P/E LTM ÷ NTM EPS growth. <1 cheap por Lynch."),
        ("PEG (forward)",
         "Forward P/E ÷ 3-5y projected growth. Más útil para growth."),
        ("PEG yield-adjusted",
         "P/E ÷ (growth + div yield). Aplica a dividend stocks."),
        ("Growth durability",
         "¿Cuántos años puede sostener este growth? Probability check."),
        ("Implied PEG of market",
         "S&P PEG ~2 históricamente. <1.5 cheap market-wide."),
    ],
    bullish_vs_bearish=[
        ("PEG <1 con growth sostenible (visibility 3+ años)",
         "PEG <1 pero growth temporal / unsustainable"),
        ("Growth orgánico de calidad",
         "Growth via M&A o non-recurring items"),
        ("Forward P/E + realistic growth assumptions",
         "Trailing P/E + peak growth = false signal"),
        ("Yield-adjusted PEG razonable",
         "PEG bajo solo por dividend yield alto (banderas value trap)"),
    ],
    valuation_impact=(
        "PEG es útil como screening tool — identificar candidates "
        "que merecen deep-dive. PERO no es valuation methodology "
        "completa. Lynch insistía: usar PEG <1 como FILTRO, después "
        "investigar a fondo. Mecánicamente PEG asume que el growth "
        "actual continúa indefinidamente — eso casi nunca es cierto. "
        "Empresas growth tienden a mean-revert a 5-10% growth eventually."
    ),
    case_study=(
        "**Amazon 2003**: P/E 50, growth proyectado 30% → PEG 1.7 "
        "(no cheap). Pero la mayoría del growth venía de "
        "reinvestment masivo (margens low por inversión). PEG "
        "missed it — Lynch's framework no captura las empresas que "
        "deliberadamente sacrifican margen por growth. Amazon "
        "100x desde ahí.\n\n"
        "**Contraejemplo — Las 'Nifty Fifty' 1972**: empresas growth "
        "blue chip (Polaroid, Xerox, Avon) con P/E 50-90 "
        "justificados por 'growth durable'. PEG ~1.5-2 que parecía "
        "razonable. 1973-74 mercado: cayeron 60-80% cuando el growth "
        "no sostuvo. Lección: PEG bajo solo justifica si el growth "
        "es realmente durable."
    ),
    common_mistakes=[
        "Usar peak / single-year growth en el denominator. Casi siempre overestima.",
        "Aplicar PEG en cyclicals (industriales, semis, energy) — distorsiona en peak.",
        "Confiar en sell-side growth projections sin verificar el track record histórico.",
        "Olvidar que PEG implícitamente asume growth perpetuo — irreal.",
        "Aplicar PEG en deep-value plays (banks, REITs) donde growth no es el driver.",
    ],
    mental_model=(
        "Lynch: 'el inversor de éxito busca empresas que el mercado "
        "subestima por aburridas pero que tienen growth real "
        "underneath'. PEG es la versión cuantitativa de esa idea — "
        "P/E que parece alto pero growth lo justifica. Pero como "
        "todo screen, es un punto de entrada para research, no la "
        "conclusión final. PEG <1 con quality y duración → "
        "winner. PEG <1 con quality dudosa → trampa."
    ),
    books=[_BOOK_LYNCH, _BOOK_DAMODARAN_VALUATION,
           Book(title="Beating the Street", author="Peter Lynch",
                year=1993, chapter_hint="Cap. sobre PEG en práctica",
                why="Lynch's sequel con ejemplos de PEG aplicado.")],
    videos=[
        Video(title="Peter Lynch's Growth Investing",
              channel="William Green / The Acquirers Podcast",
              minutes=60, url="",
              why="Discussion profunda del framework de Lynch."),
    ],
    quotes=[
        _Q_LYNCH_INVERT,
        Quote(text="The P/E ratio of any company that's fairly priced "
                   "will equal its growth rate.",
              author="Peter Lynch",
              source="One Up On Wall Street, Cap. 13"),
        Quote(text="If the P/E of Coca-Cola is 15, you'd expect the "
                   "company to grow at about 15% a year. But if the "
                   "P/E ratio is less than the growth rate, you may "
                   "have found yourself a bargain.",
              author="Peter Lynch",
              source="One Up On Wall Street"),
    ],
))
# ---------- Sum-of-the-parts (SOTP) ----------
_add(Lesson(
    slug="sotp",
    label=_label_for("sotp"),
    category=_cat_for("sotp"),
    hook=_hook_for("sotp"),
    definition=(
        "Sum-of-the-parts (SOTP) es la metodología que valora cada "
        "segmento / línea de negocio separadamente y los suma para "
        "obtener el valor del consolidado. Aplica especialmente "
        "para:\n\n"
        "  · **Conglomerados**: Berkshire, GE pre-spin, "
        "Liberty Media, Naspers.\n"
        "  · **Holding companies**: empresas que principalmente "
        "tienen stakes en otras (Naspers/Tencent, Softbank).\n"
        "  · **Empresas con divisiones muy distintas**: Disney (parks, "
        "streaming, ESPN, studios), Microsoft (Office, Azure, Xbox), "
        "Amazon (retail, AWS, ads).\n\n"
        "Cada segmento se valora con la metodología apropiada (DCF, "
        "multiples) y se aplica un descuento por holding company "
        "típicamente 10-25%."
    ),
    why_matters=(
        "Aplicar un multiple consolidado a una conglomerada con "
        "divisiones que merecen multiples muy distintos = "
        "subestimación. Ejemplo: Naspers cotizaba P/E 25 cuando solo "
        "su stake en Tencent (que cotiza P/E 30+) valía MÁS que el "
        "market cap entero. SOTP es el método para descubrir "
        "'hidden value' en holding discounts."
    ),
    how_pros_analyze=(
        "1. **Segment-level financials**: la empresa típicamente "
        "reporta revenue y operating profit por segmento. Algunas "
        "reportan total assets per segment.\n"
        "2. **Apply right multiple per segment**: tech segment → "
        "tech multiples (15-25x EBITDA), industrial segment → "
        "industrial multiples (8-12x), real estate → P/FFO.\n"
        "3. **Net debt + corporate costs**: restar net debt total + "
        "corporate overhead (allocate or central).\n"
        "4. **Holding discount**: típicamente 10-25% en conglomerates "
        "(reflects: opacity, tax inefficiency, no synergies "
        "demostradas, control premium ausente).\n"
        "5. **Comparison vs share price**: si SOTP > price + 30%, "
        "potential break-up value. Activist investors atacan estos.\n"
        "6. **Watch catalysts**: spin-offs, divestitures, asset sales "
        "pueden unlock SOTP value."
    ),
    key_metrics=[
        ("Sum of segment values (USD)",
         "Sumá cada segment valor estimado."),
        ("Conglomerate / holding discount (%)",
         "10-15% conglomerate normal · 20-30% complejo / opaco · "
         "<10% high-quality."),
        ("SOTP vs Market Cap gap",
         ">30% gap = hidden value potential. <10% = market priceó "
         "correctly."),
        ("Largest segment % of SOTP",
         "Concentration. >70% = SOTP es básicamente el segment "
         "dominante."),
        ("Catalysts visible (spin / sale / restructure)",
         "Spin-off announced = SOTP discount typically closes."),
    ],
    bullish_vs_bearish=[
        ("SOTP > Market Cap + 30% with visible catalysts",
         "SOTP > Market Cap pero no catalysts (sustained discount)"),
        ("Each segment standalone valuable",
         "One segment subsidizing weak others (forced cross-subsidy)"),
        ("Conglomerate discount narrowing",
         "Discount widening (mercado pricing complexity más)"),
        ("Management open to spin / divest",
         "Empire-building CEO (Bayer + Monsanto)"),
        ("Activist involvement / breakup pressure",
         "No external pressure, status quo permanent"),
    ],
    valuation_impact=(
        "SOTP analysis típicamente revela valor 15-40% encima del "
        "stock price en conglomerates. PERO el discount puede "
        "persist años — hasta que aparece catalyst (activist, "
        "spin-off, management change). Spin-offs históricamente "
        "outperforman el S&P por ~10pp en los 3 años post-spin "
        "(estudio de Joel Greenblatt). SOTP analysis es la base "
        "para identificar candidates."
    ),
    case_study=(
        "**Naspers / Prosus 2018-2024**: Naspers tenía un stake del "
        "31% en Tencent que valía ~$130B+. El market cap de Naspers "
        "era ~$75-90B. SOTP discount >40% — uno de los mayores en "
        "history. Spun-off Prosus 2019 para separar el stake + "
        "vendió tranches gradualmente. El discount se redujo de 40% "
        "a 20% sobre 5 años.\n\n"
        "**Caso clásico — General Electric breakup 2021**: GE "
        "anunció split en 3 empresas (Healthcare, Aviation, "
        "Energy). Pre-anuncio cotizaba a P/E 12 (descuento "
        "conglomerate). Post-anuncio rerated +50% en 6 meses. SOTP "
        "value se materializó vía corporate action."
    ),
    common_mistakes=[
        "Aplicar consolidated multiples a empresas con divisiones diversas (Disney parks + streaming en mismo P/E).",
        "Ignorar el holding discount. Sí existe estructuralmente y persiste.",
        "Aplicar SOTP a empresas sin spin / divest catalyst — el descuento puede sostenerse décadas.",
        "Olvidar costos corporativos (HQ, no-allocated G&A) en el cálculo.",
        "Asumir que cada segment valdría su SOTP independientemente — synergies negativas pueden existir.",
    ],
    mental_model=(
        "Buffett: 'a price is only what the market pays — value is "
        "what the underlying assets generate'. SOTP es la "
        "encarnación de esa idea: ignorar el ticker price, valorar "
        "las partes. Pero recordá: una empresa puede tener SOTP >> "
        "market cap por décadas. El value se monetiza con catalyst, "
        "no con time. Sin catalyst esperás eternamente."
    ),
    books=[_BOOK_DAMODARAN_VALUATION, _BOOK_MCKINSEY_VALUATION,
           Book(title="You Can Be a Stock Market Genius",
                author="Joel Greenblatt", year=1997,
                chapter_hint="Caps. sobre spin-offs",
                why="El texto sobre special situations — incluye SOTP."),
           _BOOK_BUFFETT_LETTERS],
    videos=[_VIDEO_DAMODARAN_VALUATION,
            Video(title="Joel Greenblatt on Spin-Offs",
                  channel="Special Situations", minutes=30, url="",
                  why="El autor de Stock Market Genius explica "
                       "spin-off mechanics.")],
    quotes=[
        _Q_DAMODARAN_STORY,
        Quote(text="Spin-offs are one of the few corporate actions "
                   "where management is incentivized to set the right "
                   "starting price — they own shares in both halves.",
              author="Joel Greenblatt",
              source="You Can Be a Stock Market Genius"),
        _Q_BUFFETT_PRICE_VALUE,
    ],
))
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
# ---------- Sensitivity analysis ----------
_add(Lesson(
    slug="sensitivity_analysis",
    label=_label_for("sensitivity_analysis"),
    category=_cat_for("sensitivity_analysis"),
    hook=_hook_for("sensitivity_analysis"),
    definition=(
        "Sensitivity analysis es probar cuánto cambia el intrinsic "
        "value cuando movés UNA assumption clave (manteniendo todo "
        "lo demás constante). Es el chequeo de robustez del modelo.\n\n"
        "Para DCF, las assumptions más sensitive son:\n"
        "  · **WACC**: ±50bp típicamente mueve intrinsic ±10-15%.\n"
        "  · **g terminal**: ±25bp ≈ ±5-10%.\n"
        "  · **EBIT margin assumed**: ±100bp ≈ ±15-25%.\n"
        "  · **Revenue growth rate**: ±100bp ≈ ±8-12%.\n\n"
        "Output típico: matriz 5×5 donde filas = WACC, columnas = g "
        "terminal, celdas = intrinsic value per share. Cada celda "
        "coloreada por upside / downside vs current price."
    ),
    why_matters=(
        "Un DCF que produce un point estimate ($75/share) sin "
        "sensitivity es engañoso — implica precision que no existe. "
        "Sensitivity revela cuán FRÁGIL es la tesis. Si moviendo "
        "WACC 50bp cambia tu valor 40%, el modelo es ruido. Si "
        "cambia 5%, el modelo es robusto. Damodaran insiste: 'siempre "
        "presentar sensitivity, nunca un solo número'."
    ),
    how_pros_analyze=(
        "1. **Identify the swing factors**: cuáles assumptions "
        "mueven más el output. En tech growth: g + margin. En "
        "industriales: WACC + capex. En banks: NIM + credit losses.\n"
        "2. **Reasonable ranges per assumption**:\n"
        "    · WACC: spot ± 100bp (sería ridícula una variación mayor)\n"
        "    · g terminal: 1-4% (capped por nominal GDP)\n"
        "    · EBIT margin: ±200bp del histórico through-cycle\n"
        "3. **Matriz visual**: 5×5 heatmap con verde upside, rojo "
        "downside. Color drives intuition más que numbers.\n"
        "4. **Spider chart / tornado**: ranking de assumptions por "
        "impact. Las top 3 son donde concentrar diligencia.\n"
        "5. **Combined sensitivities**: una assumption a la vez es "
        "óptimo para isolation; pero a veces se mueven en conjunto "
        "(WACC + risk-free rate)."
    ),
    key_metrics=[
        ("Intrinsic value range",
         "Min y max sobre todas las celdas. Si min < current price, "
         "no MoS robusto."),
        ("% celdas con upside positivo",
         ">75% = robust thesis · 50-75% balanced · <50% bear-leaning."),
        ("Sensitivity to top-3 inputs",
         "% Δ value / % Δ input. >2x = high sensitivity."),
        ("Implied breakeven assumption",
         "Qué WACC / g implica price = intrinsic. ¿Es plausible "
         "ese assumption?"),
    ],
    bullish_vs_bearish=[
        ("Matrix mostly green (most cells = upside)",
         "Matrix mostly red (most cells = downside)"),
        ("Even pessimistic corner shows ≥0 upside",
         "Optimistic corner barely shows upside (priced for perfection)"),
        ("Sensitivity low (model robust)",
         "Sensitivity high (model fragile)"),
        ("Top-3 sensitive inputs all in reasonable ranges",
         "Required assumptions for upside are extreme"),
    ],
    valuation_impact=(
        "Sensitivity analysis NO cambia tu point estimate — cambia "
        "tu CONFIDENCE en él. Después de hacer sensitivity, podés "
        "saber: si el modelo dice $100 con ±$30 (rango $70-130 a "
        "1 std), y current price es $85, tenés MoS modesto contra "
        "el downside ($70). Si current price es $50, tenés MoS "
        "amplio. Same point estimate, different decisions."
    ),
    case_study=(
        "**Tesla 2020 — DCF wars**: Damodaran público mostró su "
        "DCF con sensitivity matrix. Bear case (g 6%, WACC 9%): "
        "intrinsic $250. Bull case (g 12%, WACC 7%): intrinsic "
        "$2000. Range = 8x. Tesla cotizaba $400. Conclusión: el "
        "modelo era extremely sensitive — la 'tesis' dependía "
        "casi enteramente de qué corner del matrix elegías. Eso "
        "es definición de modelo frágil — el number no es robusto.\n\n"
        "**Caso limpio — Coca-Cola DCF**: assumptions reasonable, "
        "sensitivity moderate. Bear case $50, base $60, bull $72. "
        "Range solo 44%. Model robust = más confianza en el "
        "intrinsic."
    ),
    common_mistakes=[
        "Presentar un DCF point estimate sin sensitivity. Ingenuo.",
        "Sensitivity solo en WACC (ignorar g terminal y margin).",
        "Rangos de sensitivity extremos (WACC ±500bp). Diluyen el insight.",
        "No checkear cuán plausibles son los extremes ('bull case' requiere assumptions imposibles).",
        "Olvidar que múltiples assumptions tienden a moverse juntas (high growth + low WACC unlikely simultáneamente).",
    ],
    mental_model=(
        "Damodaran: 'el output de un DCF es una distribución, no un "
        "número'. La sensitivity matrix es tu intento de mapear esa "
        "distribución. Cuanto más amplia, más unsure estás. Cuanto "
        "más concentrada, más confianza. Y siempre preguntate: "
        "para que esto valga el current price, ¿qué assumptions "
        "necesito? Si las assumptions son extremas, hay MoS "
        "negativa."
    ),
    books=[_BOOK_MCKINSEY_VALUATION, _BOOK_DAMODARAN_VALUATION,
           _BOOK_KLARMAN_MOS],
    videos=[_VIDEO_DAMODARAN_VALUATION,
            Video(title="Tornado Charts and Sensitivity in DCF",
                  channel="Aswath Damodaran", minutes=25, url="",
                  why="Damodaran's practical guide.")],
    quotes=[
        _Q_DAMODARAN_STORY,
        Quote(text="The output of a DCF is a range of values, not a "
                   "point estimate. Anyone presenting a single number "
                   "as 'the value' doesn't understand the model.",
              author="Aswath Damodaran",
              source="Investment Valuation"),
        _Q_MARKS_RISK,
    ],
))
# ---------- Scenario analysis ----------
_add(Lesson(
    slug="scenario_analysis",
    label=_label_for("scenario_analysis"),
    category=_cat_for("scenario_analysis"),
    hook=_hook_for("scenario_analysis"),
    definition=(
        "Scenario analysis es construir modelos COMPLETOS bajo "
        "distintas narrativas, no solo mover una variable a la vez "
        "(eso es sensitivity). Típicamente 3 escenarios:\n\n"
        "  · **Bull case**: todo sale bien — growth alto sostenido, "
        "márgenes expansivos, multiples expansion.\n"
        "  · **Base case**: el escenario más probable — usually "
        "expansion modesta + estabilidad.\n"
        "  · **Bear case**: cosas salen mal — recession + margin "
        "compression + multiple contraction.\n\n"
        "A cada escenario se le asigna una PROBABILIDAD subjetiva "
        "(ej. 25% bull / 50% base / 25% bear). El intrinsic value "
        "probabilizado = Σ (escenario × probabilidad)."
    ),
    why_matters=(
        "Sensitivity isolates una variable; scenario analysis te "
        "fuerza a pensar de manera COHERENTE — si asumís bull "
        "growth, también deberías asumir bull margins (operating "
        "leverage). Klarman: 'no podés tener un escenario donde "
        "sales bajan pero margins se expanden — eso no es "
        "escenario, es contradicción'. Scenarios te obligan a "
        "pensar en términos de narrativas integradas, no de "
        "variables sueltas."
    ),
    how_pros_analyze=(
        "1. **Define la narrativa primero**: 'bull case = adopción "
        "rápida de AI, gross margin se mantiene 75%, growth 30%'. "
        "Luego traducila a inputs cuantitativos consistentes.\n"
        "2. **Probabilidades disciplinadas**: el bull case típico "
        "tiene 20-30% prob (no 50%). Si pensás que el bull case es "
        "60% prob, probablemente estás siendo optimista.\n"
        "3. **Bear case = recovery to mean, no end-of-world**: "
        "bear case razonable, no scenario worst-case ridiculous.\n"
        "4. **Compute weighted intrinsic**: 30% × $80 + 50% × $50 + "
        "20% × $20 = $52. Eso es tu base estimated.\n"
        "5. **Watch risk/reward asymmetry**: gain en bull / loss en "
        "bear. Si gain 60% / loss 40% probability-weighted, "
        "asymmetry favorable.\n"
        "6. **Update with new info**: el peso de cada escenario "
        "debería actualizarse con cada earnings."
    ),
    key_metrics=[
        ("Bull / base / bear scenario values",
         "Intrinsic per share bajo cada narrativa."),
        ("Probability weights",
         "Bull 20-30% · base 40-60% · bear 20-30% es estándar."),
        ("Weighted intrinsic value",
         "Σ (value × prob). El central forecast."),
        ("Bull-to-bear gain/loss ratio",
         "Upside in bull vs downside in bear. >2x = asymmetry "
         "favorable."),
        ("Implied probability of bear case",
         "Si current price = weighted intrinsic, ¿qué prob de bear "
         "implica el mercado? Compare vs tu prob."),
    ],
    bullish_vs_bearish=[
        ("Bull case requires plausible assumptions",
         "Bull case requires heroic assumptions"),
        ("Bear case downside <30% from current",
         "Bear case downside >50%"),
        ("Asymmetry gain/loss > 2:1",
         "Asymmetry adverse (gain < loss)"),
        ("Weighted intrinsic > current price con MoS",
         "Weighted intrinsic ≤ current price"),
    ],
    valuation_impact=(
        "Scenario analysis transforma el 'intrinsic value' de un "
        "número en una DISTRIBUCIÓN. Es lo que tradicionalmente se "
        "presenta en research reports: 'price target $80 in base "
        "case, $120 in bull, $40 in bear'. La decisión de inversión "
        "depende de las probabilidades — si vos pensás que la prob "
        "del bull es mayor que la implícita en el price, hay alpha. "
        "Si menor, hay sell signal."
    ),
    case_study=(
        "**Klarman Baupost — Greek debt 2011**: Baupost compró "
        "Greek government bonds a 30 cents on dollar. Bull case: "
        "Greece se restructura, pays 60c — gain 100%. Bear case: "
        "Greece default total, pays 10c — loss 67%. Klarman estimó "
        "prob 60% / 40%. Weighted: 60% × $0.60 + 40% × $0.10 = "
        "$0.40 vs $0.30 cost. 33% upside expected, asymmetric "
        "favorably. Greece paid 50c eventualmente, Baupost ganó "
        "60-80%.\n\n"
        "**Contraejemplo — many growth tech IPOs 2020-2021**: "
        "scenarios mostraban bull case 3-5x, bear case -50%. Pero "
        "las probabilidades implícitas del bull case eran 70-80% "
        "según los pitches — irreal. Cuando bear case materialized, "
        "stocks cayeron 60-80% (Robinhood, Zoom, Peloton). Lección: "
        "scenarios disciplinados con prob honestas habrían "
        "evitado el daño."
    ),
    common_mistakes=[
        "Hacer 'base case' que es prácticamente el bull case (sesgo de optimismo).",
        "Asignar 60-70% probabilidad al bull case. Casi siempre es 20-30%.",
        "Confundir scenarios (narrativas integradas) con sensitivity (variable única).",
        "No updatear probabilidades con new info (anchored a la tesis original).",
        "Ignorar que el mercado YA tiene una distribución implícita — tu scenario solo agrega valor si difiere materially.",
    ],
    mental_model=(
        "Klarman: 'invertir bien no es predecir el futuro — es "
        "ponerse en posición de ganar en múltiples futuros'. "
        "Scenario analysis es el método para hacer eso explícito. "
        "No buscás certeza (no existe); buscás que la DISTRIBUCIÓN "
        "de outcomes sea favorable. Pesando probabilities + "
        "magnitudes, podés decidir aún cuando no sabés qué va a "
        "pasar."
    ),
    books=[_BOOK_MARKS_MOST_IMPORTANT, _BOOK_KLARMAN_MOS,
           _BOOK_DAMODARAN_VALUATION,
           Book(title="Thinking in Bets", author="Annie Duke", year=2018,
                chapter_hint="Caps. 1-4 — decision-making bajo "
                              "incertidumbre",
                why="Cómo pensar en términos de probabilidades, no "
                     "certezas.")],
    videos=[
        Video(title="Howard Marks · The Most Important Thing",
              channel="Oaktree", minutes=60, url="",
              why="Marks sobre risk + probabilidades en investing."),
    ],
    quotes=[
        _Q_MARKS_RISK,
        Quote(text="Investing is not about being right or wrong; it's "
                   "about being right or wrong by enough to matter, "
                   "weighted by probability.",
              author="Seth Klarman",
              source="Margin of Safety"),
        Quote(text="In the long run, you'll be wrong more than you're "
                   "right. The key is to be more right when you're "
                   "right than wrong when you're wrong.",
              author="Annie Duke",
              source="Thinking in Bets"),
    ],
))
# ---------- Intrinsic value ----------
_add(Lesson(
    slug="intrinsic_value",
    label=_label_for("intrinsic_value"),
    category=_cat_for("intrinsic_value"),
    hook=_hook_for("intrinsic_value"),
    definition=(
        "Intrinsic value es el valor verdadero / fundamental de una "
        "empresa basado en sus cash flows futuros descontados — "
        "**independiente del precio de mercado actual**. Es el "
        "concepto central de Graham → Buffett → Damodaran.\n\n"
        "Williams (1938): 'el valor de cualquier activo es el "
        "present value de los cash flows que generará en el resto de "
        "su vida'.\n\n"
        "Crítico: intrinsic value es **una estimación**, no un hecho. "
        "Diferentes analistas con misma data pueden llegar a "
        "intrinsics distintos. Lo importante NO es ser preciso — es "
        "estar APPROXIMATELY RIGHT en lugar de PRECISELY WRONG."
    ),
    why_matters=(
        "Sin un concepto de intrinsic value, sos un trader — "
        "comprás cuando esperás que suba, vendés cuando esperás que "
        "baje. Con intrinsic value, sos un inversor — comprás cuando "
        "price < intrinsic, vendés cuando price >> intrinsic, y "
        "ignorás la volatilidad intermedia. Graham: 'the market is "
        "a weighing machine in the long run' — eventualmente price "
        "converge al intrinsic."
    ),
    how_pros_analyze=(
        "1. **Multiple methods, single estimate**: combinar DCF + "
        "comparables + asset-based. Cross-check entre métodos = "
        "confidence.\n"
        "2. **Range, not point**: presentar como rango ($60-80) con "
        "central estimate ($70). El rango captura tu uncertainty.\n"
        "3. **Update with new info**: intrinsic value cambia con "
        "cada earnings, cada macro shift, cada competitive change. "
        "Es living estimate, no static.\n"
        "4. **Compare to price**: gap > 30% (en cualquier dirección) "
        "es signal — investigate. Gap < 10% = market priceando "
        "correctly.\n"
        "5. **Reverse approach**: si current price implies WACC + g "
        "+ ROIC para be justified, ¿son those assumptions "
        "razonables? (Reverse DCF).\n"
        "6. **Margin of safety on the estimate**: el intrinsic "
        "value que calculaste tiene su own incertidumbre. MoS te "
        "protege de ese error."
    ),
    key_metrics=[
        ("Intrinsic value (central estimate)",
         "Tu best guess. Cross-checked across methods."),
        ("Intrinsic value range (low-high)",
         "Captura uncertainty. Range tight = confidence; wide = "
         "uncertainty."),
        ("Price-to-intrinsic ratio",
         "<0.7 = significant undervaluation · 0.7-1.3 = fair · "
         ">1.3 = overvaluation."),
        ("Implied assumptions of current price (reverse DCF)",
         "Si el price implica growth 25% por 10 años, ¿es "
         "razonable?"),
        ("Confidence level (high/medium/low)",
         "Self-assessment basado en data quality + business "
         "complexity."),
    ],
    bullish_vs_bearish=[
        ("Price << intrinsic (>30% discount) con high confidence",
         "Price >> intrinsic (>30% premium) con high confidence"),
        ("Multiple methods converge a similar intrinsic",
         "Methods divergen wildly (uncertainty)"),
        ("Intrinsic stable / updating positively over time",
         "Intrinsic getting cut (deteriorating business)"),
        ("Mr. Market overreaction (price wrong, intrinsic OK)",
         "Mr. Market correct (price reflects intrinsic deterioration)"),
    ],
    valuation_impact=(
        "Intrinsic value ES el target de toda valuation. P/E, "
        "EV/EBITDA, DCF, comparables — todos son métodos para "
        "estimarlo. Sin un concept de intrinsic value, no podés "
        "tener convicción para comprar contra-narrativa ('quien "
        "vende sabe algo que vos no'). Con intrinsic value, podés "
        "ignorar la volatilidad y mantener positions a través de "
        "drawdowns — la prueba de fuego del inversor."
    ),
    case_study=(
        "**Buffett comprando Washington Post 1973**: Graham y "
        "Buffett analyzaron WPO. Market cap ~$80M. Intrinsic value "
        "estimado por Buffett: $400-500M (basado en cash flows + "
        "real estate). 5-6x gap. Buffett compró 5-10% de la "
        "empresa. 30 años después se materializó el intrinsic — "
        "ganancia >100x. Caso textbook de Mr. Market irrational vs "
        "fundamental intrinsic value.\n\n"
        "**Contraejemplo — 'value investors' compraron Sears**: "
        "Eddie Lampert lo lideró con Bruce Berkowitz acompañándolo. "
        "Argumento: intrinsic value de real estate + brands > "
        "market cap. Resultado: el negocio deterioró tan rápido que "
        "el intrinsic value se redujo más rápido que el price. "
        "Bankrupt 2018. Lección: intrinsic value DEPENDE de la "
        "viabilidad del negocio underlying. Si el negocio muere, "
        "intrinsic dies con él."
    ),
    common_mistakes=[
        "Confundir intrinsic value con un número preciso. Es una estimación.",
        "Anclarse a un intrinsic value calculado hace 2 años cuando los fundamentals cambiaron.",
        "Asumir que el mercado eventualmente reconocerá tu intrinsic — puede tardar décadas o nunca.",
        "Confiar 100% en un solo método (DCF puro / multiples puro). Cross-check con varios.",
        "Olvidar que el intrinsic value puede ser MENOR al price actual y aún seguir cayendo (value traps).",
    ],
    mental_model=(
        "Damodaran: 'every valuation is wrong; the question is how "
        "wrong, in which direction, and by how much'. Aceptá que NO "
        "vas a estimar el intrinsic perfectamente. Tu trabajo es: "
        "(1) tener un proceso consistent y sin sesgos, (2) cross-"
        "check entre métodos, (3) margin of safety para el error "
        "inherente. Una vez que tenés intrinsic estimate, el "
        "market noise se vuelve oportunidad — porque vos sabés qué "
        "estás comprando."
    ),
    books=[_BOOK_INTELLIGENT_INVESTOR, _BOOK_BUFFETT_LETTERS,
           _BOOK_DAMODARAN_VALUATION, _BOOK_MCKINSEY_VALUATION,
           _BOOK_KLARMAN_MOS],
    videos=[_VIDEO_BUFFETT_1996,
            _VIDEO_DAMODARAN_VALUATION,
            Video(title="Damodaran on Intrinsic vs Relative Value",
                  channel="Aswath Damodaran", minutes=30, url="",
                  why="El profesor explica cómo combinar both methods.")],
    quotes=[
        _Q_BUFFETT_PRICE_VALUE,
        Quote(text="Intrinsic value is an all-important concept that "
                   "offers the only logical approach to evaluating the "
                   "relative attractiveness of investments. Intrinsic "
                   "value can be defined simply: it is the discounted "
                   "value of the cash that can be taken out of a "
                   "business during its remaining life.",
              author="Warren Buffett",
              source="Berkshire 2000 letter, owner's manual"),
        _Q_DAMODARAN_STORY,
        Quote(text="It is better to be approximately right than "
                   "precisely wrong.",
              author="John Maynard Keynes",
              source="(atribuido — capturado por Buffett a menudo)"),
    ],
))

# ============================================================
# Batch 3 — Sectores
# ============================================================

# ---------- Sector banks ----------
_add(Lesson(
    slug="sector_banks",
    label=_label_for("sector_banks"),
    category=_cat_for("sector_banks"),
    hook=_hook_for("sector_banks"),
    definition=(
        "Analizar un banco requiere un toolkit completamente "
        "distinto a una empresa industrial. Por qué: el balance "
        "ES el negocio — la deuda no es financing, es input. Los "
        "bancos:\n\n"
        "  · Tienen leverage estructural ~10x (regulatorio).\n"
        "  · Hacen plata del **spread** (yield assets − cost "
        "deposits) — NIM.\n"
        "  · Tienen regulación intensa (CET1, stress tests, FDIC).\n"
        "  · Su mayor riesgo NO es operacional, es CREDITO (loan "
        "losses).\n"
        "  · Quiebra súbitamente cuando hay run o reserve "
        "insufficient (Lehman, SVB).\n\n"
        "Por eso bancos cotizan en P/TBV + ROTE, no P/E, y "
        "requieren su propio playbook."
    ),
    why_matters=(
        "Bancos son ~12% del S&P y ~25% del MSCI World value. Los "
        "que no saben analizar bancos están privados de un sector "
        "enorme. Y los que aplican P/E genérico pierden plata — "
        "Lehman cotizaba P/E 8 días antes de quebrar. El sistema "
        "bancario es opaco, regulado y cíclico — entender estos "
        "três componentes es la base."
    ),
    how_pros_analyze=(
        "1. **ROTE > Cost of Equity**: el equivalente a ROIC > "
        "WACC. JPM ROTE 18%+ vs Ke 10% = compounder. Citi ROTE 7% "
        "vs Ke 11% = destrucción de valor.\n"
        "2. **NIM sensitivity to rates**: asset-sensitive (NIM "
        "expande con rates subiendo) vs liability-sensitive "
        "(contracts). Reportado en 10-Qs.\n"
        "3. **Credit quality**: NPL ratio + PCL (provisions for "
        "credit losses) + reserve coverage ratio. Subiendo = "
        "credit cycle deteriorating.\n"
        "4. **Capital adequacy**: CET1 > regulatory minimum + "
        "buffer para dividends/buybacks. <10% restringe capital "
        "return.\n"
        "5. **Deposit franchise**: CASA ratio + customer "
        "concentration. Sticky retail = competitive advantage; "
        "flighty corporate = fragility.\n"
        "6. **Loan book composition**: residential mortgage, "
        "commercial, credit card, auto — cada uno con risk "
        "profile distinto.\n"
        "7. **Off-balance-sheet**: derivatives, securitizations. "
        "Pre-2008 era la zona oculta."
    ),
    key_metrics=[
        ("ROTE (%)",
         ">15% excellent · 10-15% good · <10% subpar."),
        ("P/TBV",
         "JPM ~2.0x · BAC ~1.4x · Citi ~0.8x · EM banks ~1-2x."),
        ("NIM (%)",
         "US large-cap ~3% · regionals 3.5%+ · IBanks <2%."),
        ("CET1 ratio (%)",
         ">13% strong · 10-13% adequate · <10% restricted."),
        ("Efficiency ratio (%)",
         "<55% best · 55-65% normal · >70% bloated."),
        ("NPL ratio (%)",
         "<1% clean · 1-3% normal · >3% stress."),
    ],
    bullish_vs_bearish=[
        ("ROTE >15% sostained + P/TBV moderate",
         "ROTE <10% pero P/TBV ya pagando premium"),
        ("CET1 buffer cómodo (>12%)",
         "CET1 near regulatory minimum (no buybacks)"),
        ("NPL ratio estable + reserve coverage alto",
         "NPL subiendo + reservas no aumentando proporcionalmente"),
        ("Deposit franchise sticky (high CASA, retail-heavy)",
         "Funding mix wholesale-heavy / flighty corporate"),
        ("Loan growth ~ GDP (disciplined)",
         "Loan growth >> GDP (credit cycle warning)"),
    ],
    valuation_impact=(
        "Bancos cotizan en **P/TBV justificado = (ROTE − g) / (Ke − g)**. "
        "ROTE > Ke → P/TBV > 1. ROTE < Ke → P/TBV < 1. Esta sola "
        "ecuación explica casi todo: JPM ROTE 18% justifica P/TBV "
        "~2x; Citi ROTE 7% justifica P/TBV <1x. Los activistas "
        "atacan bancos donde el mercado pricea ROTE elevado pero "
        "el ROTE real es menor."
    ),
    case_study=(
        "**JPMorgan 2008-2024**: ROTE consistente 15%+ a través del "
        "GFC, COVID, rate cycle 2022-23. CET1 13%+. Diversificación "
        "(retail + corporate + IB + asset mgmt) suaviza cycles. "
        "Compounded 5x desde 2009 lows.\n\n"
        "**Contraejemplo — SVB 2023**: looked profitable (ROE 15%) "
        "pero deposit franchise era 90% uninsured corporate "
        "(frágil). Asset-liability mismatch: bonos long-duration vs "
        "depósitos demandables. Rate hikes 2022 wipearon unrealized "
        "losses. Run en 48h. Lección: bank profitability sin "
        "balance discipline es ilusión."
    ),
    common_mistakes=[
        "Aplicar P/E a banks. Usar P/TBV + ROTE.",
        "Confundir ROE con ROTE — ROE incluye goodwill.",
        "Confiar en NPL ratios sin verificar reserve coverage.",
        "Ignorar asset-liability mismatch (SVB 2023, S&L crisis).",
        "Asumir que big = safe. Tamaño no es sustituto de capital adequacy.",
    ],
    mental_model=(
        "Buffett: 'banking can be a wonderful business — if you "
        "don't do anything stupid'. Bancos hacen plata tomando "
        "depósitos baratos y prestando. Lo estúpido: leverage "
        "excesivo, asset-liability mismatch, exposición a "
        "credit cycles. Un banco disciplinado compounde 12-15% "
        "ROTE durante décadas. Uno indisciplinado puede wipear "
        "el equity en un trimestre."
    ),
    books=[_BOOK_DAMODARAN_VALUATION, _BOOK_DALIO_PRINCIPLES,
           _BOOK_BUFFETT_LETTERS,
           Book(title="Bank Investing: A Practitioner's Field Guide",
                author="Jeffrey Davis", year=2021,
                chapter_hint="Toda la parte sobre frameworks",
                why="Manual moderno escrito por un bank analyst.")],
    videos=[
        Video(title="How to Analyze a Bank Stock",
              channel="The Plain Bagel", minutes=15, url="",
              why="Intro accesible a P/TBV + ROTE."),
    ],
    quotes=[
        Quote(text="Banking is a very good business unless you do "
                   "dumb things.",
              author="Warren Buffett",
              source="Berkshire annual meetings"),
        _Q_BUFFETT_MOAT,
        _Q_GRAHAM_MOS,
    ],
))
# ---------- Sector tech ----------
_add(Lesson(
    slug="sector_tech",
    label=_label_for("sector_tech"),
    category=_cat_for("sector_tech"),
    hook=_hook_for("sector_tech"),
    definition=(
        "Tecnológicas no son una industria — son varias industrias "
        "que se reportan juntas:\n\n"
        "  · **SaaS / cloud**: revenue recurrente, NRR, gross "
        "margins 70-80%, capex-light (Salesforce, Snowflake).\n"
        "  · **Hardware**: cyclical, gross margins 30-50%, "
        "capex-intensive (Apple parcialmente, Dell).\n"
        "  · **Semis**: ver lección semis — propio sub-sector.\n"
        "  · **Platforms / ads**: network effects, take-rates, "
        "data flywheels (Meta, Google, Amazon ads).\n"
        "  · **AI / Frontier**: cap-ex masivo, narrative-driven "
        "(Nvidia, OpenAI ecosystem).\n\n"
        "Cada subgroup requiere métricas y multiples distintos. "
        "Aplicar el mismo framework a todas = error."
    ),
    why_matters=(
        "Tech es ~30% del S&P 500 — el sector más grande. Y el "
        "más volátil en multiples. SaaS pasó de P/S 25 (2021) a "
        "P/S 8 (2024). Saber qué multiplo y qué métricas usar "
        "para cada subgroup es la base. Y tech es donde el "
        "**Innovator's Dilemma** opera más fuerte — los líderes "
        "incumbentes pierden ante disruptores cada paradigm shift "
        "(IBM→Microsoft, Microsoft→Google, Google→OpenAI?)."
    ),
    how_pros_analyze=(
        "1. **Sub-classify first**: SaaS / hardware / platform / "
        "semis / AI infra. Cada uno con framework distinto.\n"
        "2. **Rule of 40** para SaaS (growth + FCF margin ≥ 40).\n"
        "3. **NRR > 120%** para SaaS de calidad.\n"
        "4. **Capital intensity**: hyperscalers (Microsoft, "
        "Amazon, Google) están en mega-cycle de capex AI. ¿FCF "
        "compression temporal o permanente?\n"
        "5. **Disruption risk**: ¿esta empresa es el "
        "incumbente o el disruptor? Innovator's Dilemma: "
        "incumbentes pierden cuando aparece mejor product cheaper.\n"
        "6. **Platform vs application**: platforms (Google, "
        "Amazon, Apple App Store) capturan más valor que apps. "
        "Net take-rate de la plataforma matters.\n"
        "7. **Path-to-profit clarity**: para growth tech "
        "pre-profit, ¿cuándo + cómo se llega a profitability "
        "GAAP?"
    ),
    key_metrics=[
        ("Revenue growth + Rule of 40 (SaaS)",
         "≥40 healthy · ≥50 elite."),
        ("NRR (SaaS) / Same-store sales (consumer tech)",
         ">120% NRR · positivo SSS = strong."),
        ("Gross margin (%)",
         "SaaS 70-80% · platforms 50-65% · hardware 30-50%."),
        ("EV/Revenue (growth tech)",
         "SaaS 5-15x normal · >20x bubble territory."),
        ("CapEx / Revenue (%)",
         "Software <5% · platforms 10-15% · hyperscalers 20%+ "
         "actualmente (AI capex super-cycle)."),
        ("R&D / Revenue (%)",
         "Leaders 15-25% · followers <10%."),
    ],
    bullish_vs_bearish=[
        ("Sub-clase correcta + multiplo apropiado",
         "Applying SaaS multiples to hardware (mispriced)"),
        ("Platform / network effect demostrado",
         "Single-product company sin moat estructural"),
        ("Path-to-profit clara (Rule of 40 trending up)",
         "Burning cash sin path visible (Peloton, Carvana 2022)"),
        ("Capex AI investments justified por demand visible",
         "Capex agresivo sin demand validation (Meta Metaverse 2022)"),
        ("Disruptor con moat early (Nvidia AI 2022)",
         "Incumbent ignorando disruption (Intel mobile 2010-15)"),
    ],
    valuation_impact=(
        "Tech multiples son MUY sensibles a rate cycle. Cuando "
        "rates suben, growth tech se comprime más que value "
        "(cash flows distantes valen menos). El 2022 fue "
        "textbook: Nasdaq -33% mientras S&P value -6%. Pero "
        "platforms con network effects (Visa, Microsoft) tienen "
        "menos sensitivity porque generan FCF presente fuerte. "
        "DCF tech requires: visibilidad de growth durability + "
        "ROIC steady-state plausible + reverse-DCF check."
    ),
    case_study=(
        "**Microsoft 2014-2024 — la transformación cloud**: "
        "Satya Nadella tomó CEO 2014. Pivot agresivo de license "
        "model a Azure + cloud subscription. ROIC pasó de 25% a "
        "30%+. Cloud margins (~70% gross) reemplazaron license "
        "margins. Stock 12x. Caso textbook de mature tech "
        "re-inventándose vs Innovator's Dilemma.\n\n"
        "**Contraejemplo — Intel 2014-2024**: mismo período. "
        "Negaron mobile, lost foundry edge a TSMC, missed AI "
        "wave. ROIC pasó de 22% a 4%. Stock cayó 40% mientras "
        "tech subió 200%+. Innovator's Dilemma en acción."
    ),
    common_mistakes=[
        "Aplicar SaaS multiples a empresas que no son SaaS (transactional, hardware).",
        "Ignorar el rate cycle. Growth tech es sensitive.",
        "Asumir que el líder actual será el líder en 10 años. Paradigm shifts matter.",
        "Pagar multiples 'AI premium' a empresas que solo tocan AI tangencialmente.",
        "Confundir narrative ('all in on AI') con execution real (revenue contribution).",
    ],
    mental_model=(
        "Christensen: 'el éxito de hoy es enemigo del éxito de "
        "mañana en tech'. Las empresas líderes optimizan para "
        "sus customers actuales y missean los disruptors que "
        "atacan low-end. Pensá: ¿qué startup hoy mira chiquita "
        "podría ser el Microsoft de la próxima década? Si no "
        "podés identificar el disrupter, capaz es el incumbent "
        "que estás analizando."
    ),
    books=[
        Book(title="The Innovator's Dilemma",
             author="Clayton Christensen", year=1997,
             chapter_hint="Toda la parte I",
             why="Por qué los líderes tech pierden contra "
                  "disruptors."),
        Book(title="Zero to One", author="Peter Thiel", year=2014,
             chapter_hint="Caps. 1-5 — monopolio + competition",
             why="Cómo piensa un founder/VC tech sobre moats."),
        _BOOK_DAMODARAN_VALUATION,
        _BOOK_BUFFETT_LETTERS,
    ],
    videos=[
        Video(title="Clayton Christensen · Innovator's Dilemma",
              channel="Talks at Harvard / TED", minutes=45, url="",
              why="El autor explica el framework en su own words."),
        _VIDEO_DAMODARAN_VALUATION,
    ],
    quotes=[
        Quote(text="If you don't cannibalize yourself, someone "
                   "else will.",
              author="Steve Jobs (atribuido)",
              source="Apple Inc."),
        Quote(text="The best minds of my generation are thinking "
                   "about how to make people click ads. That sucks.",
              author="Jeff Hammerbacher",
              source="(former Facebook engineer, sobre tech moats)"),
        _Q_BUFFETT_MOAT,
    ],
))
# ---------- Sector utilities ----------
_add(Lesson(
    slug="sector_utilities",
    label=_label_for("sector_utilities"),
    category=_cat_for("sector_utilities"),
    hook=_hook_for("sector_utilities"),
    definition=(
        "Las utilities (eléctricas, gas, agua) son negocios "
        "regulated — el regulador define qué retorno pueden "
        "ganar sobre el 'rate base' (asset base). Características:\n\n"
        "  · **Rate base × allowed ROE = regulated profit**. Si "
        "rate base = $20B y allowed ROE = 10%, regulated profit "
        "≈ $2B/año.\n"
        "  · **Capex-intensive**: invierten en plants, grids, "
        "líneas de transmisión. CapEx/revenue 15-25%.\n"
        "  · **Dividend-heavy**: payout ratios 60-80%. Investors "
        "los compran por yield, no growth.\n"
        "  · **Defensive**: demand es relativamente inelástica "
        "(electricity, water no se renuncia en recession).\n"
        "  · **Sensible a interest rates**: bonds proxies — "
        "cuando rates suben, utility valuations comprime."
    ),
    why_matters=(
        "Utilities son el sector más defensive del market. "
        "Durante recesiones outperform mientras growth se "
        "comprime. Pero también son los más sensibles a yield "
        "rate cycle — cuando 10Y treasury sube de 2% a 5%, "
        "utility yields tienen que subir también, lo que requiere "
        "que los stocks caigan. Saber el regulatory framework + "
        "rate base dynamics es la base."
    ),
    how_pros_analyze=(
        "1. **Allowed ROE vs achieved ROE**: si la utility "
        "consistentemente earns AT or ABOVE allowed ROE, está "
        "ejecutando bien. Si below, mismanagement.\n"
        "2. **Rate base growth**: la utility crece como crece su "
        "asset base. Rate base crece 5-7% típico via CapEx "
        "approval del regulator.\n"
        "3. **Regulatory environment**: states pro-utility (Texas, "
        "Florida) allow ROEs más altos; states adversarial "
        "(California, NY) menos. ROE allowed varía 8-12%.\n"
        "4. **Regulated vs unregulated mix**: empresas con "
        "merchant generation (no regulada) tienen más volatility. "
        "100% regulated = predictable.\n"
        "5. **Energy transition exposure**: utilities están "
        "reemplazando coal/gas con renewable + nuclear. Capex "
        "cycle masivo 2024-2040.\n"
        "6. **Dividend safety**: payout ratio + FCF coverage. "
        "Empresas reduciendo dividend = warning."
    ),
    key_metrics=[
        ("Allowed ROE (%)",
         "Definida por regulator. 8-12% típico US."),
        ("Achieved ROE vs Allowed",
         "Achievement ratio. 100% = ejecutando bien."),
        ("Rate base growth (%)",
         "5-7% típico. Subiendo en energy transition."),
        ("Dividend yield (%)",
         "3-5% típico. Yield premium sobre 10Y treasury proxy."),
        ("Payout ratio (%)",
         "60-80% típico. <60% = retiene más para growth; >85% "
         "= stress potential."),
        ("Capex / Depreciation",
         ">1 = growing rate base · <1 = shrinking (declining "
         "utility)."),
    ],
    bullish_vs_bearish=[
        ("Achieved ROE = allowed (executing)",
         "Achieved ROE consistently below allowed"),
        ("Rate base growth 5%+ via energy transition",
         "Rate base stagnant / shrinking"),
        ("Regulatory environment friendly",
         "Adversarial / political risk (CA wildfire liability)"),
        ("Dividend coverage healthy (FCF/dividend >1)",
         "Cutting dividend / payout >90%"),
        ("Rate cycle bottom (utilities relative-cheap)",
         "Rate cycle peak (utilities relative-expensive)"),
    ],
    valuation_impact=(
        "Utilities cotizan en P/E 18-24x con divid yield 3-5%. "
        "Cuando 10Y treasury sube 100bp, utility yields tienen "
        "que subir ~50bp también → price tiene que caer ~10-15%. "
        "Por eso utilities tienen alta correlación inversa con "
        "rates. En DCF, mejor usar regulated cash flow approach: "
        "rate base × allowed ROE × (1+g)^n, descontado a Ke."
    ),
    case_study=(
        "**NextEra Energy (NEE) 2010-2024**: la utility largest "
        "US. Energy transition leader (renewable + nuclear). "
        "Rate base crecida 7%+ CAGR. ROE ~12% sostained. "
        "Compounded ~13% annual (incl. div) durante 14 años. "
        "Caso de utility ejecutada bien en un mega-trend.\n\n"
        "**Contraejemplo — PG&E 2017-2019**: utility California. "
        "Wildfires causaron liability massive — $30B+. La "
        "regulación allowed pasar los costos a customers — pero "
        "el political backlash impidió. Bankrupted 2019. "
        "Lección: en utilities, el TAIL RISK regulatorio es "
        "real. Allowed ROE solo cuenta si te pagan."
    ),
    common_mistakes=[
        "Asumir que utilities son 'safe' sin chequear regulatory risk.",
        "Ignorar el rate cycle. Utilities y rates inversamente correlacionados.",
        "Aplicar DCF estándar sin reflectar regulated cash flow nature.",
        "Confiar en dividend yields sin verificar coverage (sustainability).",
        "Pasar por alto que merchant generation (no regulated) tiene volatility de commodity prices.",
    ],
    mental_model=(
        "Utilities son 'bonds with growth' — pensalas como bonds "
        "que también crecen el principal 5-7% anual via rate "
        "base expansion. Cuanto más bond-like (regulated, stable, "
        "dividend) más sensitive a rate cycle. Cuanto más merchant "
        "/ unregulated, más equity-like (commodity exposure)."
    ),
    books=[_BOOK_CFA, _BOOK_DAMODARAN_VALUATION,
           Book(title="Utility Investing: An Industry Primer",
                author="John Hanger", year=2019,
                chapter_hint="Rate base + allowed ROE mechanics",
                why="Manual técnico de utility analysis.")],
    videos=[
        Video(title="How Utilities Make Money",
              channel="The Plain Bagel", minutes=12, url="",
              why="Intro accesible al modelo regulado."),
    ],
    quotes=[
        Quote(text="Utilities are bonds with a bit of growth — and "
                   "growth that's regulated, predictable, and slow.",
              author="Warren Buffett (paráfrasis)",
              source="Berkshire on PacifiCorp + BNSF"),
        _Q_BUFFETT_PRICE_VALUE,
    ],
))
# ---------- Sector energy ----------
_add(Lesson(
    slug="sector_energy",
    label=_label_for("sector_energy"),
    category=_cat_for("sector_energy"),
    hook=_hook_for("sector_energy"),
    definition=(
        "Energía (oil & gas, coal, refining) es la industria más "
        "commodity-driven y cyclical del market. Subcategorías:\n\n"
        "  · **Upstream (E&P)**: explora + produce. Earnings "
        "swing brutalmente con oil price.\n"
        "  · **Midstream**: pipelines + storage. Más fee-based, "
        "menos cyclical.\n"
        "  · **Downstream / refining**: refining margins (crack "
        "spread). Counter-cyclical a veces.\n"
        "  · **Integrated majors**: XOM, CVX, Shell, BP — todos "
        "los anteriores.\n"
        "  · **Services**: Schlumberger, Halliburton. Cycle "
        "lag de upstream.\n\n"
        "El driver supreme: precio del subyacente (Brent, WTI, "
        "natural gas). Forecast el commodity = forecast los "
        "earnings."
    ),
    why_matters=(
        "Energy es ~4% del S&P pero 8-15% del EM markets. Su "
        "volatility extrema crea oportunidades y traps. El "
        "ejemplo más reciente: oil cayó a -$37 (negative!) en "
        "abril 2020 — los que compraron oil majors ganaron 5x en "
        "2 años. Pero los que compraron en peak 2014 ($110 oil) "
        "perdieron 60% durante los 5 años siguientes. Saber "
        "leer el cycle es la base."
    ),
    how_pros_analyze=(
        "1. **Breakeven price**: a qué oil price cada empresa es "
        "FCF-positive. Saudi Aramco breakeven ~$30; US shale "
        "marginal player ~$60. Cuando oil < breakeven, perdiendo "
        "cash.\n"
        "2. **Reserves life (R/P ratio)**: Reserves / annual "
        "production. >15 años = long-lived; <8 = need replacement.\n"
        "3. **Reserve replacement ratio**: nueva reserves added / "
        "production. >1.0 = creciendo reserve base; <1.0 = "
        "shrinking.\n"
        "4. **Capital discipline**: post-2014, las majors "
        "aprendieron a NO sobre-invertir en peak. CapEx growth "
        "<10% incluso con oil >$80 = discipline.\n"
        "5. **Decarbonization exposure**: gradient. Pure oil = "
        "exposed; integrated with renewable transition = hedged.\n"
        "6. **Through-cycle FCF**: en valuation, normalize oil "
        "price a $60-70 midcycle, no spot."
    ),
    key_metrics=[
        ("Breakeven oil price (USD/bbl)",
         "Lower = lower-cost producer. Top-tier majors $35-45."),
        ("Reserves Life (years)",
         ">15 long-lived (Saudi Aramco 80+) · <8 short-lived."),
        ("Reserve Replacement Ratio",
         ">1.0 growing · <1.0 declining."),
        ("FCF at midcycle oil ($60-70)",
         "Lo que la empresa genera through-cycle."),
        ("Dividend yield (%)",
         "Energy yields típically 3-7%."),
        ("Net debt / EBITDA (commodity adjusted)",
         "<1.5x at midcycle = healthy."),
    ],
    bullish_vs_bearish=[
        ("Cheap on through-cycle FCF basis",
         "Cheap on LTM peak earnings (cycle trap)"),
        ("Capital discipline (CapEx <50% of CFO)",
         "Capex bingo at peak prices (XOM 2008)"),
        ("Reserve replacement >1.0 + reserves long-lived",
         "Reserves declining / RR ratio <0.8"),
        ("Low breakeven (top-quartile cost)",
         "High breakeven (vulnerable in trough)"),
        ("Sentiment bearish + capex industry cuts",
         "Sentiment euphoric + capex bingo"),
    ],
    valuation_impact=(
        "Aplicar DCF estándar en energy es trampa — usa midcycle "
        "FCF. La metodología preferida: NAV (Net Asset Value) of "
        "reserves + risked development potential. Esto incorpora "
        "la realidad: la empresa es worth lo que valen sus "
        "reservas (PV of production), no su LTM earnings. Para "
        "midstream + downstream, DCF con stable cash flow funciona."
    ),
    case_study=(
        "**Oil majors 2020 trough**: Brent cayó a -$37 abril "
        "2020 por demand destruction COVID + Saudi-Russia "
        "production war. XOM dividend yield reached 10%+. Los "
        "que compraron ese trough ganaron 4-5x para 2022 cuando "
        "Brent llegó $120 post-Ukraine.\n\n"
        "**Contraejemplo — Chesapeake Energy 2014-2020**: "
        "shale producer apalancado. Capex bingo durante "
        "$100 oil 2011-14. Cuando oil cayó a $40 (2015) y luego "
        "$30 (2016), no podía servir la deuda. Bankrupted 2020. "
        "Lección: en commodities, capital discipline + balance "
        "fortress matters more que growth."
    ),
    common_mistakes=[
        "Usar LTM oil price en DCF. Always midcycle.",
        "Asumir que oil price actual continúa. Mean reversion potent en commodities.",
        "Confundir reserves (long-term) con production (current). Una empresa puede tener huge reserves pero declining production.",
        "Pasar por alto el decarbonization risk. Some reserves never get monetized.",
        "Comprar majors at peak oil con narrative 'permanent shortage'. Historically siempre wrong.",
    ],
    mental_model=(
        "Howard Marks: 'commodity cycles son la cosa más predecible "
        "del market — porque siempre van. La cosa más impredecible "
        "es el timing'. Energía es contrarian play par excellence. "
        "Comprar cuando hay euphoria de 'permanent shortage' = "
        "perder. Comprar cuando hay despair de 'industry "
        "dying' = clásico. Pero requires balance fortress para "
        "sobrevivir el trough — leverage mata en cíclicas."
    ),
    books=[
        Book(title="The Prize", author="Daniel Yergin", year=1991,
             chapter_hint="Historia + estructura de la industria",
             why="Texto definitivo de oil industry."),
        Book(title="The New Map", author="Daniel Yergin", year=2020,
             chapter_hint="Energy transition + geopolitics",
             why="Yergin updated sobre el futuro del sector."),
        _BOOK_MARKS_MARKET_CYCLE,
        _BOOK_DAMODARAN_VALUATION,
    ],
    videos=[
        Video(title="The Oil Market Explained",
              channel="Asianometry / Real Vision",
              minutes=30, url="",
              why="Cómo funciona el spot vs futures oil market."),
    ],
    quotes=[
        Quote(text="The best cure for high oil prices is high oil "
                   "prices. The best cure for low oil prices is low "
                   "oil prices.",
              author="Andy Hall (oil trader)",
              source="Industry adage"),
        _Q_MARKS_RISK,
        _Q_BUFFETT_PRICE_VALUE,
    ],
))
# ---------- Sector consumer ----------
_add(Lesson(
    slug="sector_consumer",
    label=_label_for("sector_consumer"),
    category=_cat_for("sector_consumer"),
    hook=_hook_for("sector_consumer"),
    definition=(
        "Consumer goods se divide en dos categorías muy distintas:\n\n"
        "  · **Consumer Staples**: comida, bebida, household, "
        "tobacco. Demanda inelástica — recession-resistant. "
        "Procter, Coca-Cola, Nestlé. Defensives.\n"
        "  · **Consumer Discretionary**: ropa, electronics, autos, "
        "restaurants, viajes. Demand elastic — cyclical. Nike, "
        "Disney, Tesla. Cyclicals.\n\n"
        "Drivers comunes: pricing power, brand equity, "
        "distribution moats. Pero ciclicidad opuesta — staples "
        "defensives en recession, discretionary se desploma."
    ),
    why_matters=(
        "Consumer goods son ~25% del S&P combinado. Es donde "
        "Buffett construyó Berkshire (Coca-Cola, See's, Geico "
        "indirectly). Las grandes brands en staples — Coca-Cola, "
        "P&G, Nestlé — son compounders de 7-10% real anual "
        "durante 50+ años. Saber leer brand equity + pricing "
        "power + distribution = identificar los próximos "
        "compounders."
    ),
    how_pros_analyze=(
        "1. **Pricing power test**: ¿puede subir precios above-"
        "inflation sin perder volume? (Ver lección pricing power).\n"
        "2. **Volume vs price split**: empresas top reportan "
        "ambos. Pricing positive sostained = strong brand.\n"
        "3. **Brand market share trend**: stable o growing = "
        "moat funcional. Erosionándose = competidor (private "
        "label, DTC disruptors) ganando.\n"
        "4. **Geographic diversification**: empresas EM-exposed "
        "tienen growth runway pero FX volatility.\n"
        "5. **DTC + e-commerce disruption**: traditional CPG "
        "compite ahora con D2C brands (Glossier, Casper). "
        "Tracking digital penetration.\n"
        "6. **Generational relevance**: ¿la próxima generación "
        "consume? Diet Coke en problemas con Gen Z health-conscious; "
        "Lululemon yes.\n"
        "7. **Discretionary cycle**: same-store sales en restaurants, "
        "transactions count, average ticket. Mid-cycle vs late."
    ),
    key_metrics=[
        ("Same-store sales (SSS, %)",
         "Restaurants, retail. Positive = healthy."),
        ("Volume vs Price split",
         "Strong brand: ambos positivos. Commoditized: solo price."),
        ("Gross margin (%)",
         "Brand premium: 50-65% · Mass market: 30-45%."),
        ("Marketing / Revenue (%)",
         "5-10% steady · subiendo agresivo = defensive."),
        ("E-commerce penetration (%)",
         "% of sales online. Trend matters más que level."),
        ("Brand equity rankings",
         "Interbrand, BrandZ ranking. Top 100 = compounders típicos."),
    ],
    bullish_vs_bearish=[
        ("Pricing + volume ambos positivos",
         "Solo crece por descuentos / promociones"),
        ("Market share stable o creciendo",
         "Erosionándose ante private label / DTC"),
        ("Gross margin durable through inflation",
         "Gross margin se comprime con cost inflation"),
        ("Brand relevant con next generation",
         "Brand aging (Boomers heavy, no Gen Z)"),
        ("E-commerce capability native",
         "Stuck en wholesale model legacy"),
    ],
    valuation_impact=(
        "Consumer staples cotizan premium (P/E 22-26) por "
        "predictability + recession resistance. Defensiva real "
        "que justifica low beta + low cost of equity. Consumer "
        "discretionary cotiza más cyclical — multiple expands "
        "early cycle, comprime late cycle. En recession, staples "
        "outperform discretionary por 20-30pp."
    ),
    case_study=(
        "**LVMH 2010-2024 — luxury compounding**: revenue 4x, "
        "operating margin 26%+. Estrategia: comprar brands "
        "establecidos (LV, Dior, Tiffany), aplicar disciplina, "
        "mantener pricing premium. Cada brand premium "
        "compounde. Stock 8x.\n\n"
        "**Contraejemplo — Bed Bath & Beyond 2015-2023**: "
        "missed e-commerce shift, perdió brand relevance vs "
        "Amazon + Wayfair, missed Gen Z. Bankrupted 2023. "
        "Lección: consumer brands aging mueren silenciosamente "
        "hasta que es muy tarde."
    ),
    common_mistakes=[
        "Confundir 'big brand' con 'brand moat'. Sears era enorme.",
        "Aplicar mismos multiples a staples vs discretionary.",
        "Ignorar generational shift. Brands relevantes a Boomers pueden estar muriendo con Gen Z.",
        "Pagar premium por consumer staples sin verificar pricing power presente.",
        "Subestimar disruption D2C / e-commerce a CPG tradicional.",
    ],
    mental_model=(
        "Buffett: 'when I look for businesses, I look for "
        "products people want to buy because they trust them — "
        "Coca-Cola, See's, Disney'. Brand consumer = trust + "
        "habit + emotional connection. Eso es resistente a "
        "competition mucho más que tech features. Pero requires "
        "verificar generacionalmente cada decade."
    ),
    books=[_BOOK_FISHER, _BOOK_BUFFETT_LETTERS,
           Book(title="Building Strong Brands",
                author="David Aaker", year=1996,
                chapter_hint="Caps. 1-6 — brand equity model",
                why="Texto fundacional de brand strategy."),
           Book(title="The Direct-to-Consumer Playbook",
                author="Mike Stevens", year=2023,
                chapter_hint="DTC vs traditional retail",
                why="Disrupción moderna explicada.")],
    videos=[_VIDEO_BUFFETT_1996,
            Video(title="LVMH Case Study",
                  channel="Wharton / CFA Institute",
                  minutes=30, url="",
                  why="Brand compounding en luxury.")],
    quotes=[
        _Q_BUFFETT_MOAT,
        Quote(text="If you give me $100 billion and ask me to take "
                   "away the soft drink leadership of Coca-Cola, I "
                   "can't do it.",
              author="Warren Buffett",
              source="2007 Berkshire annual meeting"),
        _Q_BUFFETT_PRICE_VALUE,
    ],
))
# ---------- Sector industrials ----------
_add(Lesson(
    slug="sector_industrials",
    label=_label_for("sector_industrials"),
    category=_cat_for("sector_industrials"),
    hook=_hook_for("sector_industrials"),
    definition=(
        "Industriales (machinery, defense, aerospace, transports) "
        "son sector cyclical donde la demanda viene de **capex de "
        "otras empresas** (B2B). Sub-categorías:\n\n"
        "  · **Capital goods**: Caterpillar, Deere, "
        "Honeywell — vendem maquinaria.\n"
        "  · **Aerospace/Defense**: Boeing, Lockheed, RTX. "
        "Mixed cycle (commercial cyclical, defense counter).\n"
        "  · **Transports**: UPS, FedEx, railroads. Sensible al "
        "GDP + freight cycle.\n"
        "  · **Building products**: Sherwin-Williams, Vulcan. "
        "Housing cycle.\n\n"
        "Métricas centrales: **backlog**, **book-to-bill ratio**, "
        "**lead times**. Estos leading indicators preceden "
        "revenue por 6-18 meses."
    ),
    why_matters=(
        "Industriales son el barómetro de la economía real — "
        "cuando Caterpillar guides up, hay capex cycle "
        "acelerando. Cuando Boeing announces order cancellations, "
        "demand softening. Saber leer estos signals temprano "
        "permite anticipar el ciclo broader."
    ),
    how_pros_analyze=(
        "1. **Backlog growth**: orders en queue not yet shipped. "
        "Sostained growth = revenue visibility 2-3 años.\n"
        "2. **Book-to-bill**: orders received / orders shipped. "
        ">1 building backlog · <1 burning through it.\n"
        "3. **Operating leverage**: industriales tienen high "
        "fixed costs (plants, R&D). Small revenue moves "
        "amplifican earnings.\n"
        "4. **Capex cycle position**: ISM PMI new orders = "
        "leading indicator. Subiendo desde <50 = early "
        "expansion (best for industrials).\n"
        "5. **Geographic mix**: US-only vs global. China "
        "exposure es double-edged (huge market + geopolitical).\n"
        "6. **Aftermarket revenue**: parts + services. "
        "Recurring + high margin. Mejor que solo OEM.\n"
        "7. **Defense vs commercial split**: defense es counter-"
        "cyclical (budget driven), commercial procyclical."
    ),
    key_metrics=[
        ("Backlog (USD)",
         "Pipeline future revenue. Trend matters."),
        ("Book-to-bill ratio",
         ">1.05 expanding · 0.95-1.05 stable · <0.95 contracting."),
        ("Aftermarket / Total revenue (%)",
         ">30% = sticky business · <15% = pure transactional."),
        ("Operating margin (%)",
         "Industriales: 12-20% best-in-class · 8-12% normal."),
        ("ROIC (%)",
         "Best industrials (Honeywell, Roper): 15-20%. Average "
         "industrials: 8-12%."),
        ("Capex / Revenue (%)",
         "15-25% típico para machinery. Heavy capex during cycle peaks."),
    ],
    bullish_vs_bearish=[
        ("Backlog growing + book-to-bill >1",
         "Backlog shrinking + book-to-bill <1"),
        ("ISM PMI rising from <50 (early cycle)",
         "ISM PMI falling from >55 (late cycle)"),
        ("Aftermarket % growing (more sticky revenue)",
         "Aftermarket flat (only transactional)"),
        ("Capital discipline (CapEx normalizado)",
         "Capex bingo at cycle peak"),
        ("Diversified end markets",
         "Single-end-market concentration (housing-only)"),
    ],
    valuation_impact=(
        "Industriales cotizan en P/E 15-22 con cyclical "
        "compression/expansion. Best-in-class (Honeywell, "
        "Roper, RTX) premium por mix de aftermarket + tech. "
        "Pure-play cyclicals (Caterpillar, Deere) trade at "
        "discount through-cycle. Usar normalized through-cycle "
        "earnings en valuation."
    ),
    case_study=(
        "**Honeywell 2003-2024**: transformación de cyclical "
        "industrial a aerospace + automation + software. ROIC "
        "subió de 10% a 17%. Margin expansion via mix shift. "
        "Stock 6x. Caso de industrial mejor que cyclical "
        "average via portfolio management.\n\n"
        "**Contraejemplo — Boeing 2018-2024**: 737 MAX grounding "
        "+ COVID + 787 quality issues + supply chain. Backlog "
        "intact pero delivery rate cayó. FCF negativo 5 años "
        "seguidos. Stock cayó 60%. Lección: industriales high "
        "operating leverage + high financial leverage = "
        "double exposed."
    ),
    common_mistakes=[
        "Comprar industriales en peak earnings (low P/E cyclical trap).",
        "Ignorar backlog + book-to-bill — leading indicators.",
        "Pagar premium por industrials sin verificar aftermarket sticky revenue.",
        "Subestimar el effect del rate cycle on capex demand (rates up = capex down 6m later).",
        "No diferencias defense (acyclical) de commercial aerospace (procyclical).",
    ],
    mental_model=(
        "Industriales son the canary in the coal mine para el "
        "economic cycle. Cuando Caterpillar dice 'mining demand "
        "soft', sabés que commodity cycle peaking. Cuando "
        "Honeywell aerospace orders surging, knows aircraft "
        "production accelerating. Pensá industriales no solo "
        "como inversión — son INFORMACIÓN sobre el broader cycle."
    ),
    books=[_BOOK_MCKINSEY_VALUATION, _BOOK_MARKS_MARKET_CYCLE,
           _BOOK_DALIO_PRINCIPLES,
           Book(title="Industrial Mega Trends",
                author="Jonathan Schramm", year=2021,
                chapter_hint="Caps. on automation + electrification",
                why="Trends modernos que reshape industriales.")],
    videos=[
        Video(title="Reading PMI for Investment Insights",
              channel="ISM / CFA Institute", minutes=20, url="",
              why="Cómo usar PMI como leading indicator."),
    ],
    quotes=[
        Quote(text="Industrials are the steel thread that runs "
                   "through the entire economy. When they're "
                   "humming, the economy hums.",
              author="Anonymous PM",
              source="Industry adage"),
        _Q_MARKS_RISK,
        _Q_BUFFETT_MOAT,
    ],
))
# ---------- Sector healthcare ----------
_add(Lesson(
    slug="sector_healthcare",
    label=_label_for("sector_healthcare"),
    category=_cat_for("sector_healthcare"),
    hook=_hook_for("sector_healthcare"),
    definition=(
        "Healthcare es el sector más heterogéneo del market. "
        "Sub-categorías:\n\n"
        "  · **Big Pharma**: Pfizer, J&J, Eli Lilly, Merck. "
        "Patent cliff cycles + pipeline R&D.\n"
        "  · **Biotech**: pre-revenue clinical trials. Binary "
        "outcomes — phase 3 success/fail.\n"
        "  · **Medical devices**: Medtronic, Boston Scientific. "
        "Steady, consumable revenue.\n"
        "  · **Managed care / health insurance**: UnitedHealth, "
        "Humana. Combined ratio + medical loss ratio (MLR).\n"
        "  · **Services / hospitals**: HCA, Tenet. Reimbursement "
        "+ procedure volume.\n\n"
        "Cada uno requiere framework distinto. Aplicar pharma "
        "metrics a managed care = error."
    ),
    why_matters=(
        "Healthcare es ~13% del S&P y ~18% del US GDP — uno de "
        "los sectores más grandes del economy. Tendencias "
        "macro (aging population, GLP-1 obesity drugs, AI "
        "drug discovery) lo convierten en mega-cycle. Pero "
        "patent cliffs, FDA risks, payer pressure crean tail "
        "risks específicos del sector."
    ),
    how_pros_analyze=(
        "1. **Pipeline analysis** (pharma): drugs en phase 2-3, "
        "expected revenue contribution, peak sales projections. "
        "Pipeline thin = patent cliff coming.\n"
        "2. **Patent expiry calendar**: blockbusters perdiendo "
        "exclusivity. Humira (AbbVie) perdió $20B+ revenue in "
        "2023-24. Patent cliff = bear thesis.\n"
        "3. **Trial probabilities** (biotech): phase 1→2 "
        "success rate ~60%, 2→3 ~30%, 3→approval ~50%. "
        "Compound probability matters.\n"
        "4. **MLR (managed care)**: medical losses / premiums. "
        "Industry target 80-85%. Lower = profitable but "
        "regulatory backlash.\n"
        "5. **Payer mix** (hospitals): Medicare/Medicaid vs "
        "commercial. Commercial is high-margin; gov't lower.\n"
        "6. **R&D efficiency**: $ invested per drug approved. "
        "Big Pharma struggling here — productivity declining "
        "decades."
    ),
    key_metrics=[
        ("R&D intensity (%)",
         "Big pharma 15-25% · biotech can be 100%+ pre-revenue · "
         "medical devices 5-10%."),
        ("Pipeline NPV / Market Cap",
         "Pharma valuation foundation. Pipeline > 50% MC = "
         "high R&D-dependent."),
        ("Patent cliff exposure (%)",
         "% revenue from drugs losing exclusivity in next 5y."),
        ("Medical Loss Ratio (managed care)",
         "80-85% target · <80% high profitability · >85% margin "
         "compression."),
        ("Phase 3 success probability (biotech)",
         "Historical 50%. Some indications higher (oncology lower, "
         "metabolic higher)."),
        ("ROIC (pharma)",
         "Best (Lilly with GLP-1): 30%+. Average: 10-15%."),
    ],
    bullish_vs_bearish=[
        ("Pipeline robust + patent cliff distant",
         "Pipeline thin + patent cliff <2y away"),
        ("Successful phase 3 trial + FDA approval visible",
         "Trial failure / FDA setback"),
        ("MLR managed (managed care)",
         "MLR creciendo + regulatory pressure"),
        ("Aging population mega-trend exposure",
         "Reimbursement pressure / drug pricing legislation"),
        ("Diversified pipeline / multiple indications",
         "Single-drug dependency (binary outcome)"),
    ],
    valuation_impact=(
        "Pharma valuation requires DCF on existing drugs + "
        "risked NPV de pipeline drugs. Biotechs pre-revenue: "
        "risked NPV de cada drug × prob of success. Managed care "
        "es más como insurance (P/E + MLR analysis). El error "
        "común: aplicar simple P/E sin pipeline analysis = "
        "subestimar pharma con strong pipeline o sobreestimar "
        "with patent cliff coming."
    ),
    case_study=(
        "**Eli Lilly 2020-2024 — GLP-1 revolution**: developed "
        "Mounjaro/Zepbound (semaglutide competitor). Mercado de "
        "obesity (~70M Americans clinically obese). Revenue "
        "projection 2030 GLP-1 globally $100B+. Stock 5x en 4 "
        "años, P/E pasó de 25 a 65. Caso de pipeline asset "
        "transformacional.\n\n"
        "**Contraejemplo — Bausch + Lomb / Valeant 2015-2017**: "
        "growth via acquisitions con drugs price-gouged + heavy "
        "debt. Cuando regulatory + customer backlash hit, stock "
        "cayó 95%. Lección: pharma growth via pricing "
        "agresivo = transitorio, no sostenible."
    ),
    common_mistakes=[
        "Comprar pharma sin understanding patent cliff calendar.",
        "Sub-estimar trial failure probability (biotechs son binary).",
        "Confiar en management's peak sales projections sin validar.",
        "Aplicar P/E genérico a managed care (usar MLR + insurance metrics).",
        "Ignorar reimbursement dynamics (Medicare pricing power growing).",
    ],
    mental_model=(
        "Healthcare es donde science meets business — y donde la "
        "ciencia es **probabilística**. Pensá en términos de "
        "expected value: pipeline drug con phase 3 trial = NPV × "
        "probability of success. Don't fall in love con una "
        "story; toda thesis pharma puede flame out por un "
        "single trial. Diversification across indications es el "
        "mecanismo de risk management natural."
    ),
    books=[_BOOK_FISHER, _BOOK_DAMODARAN_VALUATION,
           Book(title="The Pharmaceutical Industry",
                author="Frederick Frank", year=2020,
                chapter_hint="R&D economics + patent cycles",
                why="Manual técnico del sector."),
           Book(title="The Truth About the Drug Companies",
                author="Marcia Angell", year=2004,
                chapter_hint="Cómo funciona la economía pharma",
                why="Visión crítica + entendimiento profundo del "
                     "modelo.")],
    videos=[
        Video(title="How Drug Discovery Works",
              channel="Vox / CNBC", minutes=20, url="",
              why="Intro accesible al pipeline + FDA process."),
    ],
    quotes=[
        Quote(text="Drug discovery is like baseball — you fail "
                   "70% of the time and people still call you a "
                   "star.",
              author="Anonymous pharma executive",
              source="Industry folklore"),
        _Q_MARKS_RISK,
        _Q_BUFFETT_PRICE_VALUE,
    ],
))
# ---------- Sector semis ----------
_add(Lesson(
    slug="sector_semis",
    label=_label_for("sector_semis"),
    category=_cat_for("sector_semis"),
    hook=_hook_for("sector_semis"),
    definition=(
        "Semiconductores son la industria más cíclica + más "
        "geopolitically charged del tech stack. Estructura "
        "competitiva moderna:\n\n"
        "  · **Fabless designers**: Nvidia, AMD, Qualcomm. "
        "Diseñan chips, no manufacturan. Asset-light, R&D-heavy.\n"
        "  · **Foundries**: TSMC, Samsung Foundry. Manufacturan "
        "para fabless. Capital-intensive ($30B+ fab cost).\n"
        "  · **IDMs (Integrated Device Manufacturers)**: Intel "
        "tradicionalmente, Samsung memory. Diseñan + manufacturan.\n"
        "  · **Equipment**: ASML (EUV monopoly), Applied "
        "Materials, Lam Research. Suministran a foundries.\n"
        "  · **Memory**: Micron, SK Hynix. Commoditized, "
        "ultra-cyclical.\n\n"
        "Geopolitics matter — TSMC Taiwan concentration, China "
        "ambitions, US export controls."
    ),
    why_matters=(
        "Semis representan el TECH STACK underlying todo lo demás "
        "(AI, autos, IoT, consumer electronics). Pero son "
        "cyclically extremes: Nvidia +800% en 2023, AMD -60% "
        "en 2022. El AI super-cycle 2023-2030 + geopolitical "
        "shifts crean opportunities masivas — y trampas. "
        "Saber leer este sector requires entendiment del ciclo "
        "AND del competitive landscape."
    ),
    how_pros_analyze=(
        "1. **Cycle position**: book-to-bill, lead times, "
        "inventory days. (Ver lección semis_metrics detallada).\n"
        "2. **Competitive position**: ¿líder en design (TSMC 3nm, "
        "Nvidia AI), o follower? Followers tienen tougher "
        "economics.\n"
        "3. **R&D intensity**: 15-25% es leader (Nvidia, ASML, "
        "TSMC). <10% = ceding ground.\n"
        "4. **Capital intensity**: foundries 30%+ capex/revenue; "
        "fabless <10%. Capex-light has better through-cycle FCF.\n"
        "5. **Geographic / customer concentration**: TSMC mfg "
        "Taiwan + customer Apple/NVDA concentrated. Tail risks.\n"
        "6. **End-market exposure**: AI/data center growing 30%+; "
        "PC/mobile stagnant; auto growing 10-15%. Mix matters.\n"
        "7. **Geopolitical**: US-China escalation impact on "
        "specific players (semis equipment China-restricted; "
        "TSMC Taiwan exposure)."
    ),
    key_metrics=[
        ("Book-to-bill ratio",
         ">1.1 expanding · <0.9 contracting."),
        ("R&D / Revenue (%)",
         "Leaders 15-25% · followers <10%."),
        ("Gross margin (%)",
         "Foundries 50-55% · Nvidia AI 75%+ · memory cyclical "
         "20-50%."),
        ("Capex / Revenue (%)",
         "Foundries 30%+ · fabless <10%."),
        ("AI revenue % (2024)",
         "Nvidia ~75% · Broadcom ~25% · AMD ~15% · Intel <10%."),
        ("Geographic exposure to China",
         "Restricted for advanced nodes. Material impact for many."),
    ],
    bullish_vs_bearish=[
        ("Líder competitivo + AI exposure growing",
         "Lagging competitive position (Intel 2014-24)"),
        ("Book-to-bill >1 sostenido (upcycle)",
         "Book-to-bill <1 (downcycle starting)"),
        ("Diversified end markets",
         "Concentrated customer / Single market exposed"),
        ("R&D intensity sostained (preserving lead)",
         "R&D cuts (ceding tech edge)"),
        ("Geopolitical winner (US-aligned, fab diversification)",
         "Geopolitical loser (China-exposed, Taiwan concentrated)"),
    ],
    valuation_impact=(
        "Semis multiples swing wildly through cycle. Forward "
        "P/E puede ir de 12 (trough) a 40 (peak euphoria). "
        "Through-cycle normalization es essential. AI super-"
        "cycle players (Nvidia, AVGO, TSMC) merecen premium "
        "actualmente — pero su sostained depende de AI capex "
        "durability (uncertain post 2027)."
    ),
    case_study=(
        "**TSMC 2010-2024 — foundry monopoly**: only company "
        "world manufacturing leading-edge (3nm, 2nm). All major "
        "fabless customers (Apple, Nvidia, AMD, Broadcom). ROIC "
        "30%+ sostained. Stock 8x. Geopolitical concentration "
        "(Taiwan) es el solo risk material.\n\n"
        "**Contraejemplo — Intel 2014-2024**: lost manufacturing "
        "edge a TSMC (couldn't deliver 10nm/7nm timely). Lost "
        "mobile (no chips iPhone). Missed AI wave (no GPUs). "
        "ROIC pasó de 22% a 4%. Stock cayó 50% mientras "
        "industry subió 300%+. Lección: en semis, manufacturing "
        "execution matters tanto como design."
    ),
    common_mistakes=[
        "Comprar en peak earnings (low P/E cyclical trap).",
        "Asumir AI demand continues forever sin chequear capex digestion 2027+.",
        "Subestimar geopolitical risk (TSMC Taiwan).",
        "Confundir all-semis con AI-semis (very different end markets).",
        "Pasar por alto R&D intensity — losing tech edge takes years to manifest pero killer when materializes.",
    ],
    mental_model=(
        "Semis es una industria where the timing of cycles "
        "doesn't matter — sus ciclos son inevitables, pero el "
        "winner-vs-loser dynamic es PERSISTENT. Líderes (TSMC, "
        "ASML, Nvidia hoy) tienden a sostained leads decades; "
        "losers (Intel, MIPS, others) rarely vuelven. Identify "
        "los winners structurally, then time el cycle entry."
    ),
    books=[
        Book(title="Chip War", author="Chris Miller", year=2022,
             chapter_hint="Estructura competitiva moderna",
             why="The book on semis right now."),
        _BOOK_DAMODARAN_VALUATION,
        Book(title="The Last Wave",
             author="Walter Isaacson", year=2014,
             chapter_hint="Caps. sobre Intel + semis history",
             why="Historia del sector + key players."),
    ],
    videos=[
        Video(title="The Semiconductor Cycle Explained",
              channel="Asianometry", minutes=25, url="",
              why="Channel especializado en semis."),
        Video(title="Chris Miller · Chip War",
              channel="Talks at Google", minutes=60, url="",
              why="El autor explica la geopolítica."),
    ],
    quotes=[
        Quote(text="In semiconductors, the only constant is "
                   "cyclicality. The companies that survive are the "
                   "ones that prepare for the downcycle when "
                   "everyone is partying at the peak.",
              author="Morris Chang",
              source="Founder of TSMC"),
        Quote(text="Whoever controls the design of advanced chips "
                   "controls the future of technology.",
              author="Chris Miller",
              source="Chip War"),
        _Q_MARKS_RISK,
    ],
))

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
