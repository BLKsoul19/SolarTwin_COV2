"""Header global del dashboard."""

from __future__ import annotations

import streamlit as st


TITLES = {
    "🏠 General":       ("🏠 General", "Estado del gemelo digital y catálogo de paneles"),
    "⚡ Simulador I-V": ("⚡ Simulador I-V / P-V", "Single Diode Model · parámetros CEC/SAM"),
    "🔄 Comparador":    ("🔄 Comparador multi-panel", "Curvas P-V superpuestas y tabla de diferencias"),
    "🌡 Análisis NOCT": ("🌡 Modelo NOCT — Eje Cafetero", "Ross-NOCT aplicado al clima colombiano"),
}


def render_header(page: str) -> None:
    """Renderiza el encabezado correspondiente a la página activa."""
    title_main, title_sub = TITLES[page]

    st.markdown(
        f"""
        <div class="st-solar-header">
            <div>
                <h1>{title_main}</h1>
                <p>{title_sub}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
