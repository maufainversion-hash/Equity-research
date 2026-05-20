"""
Snapshot de valuación del catálogo — IO compartido.

La página *Discount* necesita el valor intrínseco de cientos de
empresas. Correr el pipeline en vivo para todas dispararía miles de
llamadas API, así que se precalcula un snapshot offline con
``scripts/build_discount_snapshot.py`` y la página sólo lo lee.

Este módulo es la fuente única de la ruta del snapshot y de su
esquema, para que el script (escritor) y la página (lector) no se
desincronicen.
"""
from __future__ import annotations
import json
import logging
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

# El snapshot vive junto al catálogo, dentro del paquete ``data``.
SNAPSHOT_PATH = Path(__file__).resolve().parent / "discount_snapshot.json"

# Versión del esquema — si cambia la forma de cada registro, subir esto
# para que un snapshot viejo se considere obsoleto.
SCHEMA_VERSION = 1


def load_snapshot(path: Path | None = None) -> dict[str, Any]:
    """Carga el snapshot. Devuelve ``{}`` si no existe o está corrupto —
    la página entonces muestra un mensaje para correr el script."""
    p = path or SNAPSHOT_PATH
    if not p.exists():
        return {}
    try:
        with p.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, dict) or "companies" not in data:
            return {}
        return data
    except Exception as e:                      # JSON corrupto / IO
        log.warning("discount snapshot unreadable: %s", e)
        return {}


def write_snapshot(companies: list[dict[str, Any]], *,
                   generated_utc: str, path: Path | None = None) -> Path:
    """Escribe el snapshot a disco. Usado por el script de build."""
    p = path or SNAPSHOT_PATH
    payload = {
        "schema_version": SCHEMA_VERSION,
        "generated_utc": generated_utc,
        "n_companies": len(companies),
        "companies": companies,
    }
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    return p
