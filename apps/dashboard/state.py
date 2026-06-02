"""Inicialización de estado de sesión del dashboard."""

from __future__ import annotations

import streamlit as st


def init_session_state() -> None:
    """Inicializa las claves compartidas de ``st.session_state``."""
    # Simulador reactivo (Mejora 1)
    if "sim_state" not in st.session_state:
        st.session_state.sim_state = {
            "g_poa": 1000,
            "t_cell": 25,
            "n_points": 100,
            "last_panel": None,
            "needs_update": True,
        }

    # Historial de simulaciones (Mejora 2)
    if "sim_history" not in st.session_state:
        st.session_state.sim_history = []

    # Favoritos de paneles (Mejora 3)
    if "fav_panels" not in st.session_state:
        st.session_state.fav_panels = []
