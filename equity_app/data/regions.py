"""
Regiones de mercado — capa de compatibilidad sobre ``company_catalog``.

El universo curado vive ahora en :mod:`data.company_catalog`, con cada
empresa etiquetada por país y sector. Este módulo conserva la API por
región (``region_names`` / ``universe_for`` / ``region_of``) que usa el
selector de la página de Equity Analysis, delegando todo al catálogo.

El selector en cascada de la pantalla de búsqueda (País → Sector →
Empresa) consume ``company_catalog`` directamente.
"""
from __future__ import annotations

from data.company_catalog import (
    regions as _regions,
    region_of_ticker as _region_of_ticker,
    universe_by_region as _universe_by_region,
)


def region_names() -> list[str]:
    """Nombres de región en orden de display."""
    return _regions()


def universe_for(region: str) -> dict[str, str]:
    """Universo ``{ticker: nombre}`` de la región. North America ante un
    nombre desconocido (fallback seguro)."""
    uni = _universe_by_region(region)
    return uni if uni else _universe_by_region("North America")


def region_of(ticker: str) -> str:
    """Región a la que pertenece ``ticker`` — para inicializar el
    selector en la región del ticker activo."""
    return _region_of_ticker(ticker)
