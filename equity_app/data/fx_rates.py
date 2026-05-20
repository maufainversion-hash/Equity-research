"""
Tipos de cambio ARS/USD — base para CEDEARs y equities argentinas.

Fuente: dolarapi.com (``/v1/dolares``) — API pública, sin key. Expone
oficial, blue, MEP (``bolsa``), CCL (``contadoconliqui``), mayorista,
cripto y tarjeta, con actualización intradía.

Para CEDEARs el tipo de cambio relevante es el CCL / MEP: el CEDEAR
cotiza en pesos y su arbitraje contra el subyacente estadounidense
define el dólar implícito de la operación.

Todas las funciones degradan a ``{}`` / ``None`` ante un fallo de red
— nunca levantan excepción al caller.
"""
from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Optional

import streamlit as st

log = logging.getLogger(__name__)

_DOLARAPI_URL = "https://dolarapi.com/v1/dolares"

# ``casa`` de dolarapi → clave canónica usada en el app.
_CASA_MAP = {
    "oficial":         "oficial",
    "blue":            "blue",
    "bolsa":           "mep",     # dólar MEP / Bolsa
    "contadoconliqui": "ccl",     # contado con liquidación
    "mayorista":       "mayorista",
    "cripto":          "cripto",
    "tarjeta":         "tarjeta",
}


@dataclass
class FXRate:
    """Una cotización ARS/USD."""
    kind:        str                  # oficial / blue / mep / ccl / ...
    nombre:      str
    compra:      Optional[float]
    venta:       Optional[float]
    actualizado: Optional[str] = None

    @property
    def mid(self) -> Optional[float]:
        """Punto medio compra/venta; cae a venta o compra si falta uno."""
        if self.compra and self.venta:
            return (self.compra + self.venta) / 2.0
        return self.venta or self.compra


def _to_float(v: object) -> Optional[float]:
    try:
        return float(v) if v is not None else None  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


@st.cache_data(ttl=900, show_spinner=False)
def fetch_ars_usd_rates() -> dict[str, FXRate]:
    """Cotizaciones ARS/USD vigentes, indexadas por clave canónica.

    Devuelve ``{"oficial": FXRate, "blue": FXRate, "mep": FXRate,
    "ccl": FXRate, ...}``. Diccionario vacío ante cualquier fallo —
    el caller decide cómo degradar."""
    try:
        import requests  # import diferido — entornos sin red / sin la lib
    except ImportError:
        return {}
    try:
        r = requests.get(_DOLARAPI_URL, timeout=12)
    except Exception as e:
        log.warning("dolarapi request failed: %s", e)
        return {}
    if r.status_code != 200:
        log.warning("dolarapi returned HTTP %s", r.status_code)
        return {}
    try:
        payload = r.json()
    except ValueError:
        return {}
    if not isinstance(payload, list):
        return {}

    out: dict[str, FXRate] = {}
    for row in payload:
        if not isinstance(row, dict):
            continue
        casa = str(row.get("casa", "")).lower()
        kind = _CASA_MAP.get(casa)
        if kind is None:
            continue
        out[kind] = FXRate(
            kind=kind,
            nombre=str(row.get("nombre") or kind.upper()),
            compra=_to_float(row.get("compra")),
            venta=_to_float(row.get("venta")),
            actualizado=row.get("fechaActualizacion"),
        )
    return out


def get_rate(kind: str = "ccl") -> Optional[float]:
    """Punto medio del tipo de cambio ``kind`` (default CCL — el
    relevante para CEDEARs). ``None`` si no se pudo resolver."""
    rates = fetch_ars_usd_rates()
    fx = rates.get(kind)
    return fx.mid if fx is not None else None


def get_ccl_rate() -> Optional[float]:
    """Dólar CCL (contado con liquidación) — el tipo de cambio implícito
    en el arbitraje de CEDEARs y ADRs."""
    return get_rate("ccl")


def get_mep_rate() -> Optional[float]:
    """Dólar MEP / Bolsa."""
    return get_rate("mep")


def is_available() -> bool:
    """True si dolarapi respondió con al menos una cotización."""
    return bool(fetch_ars_usd_rates())
