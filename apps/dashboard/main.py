"""
SolarTwin CO — Dashboard Streamlit
===================================
Gemelo digital de paneles fotovoltaicos · Eje Cafetero, Colombia.

Ejecución:
  uvicorn apps.api.main:app --reload --port 8000   # Terminal 1
  streamlit run apps/dashboard/main.py             # Terminal 2
"""

from __future__ import annotations

import streamlit as st

from apps.dashboard.components.header import render_header
from apps.dashboard.components.sidebar import render_sidebar
from apps.dashboard.config import (
    INITIAL_SIDEBAR_STATE,
    MENU_ITEMS,
    PAGE_ICON,
    PAGE_LAYOUT,
    PAGE_TITLE,
)
from apps.dashboard.pages.comparator import render_comparator
from apps.dashboard.pages.general import render_general
from apps.dashboard.pages.noct import render_noct
from apps.dashboard.pages.simulator import render_simulator
from apps.dashboard.state import init_session_state
from apps.dashboard.styles import inject_global_styles


PAGE_RENDERERS = {
    "🏠 General": render_general,
    "⚡ Simulador I-V": render_simulator,
    "🔄 Comparador": render_comparator,
    "🌡 Análisis NOCT": render_noct,
}


def main() -> None:
    """Punto de entrada Streamlit del dashboard modular."""
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout=PAGE_LAYOUT,
        initial_sidebar_state=INITIAL_SIDEBAR_STATE,
        menu_items=MENU_ITEMS,
    )
    init_session_state()
    inject_global_styles()
    page = render_sidebar()
    render_header(page)
    PAGE_RENDERERS[page]()

if __name__ == "__main__":
    main()