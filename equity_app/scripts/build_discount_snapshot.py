#!/usr/bin/env python3
"""
CLI del builder del snapshot de valuación.

Envoltorio fino de :func:`analysis.discount_builder.build_snapshot` — la
lógica vive ahí y la comparte el botón "Actualizar datos" del app.

Uso
---
    python scripts/build_discount_snapshot.py            # todo el catálogo
    python scripts/build_discount_snapshot.py --limit 20 # prueba rápida
    python scripts/build_discount_snapshot.py --region "Latin America"
"""
from __future__ import annotations
import argparse
import sys
import time
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

# El script vive en equity_app/scripts/ — sumar equity_app al path.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analysis.discount_builder import build_snapshot              # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--limit", type=int, default=0,
                    help="Valuar sólo las primeras N empresas (prueba).")
    ap.add_argument("--region", type=str, default=None,
                    help="Restringir a una región del catálogo.")
    args = ap.parse_args()

    print("Valuando el catálogo… (lento — un análisis por empresa)")
    t0 = time.time()

    def _prog(done: int, total: int, msg: str) -> None:
        print(f"  [{done}/{total}] {msg}")

    res = build_snapshot(limit=args.limit, region=args.region, progress=_prog)

    print(f"\nListo en {(time.time() - t0) / 60:.1f} min — {res['ok']} "
          f"valuadas, {res['fail']} sin datos, {res['skipped']} omitidas "
          f"por alta inflación.")
    print(f"{res['discounted']} en descuento. Snapshot escrito en {res['path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
