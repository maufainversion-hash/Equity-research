"""Smoke tests — every UI module imports, every page parses.

Guards against the failure class that has bitten this app before: a
module that exists on disk but breaks at *import time* — a missing
dependency, a bad relative import, a syntax error from a careless
edit. That breakage is invisible until the page needing the module is
opened (and on Streamlit Cloud, until the deploy boots).

- ui/components and ui/charts modules only define functions on import,
  so they can be imported directly.
- pages/*.py execute Streamlit calls at import time, so they can't be
  imported in a bare test — an AST parse catches syntax-level breakage.
"""
from __future__ import annotations
import ast
import importlib
from pathlib import Path

import pytest

_EQUITY_APP = Path(__file__).resolve().parent.parent


def _discover_modules(*subdirs: str) -> list[str]:
    """Dotted module paths for every non-dunder .py under each subdir."""
    mods: list[str] = []
    for sub in subdirs:
        d = _EQUITY_APP / sub
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.py")):
            if p.stem == "__init__":
                continue
            mods.append(f"{sub.replace('/', '.')}.{p.stem}")
    return mods


_UI_MODULES = _discover_modules("ui/components", "ui/charts")


@pytest.mark.parametrize("module", _UI_MODULES)
def test_ui_module_imports(module: str) -> None:
    """Every ui/components and ui/charts module imports without error."""
    importlib.import_module(module)


def _page_files() -> list[Path]:
    pages = _EQUITY_APP / "pages"
    return sorted(pages.glob("*.py")) if pages.is_dir() else []


@pytest.mark.parametrize("page", _page_files(), ids=lambda p: p.name)
def test_page_file_parses(page: Path) -> None:
    """Every Streamlit page file is syntactically valid."""
    ast.parse(page.read_text(encoding="utf-8"))


def test_app_entrypoint_parses() -> None:
    """The app.py entrypoint is syntactically valid."""
    ast.parse((_EQUITY_APP / "app.py").read_text(encoding="utf-8"))


def test_ui_module_discovery_nonempty() -> None:
    """Sanity: discovery actually found the UI modules (guards against
    a silently-empty parametrization making the suite look green)."""
    assert len(_UI_MODULES) > 50
