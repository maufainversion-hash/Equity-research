"""
Combine intrinsic-value estimates (DCF, comparables, MC, DDM, RI, EPV,
Multiples) into a single point estimate, a (low, high) range, an
inter-quartile range (p25, p75), and a confidence flag.

Each model contributes its per-share intrinsic value. Profile-specific
weights from :data:`PROFILE_WEIGHTS` decide how heavily to load each.
Models that failed (returned None) get their weight redistributed
across survivors.

Sanity clip is *asymmetric and profile-aware* (see
:data:`PROFILE_CLIP_CONFIG`):

- For growth profiles (young/high/mature_growth) the **below** bound
  is loose or disabled — models legitimately produce values far below
  price because LTM cash flows do not capture the growth that the
  market is paying for. Penalising those would force the aggregator
  to invent an absurd "SELL" verdict for every growth stock.
- For mature/cyclical/declining profiles both bounds are tight —
  there's no reason a well-applied DCF on a stable business should
  diverge from price by more than ~60%; if it does, the model is
  likely misapplied.

When ≥ half of the surviving models for a growth profile get clipped
above the upper bound (i.e. the market is paying multiples that no
traditional model can justify on current fundamentals), the
aggregator returns ``not_applicable=True``. The downstream rater
then emits a "N/A" verdict instead of a mechanical SELL — the
correct read is "use the reverse-DCF implied growth as the headline",
not "the stock is overvalued by 90%".
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from core.constants import RATING_THRESHOLDS


# ============================================================
# Profile → model weights
# ============================================================
PROFILE_WEIGHTS: dict[str, dict[str, float]] = {
    # ---- Damodaran lifecycle stages ----
    "mature_stable": {
        "epv": 0.35, "multiples": 0.30, "dcf": 0.15,
        "comps": 0.10, "ddm": 0.05, "monte_carlo": 0.05, "ri": 0.0,
    },
    "mature_growth": {
        "dcf": 0.30, "multiples": 0.30, "epv": 0.20,
        "comps": 0.10, "monte_carlo": 0.05, "ddm": 0.05, "ri": 0.0,
    },
    "high_growth": {
        "dcf": 0.40, "multiples": 0.25, "comps": 0.15,
        "monte_carlo": 0.10, "epv": 0.10, "ddm": 0.0, "ri": 0.0,
    },
    "young_growth": {
        "dcf": 0.45, "multiples": 0.25, "monte_carlo": 0.15,
        "comps": 0.10, "epv": 0.05, "ddm": 0.0, "ri": 0.0,
    },
    "cyclical": {
        "epv": 0.35, "multiples": 0.30, "dcf": 0.15,
        "comps": 0.10, "monte_carlo": 0.10, "ddm": 0.0, "ri": 0.0,
    },
    "declining": {
        "epv": 0.40, "multiples": 0.25, "comps": 0.20,
        "dcf": 0.10, "monte_carlo": 0.05, "ddm": 0.0, "ri": 0.0,
    },
    # ---- Business-profile overrides (financial sector) ----
    "bank": {
        "ri": 0.45, "ddm": 0.30, "multiples": 0.20, "comps": 0.05,
        "dcf": 0.0, "epv": 0.0, "monte_carlo": 0.0,
    },
    "insurance": {
        "ri": 0.45, "ddm": 0.30, "multiples": 0.20, "comps": 0.05,
        "dcf": 0.0, "epv": 0.0, "monte_carlo": 0.0,
    },
    "reit": {
        "ddm": 0.50, "multiples": 0.30, "comps": 0.15, "epv": 0.05,
        "dcf": 0.0, "monte_carlo": 0.0, "ri": 0.0,
    },
    # ---- Legacy keys (back-compat for callers still using business-profile names) ----
    "steady_compounder": {
        "dcf": 0.15, "epv": 0.40, "multiples": 0.35,
        "comps": 0.05, "ddm": 0.05, "ri": 0.0, "monte_carlo": 0.0,
    },
    "growth_tech": {
        "dcf": 0.30, "epv": 0.15, "multiples": 0.30,
        "comps": 0.10, "monte_carlo": 0.10, "ddm": 0.0, "ri": 0.05,
    },
    "dividend_payer": {
        "ddm": 0.30, "epv": 0.25, "multiples": 0.25,
        "dcf": 0.10, "comps": 0.10, "monte_carlo": 0.0, "ri": 0.0,
    },
    "default": {
        "dcf": 0.20, "epv": 0.25, "multiples": 0.25, "comps": 0.10,
        "monte_carlo": 0.10, "ddm": 0.05, "ri": 0.05,
    },
}


# ============================================================
# Profile → (above_threshold, below_threshold) for sanity clip
# ============================================================
# Asymmetric clip: how far above price (above) and below price (below)
# a model can fall before being penalised. ``None`` disables that side.
#
# Rationale by profile:
# - young_growth / high_growth: cash-flow models *will* give values
#   far below price (the market discounts growth they can't see).
#   Disable the below side entirely; only clip extreme upside outliers.
# - mature_growth: still some growth premium expected — loose both
#   sides, but keep them.
# - mature_stable / cyclical / declining: any large gap is a sign of
#   model misapplication, not real mispricing — tight clip.
# - bank / insurance / reit: specialised models (RI/DDM); other models
#   are noise. Strict clip prevents non-applicable models from
#   contributing.
# - default: 0.60 symmetric (back-compat with prior fixed behavior).
PROFILE_CLIP_CONFIG: dict[str, tuple[Optional[float], Optional[float]]] = {
    "young_growth":    (2.00, None),
    "high_growth":     (1.50, None),
    "mature_growth":   (0.85, 0.85),
    "mature_stable":   (0.60, 0.60),
    "cyclical":        (0.60, 0.60),
    "declining":       (0.60, 0.60),
    "bank":            (0.50, 0.50),
    "insurance":       (0.50, 0.50),
    "reit":            (0.50, 0.50),
    # legacy keys
    "growth_tech":     (1.50, None),
    "steady_compounder": (0.60, 0.60),
    "dividend_payer":  (0.60, 0.60),
    "default":         (0.60, 0.60),
}

# Profiles where "models priced way below market" is expected behavior
# (growth premium not captured by LTM cash-flow models). When ≥ half
# of survivors get clipped *above* on one of these, the verdict is N/A.
_GROWTH_PROFILES = frozenset({"young_growth", "high_growth", "growth_tech"})


# ============================================================
# Result dataclass
# ============================================================
@dataclass
class AggregatedValuation:
    intrinsic_per_share: float
    range_low: float                              # back-compat: cv-scaled band
    range_high: float
    range_p25: float                              # inter-quartile across surviving models
    range_p75: float
    weights_used: dict[str, float]
    contributions: dict[str, float]               # value x weight per model
    raw_estimates: dict[str, float] = field(default_factory=dict)
    clipped_models: list[str] = field(default_factory=list)
    dispersion_cv: float = 0.0                    # coefficient of variation
    confidence: str = "high"                      # high | medium | low
    profile: str = "default"
    n_models_used: int = 0
    # ---- Koller decomposition ----
    # DCF - EPV (per share). Positive => market is paying for growth on
    # top of asset-in-place earnings; negative => DCF is below the
    # no-growth floor (a red flag for the DCF assumptions).
    value_of_growth_premium: Optional[float] = None
    # Cyclical normalization signal: "above_cycle" | "at_cycle" | "below_cycle"
    # — derived from EPV's normalization_factor (current_nopat / normalized).
    normalization_signal: Optional[str] = None
    # ---- Applicability flag ----
    # True when ≥ half of surviving growth-profile models get clipped
    # above the upper bound — i.e. the market is paying multiples no
    # cash-flow model can justify. The rating layer reads this and
    # emits "N/A" instead of a mechanical SELL.
    not_applicable: bool = False
    # Human-readable explanation of the verdict / applicability call.
    # Empty string when there is nothing notable to say.
    applicability_note: str = ""


# ============================================================
# Public API
# ============================================================
def aggregate(
    *,
    dcf: Optional[float] = None,
    comparables: Optional[float] = None,
    monte_carlo: Optional[float] = None,
    ddm: Optional[float] = None,
    residual_income: Optional[float] = None,
    epv: Optional[float] = None,
    multiples: Optional[float] = None,
    profile: Optional[str] = None,
    current_price: Optional[float] = None,
    sector: Optional[str] = None,               # kept for back-compat; ignored when profile set
    range_band: float = 0.20,
    sanity_clip_threshold: float = 0.60,
    epv_normalization_factor: Optional[float] = None,
) -> AggregatedValuation:
    """Combine the per-share intrinsic values into one aggregated result.

    Args:
      profile: One of the keys in :data:`PROFILE_WEIGHTS`. Falls back to
               "default" when None or unknown. Replaces the old sector
               argument (still accepted but unused — callers should
               migrate to passing profile explicitly).
      current_price: Used for sanity-clipping wildly off models. When
               omitted, no clipping is applied (back-compat path).
      sanity_clip_threshold: Fractional gap above which a model's
               weight is reduced 70% (e.g. 0.60 ⇒ a model whose output
               is <40% or >160% of the current price is penalised).
    """
    profile_key = profile if (profile and profile in PROFILE_WEIGHTS) else "default"
    base_weights = PROFILE_WEIGHTS[profile_key]

    raw = {
        "dcf": dcf, "comps": comparables, "monte_carlo": monte_carlo,
        "ddm": ddm, "ri": residual_income,
        "epv": epv, "multiples": multiples,
    }
    survivors = {k: float(v) for k, v in raw.items()
                 if v is not None and np.isfinite(v) and v > 0}
    # raw_estimates surfaces everything that came in finite + positive so
    # the UI can render the per-model breakdown including clipped ones.
    raw_estimates = dict(survivors)

    if not survivors:
        return AggregatedValuation(
            intrinsic_per_share=float("nan"),
            range_low=float("nan"), range_high=float("nan"),
            range_p25=float("nan"), range_p75=float("nan"),
            weights_used={}, contributions={}, raw_estimates={},
            clipped_models=[],
            confidence="low", profile=profile_key, n_models_used=0,
        )

    # ---- Sanity clip (asymmetric + profile-aware) ----
    # Resolve (above, below) bounds: prefer profile config; fall back to
    # the legacy fixed ``sanity_clip_threshold`` if profile is unknown.
    above_thr, below_thr = PROFILE_CLIP_CONFIG.get(
        profile_key, (sanity_clip_threshold, sanity_clip_threshold))

    clipped_set: set[str] = set()
    clipped_above: set[str] = set()
    if current_price is not None and np.isfinite(current_price) and current_price > 0:
        hi_bound = (current_price * (1.0 + above_thr)
                    if above_thr is not None else float("inf"))
        lo_bound = (current_price * max(0.0, 1.0 - below_thr)
                    if below_thr is not None else 0.0)
        for k, v in survivors.items():
            if v > hi_bound:
                clipped_set.add(k)
                clipped_above.add(k)
            elif v < lo_bound:
                clipped_set.add(k)
        sane = {k: v for k, v in survivors.items() if k not in clipped_set}
        # Fallback: if clipping leaves <2 sane models, include the clipped
        # ones too but they'll be penalised in the weight stage.
        if len(sane) < 2:
            sane = dict(survivors)
        usable = sane
    else:
        usable = dict(survivors)

    # ---- Applicability flag ----
    # The same underlying problem (cash-flow models can't justify a
    # growth stock's price) can show up two ways:
    #   (a) Models clip *above* the price (rare — when the model
    #       happens to compute a value 1.5x+ price).
    #   (b) Models cluster far *below* the price (PLTR-style: 5 of 5
    #       give ~$10 against a $137 print). Asymmetric clip lets them
    #       survive — but the resulting intrinsic is meaningless.
    # In either case the mechanical verdict would be a wrong SELL/N/A
    # is the correct read.
    not_applicable = False
    applicability_note = ""
    if profile_key in _GROWTH_PROFILES and len(survivors) >= 2:
        trigger_above = len(clipped_above) >= max(2, len(survivors) // 2)
        trigger_below = False
        if (current_price is not None and np.isfinite(current_price)
                and current_price > 0):
            below_thr_px = current_price * 0.50          # < half of price
            n_below = sum(1 for v in survivors.values() if v < below_thr_px)
            # ⅔ of surviving classical models give << price → the cluster
            # is signal, not noise from a single broken model.
            trigger_below = n_below >= max(2, (len(survivors) * 2) // 3)
        if trigger_above or trigger_below:
            not_applicable = True
            applicability_note = (
                f"Modelos clásicos no aplicables al perfil "
                f"{profile_key}: el mercado descuenta crecimiento "
                f"que los flujos actuales no capturan. La lectura "
                f"central es el implied growth del reverse-DCF, no "
                f"el intrinsic mecánico."
            )

    # ---- Weights ----
    raw_w = {k: base_weights.get(k, 0.0) for k in usable}
    # Penalise clipped models that still made it into the usable set
    # (only happens in the <2 sane fallback).
    for k in list(raw_w):
        if k in clipped_set:
            raw_w[k] *= 0.3
    total = sum(raw_w.values())
    if total <= 0:
        raw_w = {k: 1.0 for k in usable}
        total = float(len(usable))
    weights = {k: raw_w[k] / total for k in usable}

    contribs = {k: weights[k] * usable[k] for k in usable}
    intrinsic = float(sum(contribs.values()))

    # ---- Inter-quartile range across surviving models ----
    if len(usable) >= 2:
        values = np.array(list(usable.values()), dtype=float)
        range_p25 = float(np.percentile(values, 25))
        range_p75 = float(np.percentile(values, 75))
    else:
        range_p25 = intrinsic * 0.85
        range_p75 = intrinsic * 1.15

    # ---- CV-scaled band (back-compat range_low / range_high) ----
    cv_values = np.array(list(usable.values()), dtype=float)
    cv = float(cv_values.std(ddof=0) / cv_values.mean()) if cv_values.mean() > 0 else 0.0

    threshold = float(RATING_THRESHOLDS["low_confidence_dispersion"])
    if cv >= threshold:
        confidence = "low"
    elif cv >= threshold / 2:
        confidence = "medium"
    else:
        confidence = "high"

    band = float(np.clip(range_band * (1.0 + cv), 0.05, 0.50))
    low = intrinsic * (1.0 - band)
    high = intrinsic * (1.0 + band)

    # ---- Koller decomposition: DCF - EPV per share ----
    # Use the *survivor* values so a clipped DCF or EPV doesn't poison
    # the signal — when either is None or non-positive, leave the field
    # as None so the UI can show "n/a".
    dcf_val = survivors.get("dcf")
    epv_val = survivors.get("epv")
    value_of_growth_premium: Optional[float] = None
    if dcf_val is not None and epv_val is not None:
        value_of_growth_premium = float(dcf_val - epv_val)

    # ---- Cyclical normalization signal ----
    normalization_signal: Optional[str] = None
    if (epv_normalization_factor is not None
            and np.isfinite(epv_normalization_factor)):
        # current_nopat / nopat_normalized: > 1.15 => peak; < 0.85 => trough.
        if epv_normalization_factor > 1.15:
            normalization_signal = "above_cycle"
        elif epv_normalization_factor < 0.85:
            normalization_signal = "below_cycle"
        else:
            normalization_signal = "at_cycle"

    return AggregatedValuation(
        intrinsic_per_share=intrinsic,
        range_low=float(low),
        range_high=float(high),
        range_p25=float(range_p25),
        range_p75=float(range_p75),
        weights_used=weights,
        contributions=contribs,
        raw_estimates=raw_estimates,
        clipped_models=sorted(clipped_set),
        dispersion_cv=float(cv),
        confidence=confidence,
        profile=profile_key,
        n_models_used=len(usable),
        value_of_growth_premium=value_of_growth_premium,
        normalization_signal=normalization_signal,
        not_applicable=not_applicable,
        applicability_note=applicability_note,
    )
