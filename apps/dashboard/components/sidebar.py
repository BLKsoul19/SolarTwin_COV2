"""Sidebar global: navegación, estado de API y contexto geográfico."""

from __future__ import annotations

import streamlit as st

from apps.dashboard.api_client import api_health
from apps.dashboard.config import NAVIGATION_PAGES


def render_sidebar() -> str:
    """Renderiza la barra lateral y devuelve la página seleccionada."""
    with st.sidebar:
        st.markdown(
            """
            <div style="padding: 8px 0 16px;">
                <div style="font-size:20px; font-weight:700; color:#7effd4; letter-spacing:-0.5px;">
                    ☀ SolarTwin CO
                </div>
                <div style="font-size:11px; color:#4a7a8a; margin-top:2px;">
                    v2.0 · Single Diode Model
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Estado de la API
        health = api_health()
        if health["ok"]:
            st.markdown(
                f'<span class="status-online">● API conectada</span> '
                f'<span style="font-size:11px;color:#7fa3bc;">({health["latency_ms"]:.0f} ms)</span>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<span class="status-offline">● API desconectada</span>',
                unsafe_allow_html=True,
            )
            st.caption(f"Error: {health.get('error', 'desconocido')[:60]}")

        st.markdown("---")

        # Navegación
        page = st.radio(
            "Sección",
            NAVIGATION_PAGES,
            label_visibility="collapsed",
        )

        st.markdown("---")

        # Contexto geográfico (sidebar info)
        st.markdown(
            """
            <div style="font-size:11px; color:#4a7a8a; line-height:1.7;">
                <div style="color:#7fa3bc; font-weight:600; margin-bottom:6px;">
                    📍 Manizales, Caldas
                </div>
                Lat 5°07'N · 2,154 m s.n.m.<br>
                T_amb: 15–26°C<br>
                G_solar: 1,450 kWh/m²/año<br>
                Nubosidad: 60–80%<br>
                Viento: 2–4 m/s
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.caption("SolarTwin CO · Sprint 2 · FastAPI + pvlib")

    return page
