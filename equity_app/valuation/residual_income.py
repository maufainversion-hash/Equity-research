"""
Residual Income (Edwards-Bell-Ohlson) valuation.

    Equity Value = Book Value + Σ PV(Residual Income)
    Residual Income_t = NI_t − r_e · BV_{t-1}

The model is preferred over FCFF DCF for financials (banks, insurers)
where the line between operating and financing cash is blurry and FCF
can be misleading.

Two stages here:
- Stage 1: explicit RI projection for ``stage1_years`` based on a
  forward ROE growth assumption.
- Stage 2: the residual income FADES — the excess return over the cost
  of equity is competed away, so the post-explicit tail decays at a
  persistence factor ω per year rather than growing in perpetuity.

Like DDM, the discount rate is the **cost of equity**, not WACC.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd

from analysis.ratios import _get, cagr
from core.constants import DCF_DEFAULTS
from core.exceptions import InsufficientDataError, ValuationError


# Factor de persistencia del ingreso residual. El exceso de retorno
# sobre el costo de capital se erosiona por competencia; ω es la
# fracción que sobrevive cada año tras la etapa explícita. La media
# empírica de la economía (Dechow-Hutton-Sloan) ronda 0.62; 0.70 toma
# en cuenta que RI se aplica a negocios con foso (bancos, aseguradoras).
_DEFAULT_PERSISTENCE = 0.70


# ============================================================
# Result
# ============================================================
@dataclass
class RIResult:
    intrinsic_value_per_share: float
    book_value_per_share: float
    pv_explicit_ri: float
    pv_terminal_ri: float
    cost_of_equity: float
    base_roe: float
    base_eps: float
    stage1_growth: float
    terminal_growth: float
    persistence_factor: float
    stage1_years: int
    projected_ri: list[float] = field(default_factory=list)


# ============================================================
# Internals
# ============================================================
def _shares_outstanding(income: pd.DataFrame, balance: pd.DataFrame) -> float:
    sh = _get(income, "weighted_avg_shares")
    if sh is not None and not sh.dropna().empty:
        return float(sh.dropna().iloc[-1])
    sh = _get(balance, "common_shares_outstanding")
    if sh is not None and not sh.dropna().empty:
        return float(sh.dropna().iloc[-1])
    raise InsufficientDataError("Cannot find share count")


def _historical_roe(income: pd.DataFrame, balance: pd.DataFrame,
                    *, max_years: int = 5) -> tuple[float, Optional[float]]:
    """Returns (mean ROE, mean ROE growth) over up to ``max_years``."""
    ni = _get(income, "net_income")
    eq = _get(balance, "total_equity")
    if ni is None or eq is None:
        raise InsufficientDataError("Need net income and total equity")
    df = pd.concat([ni, eq], axis=1).dropna().tail(max_years)
    df.columns = ["ni", "eq"]
    df = df[df["eq"] > 0]
    if df.empty:
        raise InsufficientDataError("All equity values are non-positive")
    roe_series = df["ni"] / df["eq"]
    mean_roe = float(roe_series.mean())
    g = None
    if len(roe_series) >= 2 and roe_series.iloc[0] > 0:
        c = cagr(roe_series)
        g = c if np.isfinite(c) else None
    return mean_roe, g


# ============================================================
# Public API
# ============================================================
def run_residual_income(
    *,
    income: pd.DataFrame,
    balance: pd.DataFrame,
    cost_of_equity: float,
    stage1_years: int = 5,
    stage1_growth: Optional[float] = None,
    terminal_growth: Optional[float] = None,
    persistence: float = _DEFAULT_PERSISTENCE,
) -> RIResult:
    """
    Two-stage Residual Income.

    ``stage1_growth`` is applied to **net income** (not EPS) — book value
    grows by retained earnings each year (we assume zero net buybacks/
    issuance in projections).
    """
    # ``g_t`` ya NO alimenta un valor terminal de crecimiento perpetuo
    # (ver el bloque terminal abajo) — sólo sirve de fallback del
    # crecimiento de etapa 1 cuando la empresa no tiene historial de NI.
    g_t = float(terminal_growth if terminal_growth is not None
                else DCF_DEFAULTS["terminal_growth"])

    ni_s = _get(income, "net_income")
    eq_s = _get(balance, "total_equity")
    if ni_s is None or eq_s is None:
        raise InsufficientDataError("Need net income and total equity")

    ni_clean = ni_s.dropna()
    eq_clean = eq_s.dropna()
    if ni_clean.empty or eq_clean.empty:
        raise InsufficientDataError(
            "Net income or equity series is all-NaN — typical of "
            "thin SEC filers / fresh IPOs."
        )
    last_ni = float(ni_clean.iloc[-1])
    last_bv = float(eq_clean.iloc[-1])
    if last_bv <= 0:
        raise ValuationError(f"Book value is non-positive ({last_bv:,.0f})")

    base_roe = last_ni / last_bv
    # Sanity de entrada: un ROE absoluto > 100% casi siempre es un error
    # de unidades (NI y patrimonio en escalas/monedas distintas), no un
    # negocio real. RI sobre datos así explota — mejor declinar y dejar
    # que el agregador use los otros modelos.
    if not np.isfinite(base_roe) or abs(base_roe) > 1.0:
        raise ValuationError(
            f"ROE base implausible ({base_roe:.0%}) — datos poco "
            f"confiables para Ingreso Residual"
        )
    shares = _shares_outstanding(income, balance)
    bvps = last_bv / shares
    eps = last_ni / shares

    # Default growth = NI CAGR.
    if stage1_growth is None:
        ni_clean = ni_s.dropna().tail(5)
        if len(ni_clean) >= 2 and ni_clean.iloc[0] > 0:
            cg = cagr(ni_clean)
            stage1_growth = cg if np.isfinite(cg) else g_t
        else:
            stage1_growth = g_t
    # RI es muy sensible al crecimiento proyectado: proyectar el NI a
    # 25-30% anual durante 5 años hace explotar el valor terminal. Se
    # acota más fuerte que el DCF — las empresas para las que RI es el
    # método correcto (bancos, aseguradoras, brokers) son maduras.
    g1 = float(np.clip(stage1_growth, -0.10, 0.12))

    bv_t = last_bv
    ni_t = last_ni
    pv_explicit = 0.0
    projected_ri: list[float] = []

    for t in range(1, stage1_years + 1):
        ni_t = ni_t * (1.0 + g1)
        ri = ni_t - cost_of_equity * bv_t
        projected_ri.append(ri)
        pv_explicit += ri / (1.0 + cost_of_equity) ** t
        bv_t = bv_t + ni_t                           # zero-payout assumption

    # Terminal — el ingreso residual se DESVANECE, no crece a perpetuidad.
    # El exceso de retorno sobre el costo de capital se erosiona por la
    # competencia (modelo de Ohlson). La cola posterior a la etapa
    # explícita decae geométricamente a un factor de persistencia ω:
    #     PV_n(cola) = RI_n · ω / (1 + r − ω)
    # ω→0 el exceso desaparece de inmediato; ω→1 casi perpetuo. El
    # denominador (1 + r − ω) es siempre positivo para ω < 1 — el
    # terminal NO puede explotar como con la fórmula de Gordon (r − g),
    # que era la causa de los intrínsecos disparatados en financieros.
    omega = float(np.clip(persistence, 0.0, 0.95))
    ri_n = projected_ri[-1]
    terminal_value = ri_n * omega / (1.0 + cost_of_equity - omega)
    pv_terminal = terminal_value / (1.0 + cost_of_equity) ** stage1_years

    equity_value = last_bv + pv_explicit + pv_terminal
    if equity_value <= 0:
        raise ValuationError("Computed equity value is non-positive")
    # Sanity de salida: el valor de un financiero rara vez supera ~5×
    # su valor libro. Un intrínseco por encima de eso es la proyección
    # de RI divergiendo sobre datos finos — se declina para no
    # contaminar el agregado (era la causa de los "+390%" que aparecían
    # en bancos internacionales).
    if equity_value > 5.0 * last_bv:
        raise ValuationError(
            f"Ingreso Residual divergió — intrínseco "
            f"{equity_value / last_bv:.1f}× el valor libro; datos poco "
            f"confiables"
        )

    return RIResult(
        intrinsic_value_per_share=float(equity_value / shares),
        book_value_per_share=float(bvps),
        pv_explicit_ri=float(pv_explicit / shares),
        pv_terminal_ri=float(pv_terminal / shares),
        cost_of_equity=float(cost_of_equity),
        base_roe=float(base_roe),
        base_eps=float(eps),
        stage1_growth=g1,
        terminal_growth=g_t,
        persistence_factor=float(omega),
        stage1_years=int(stage1_years),
        projected_ri=[float(x / shares) for x in projected_ri],
    )
