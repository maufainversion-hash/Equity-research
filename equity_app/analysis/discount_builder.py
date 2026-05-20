"""
Construcción del snapshot de valuación del catálogo.

Lógica compartida por el CLI (``scripts/build_discount_snapshot.py``) y
el botón "Actualizar datos" de la página Discount. Valúa cada empresa
del catálogo con el pipeline completo y escribe el resultado en
``data/discount_snapshot.json`` — ticker, precio, valor intrínseco,
upside, veredicto, capitalización, ratios y resumen de valuación.

Es lento (un análisis por empresa, cientos de llamadas API): pensado
para correrse on-demand, nunca al abrir una página.
"""
from __future__ import annotations
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Callable, Optional

from data.company_catalog import (
    Company, all_companies, is_high_inflation_ticker,
)
from data.discount_data import write_snapshot

log = logging.getLogger(__name__)

# Callback de progreso: progress(hechas, total, mensaje).
ProgressFn = Callable[[int, int, str], None]

# Ratios del quick-look — claves de calculate_ratios.
_QUICK_RATIOS = [
    "Revenue Growth %", "Operating Margin %", "Net Margin %",
    "ROE %", "ROIC %", "Debt/Equity", "Current Ratio",
]

# Cota de cordura: un intrínseco fuera de [0.2×, 5×] el precio casi
# siempre es un error de datos (share count, moneda nominal), no un
# descuento real — se descarta para no contaminar el snapshot.
_SANITY_LO, _SANITY_HI = 0.2, 5.0


def _num(v):
    try:
        f = float(v)
        return round(f, 4) if f == f else None      # f==f descarta NaN
    except (TypeError, ValueError):
        return None


def _model_intrinsic(model) -> Optional[float]:
    if model is None:
        return None
    for attr in ("intrinsic_value_per_share", "intrinsic_per_share",
                 "value_per_share", "implied_per_share_median"):
        v = _num(getattr(model, attr, None))
        if v is not None:
            return v
    return None


def _ratios_block(income, balance, cash, wacc) -> dict:
    """Última fila de calculate_ratios, sólo los ratios del quick-look."""
    out: dict = {}
    try:
        from analysis.ratios import calculate_ratios
        df = calculate_ratios(income, balance, cash, wacc=wacc)
        if df is not None and not df.empty:
            last = df.iloc[-1]
            for k in _QUICK_RATIOS:
                if k in df.columns:
                    out[k] = _num(last.get(k))
    except Exception as e:
        log.debug("ratios block failed: %s", e)
    return out


def _record(co: Company) -> Optional[dict]:
    """Valúa una empresa y arma su registro del snapshot, o ``None`` si
    no se pudo valuar de forma confiable."""
    # Imports pesados diferidos — así importar este módulo es barato.
    from analysis.assumptions import Assumptions
    from analysis.parallel_loader import load_bundle
    from core.valuation_pipeline import run_valuation

    bundle = load_bundle(co.ticker)
    if bundle.income is None or bundle.income.empty:
        return None
    quote = bundle.quote or {}
    price = _num(quote.get("price"))

    results = run_valuation(
        ticker=co.ticker, income=bundle.income, balance=bundle.balance,
        cash=bundle.cash, assumptions=Assumptions(), peers=bundle.peers,
        current_price=price, sector=bundle.sector,
        info=bundle.info, quote=quote,
    )
    agg = getattr(results, "aggregator", None)
    intrinsic = _num(getattr(agg, "intrinsic_per_share", None))
    if price is None or intrinsic is None or price <= 0 or intrinsic <= 0:
        return None
    if not (_SANITY_LO <= intrinsic / price <= _SANITY_HI):
        log.debug("%s descartada — intrínseco/precio %.1f fuera de rango",
                  co.ticker, intrinsic / price)
        return None

    rating = getattr(results, "rating", None)
    wacc = _num(getattr(getattr(results, "wacc", None), "wacc", None))
    cv = _num(getattr(agg, "dispersion_cv", None))

    return {
        "ticker":     co.ticker,
        "name":       co.name,
        "country":    co.country,
        "sector":     co.sector,
        "region":     co.region,
        "price":      price,
        "market_cap": _num(getattr(bundle, "market_cap", None)),
        "intrinsic":  intrinsic,
        "upside_pct": round((intrinsic - price) / price * 100.0, 1),
        "verdict":    str(getattr(rating, "verdict", "") or "—"),
        "confidence": str(getattr(rating, "confidence", "") or ""),
        "pe":         _num((bundle.info or {}).get("trailingPE")),
        "wacc_pct":   round(wacc * 100.0, 1) if wacc is not None else None,
        "ratios":     _ratios_block(bundle.income, bundle.balance,
                                    bundle.cash, wacc),
        "valuation": {
            "dcf":       _model_intrinsic(getattr(results, "dcf", None)),
            "epv":       _model_intrinsic(getattr(results, "epv", None)),
            "multiples": _model_intrinsic(getattr(results, "multiples", None)),
            "n_models":  getattr(agg, "n_models_used", None),
            "dispersion_pct": round(cv * 100.0, 0) if cv is not None else None,
        },
    }


def _record_safe(co: Company) -> tuple[Optional[dict], str, str]:
    """Versión thread-safe de ``_record`` — devuelve ``(rec, tag, msg)``
    en lugar de lanzar. ``tag`` ∈ {"ok", "skipped", "fail"}."""
    if is_high_inflation_ticker(co.ticker):
        return None, "skipped", f"{co.ticker} — omitida (alta inflación)"
    try:
        rec = _record(co)
        if rec is not None:
            return (rec, "ok",
                    f"{co.ticker} — upside {rec['upside_pct']:+.0f}% "
                    f"{rec['verdict']}")
        return None, "fail", f"{co.ticker} — sin datos / no confiable"
    except Exception as e:
        log.debug("snapshot record failed for %s: %s", co.ticker, e)
        return None, "fail", f"{co.ticker} — error {type(e).__name__}"


def build_snapshot(
    *,
    limit: int = 0,
    region: Optional[str] = None,
    progress: Optional[ProgressFn] = None,
    workers: int = 4,
) -> dict:
    """Valúa el catálogo y escribe el snapshot — en paralelo.

    ``workers`` — valuaciones simultáneas. Default 4: a 1.5-3s por
    empresa secuencial, paraleliza 4 a la vez baja el tiempo total de
    ~8 min a ~2-3 min sin saturar a los proveedores (cada provider ya
    tiene su propio rate limiter interno). Setear ``workers=1`` para
    el comportamiento serial original.

    ``limit`` — sólo las primeras N empresas (prueba). ``region`` —
    restringir a una región. ``progress`` — callback ``(hechas, total,
    mensaje)``; se llama desde el hilo principal a medida que cada
    futuro completa, así es seguro actualizar Streamlit desde acá.
    """
    universe = list(all_companies())
    if region:
        universe = [c for c in universe if c.region == region]
    if limit and limit > 0:
        universe = universe[:limit]

    total = len(universe)
    records: list[dict] = []
    ok = fail = skipped = 0

    def _ts() -> str:
        return datetime.now(timezone.utc).isoformat()

    # Pool paralelo. _record_safe nunca levanta, así que as_completed
    # siempre entrega un (rec, tag, msg) — no hay reintentos sucios.
    with ThreadPoolExecutor(max_workers=max(1, int(workers))) as pool:
        futures = {pool.submit(_record_safe, co): co for co in universe}
        for done, fut in enumerate(as_completed(futures), 1):
            rec, tag, msg = fut.result()
            if tag == "ok" and rec is not None:
                records.append(rec)
                ok += 1
            elif tag == "skipped":
                skipped += 1
            else:
                fail += 1
            if progress:
                progress(done, total, msg)
            # Flush parcial cada 25 — sobrevive una interrupción.
            if done % 25 == 0:
                write_snapshot(records, generated_utc=_ts())

    path = write_snapshot(records, generated_utc=_ts())
    return {
        "records":    records,
        "ok":         ok,
        "fail":       fail,
        "skipped":    skipped,
        "discounted": sum(1 for r in records if (r.get("upside_pct") or 0) > 0),
        "total":      total,
        "path":       str(path),
    }
