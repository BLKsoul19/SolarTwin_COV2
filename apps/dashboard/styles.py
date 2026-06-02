"""Estilos globales embebidos del dashboard."""

from __future__ import annotations

import streamlit as st


def inject_global_styles() -> None:
    """Inyecta el CSS global de SolarTwin en la página actual."""
    st.markdown(
        """
        <style>
        /* ── Fuente y fondo ── */
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* ── Sidebar ── */
        section[data-testid="stSidebar"] {
            background: #0d1f2d;
            border-right: 1px solid #1a3448;
        }
        section[data-testid="stSidebar"] * {
            color: #c8d8e4 !important;
        }
        section[data-testid="stSidebar"] .stSelectbox label,
        section[data-testid="stSidebar"] .stSlider label,
        section[data-testid="stSidebar"] .stNumberInput label {
            color: #7fa3bc !important;
            font-size: 12px !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        section[data-testid="stSidebar"] hr {
            border-color: #1a3448 !important;
        }

        /* ── Header principal ── */
        .st-solar-header {
            background: linear-gradient(135deg, #0d1f2d 0%, #0f3d2e 100%);
            border-radius: 12px;
            padding: 24px 32px;
            margin-bottom: 24px;
            display: flex;
            align-items: center;
            gap: 16px;
        }
        .st-solar-header h1 {
            color: #fff !important;
            font-size: 26px !important;
            font-weight: 600 !important;
            margin: 0 !important;
            letter-spacing: -0.3px;
        }
        .st-solar-header p {
            color: #7fa3bc !important;
            font-size: 13px !important;
            margin: 4px 0 0 0 !important;
        }

        /* ── KPI Cards ── */
        .kpi-card {
            background: #fff;
            border: 1px solid #e8e6e0;
            border-radius: 10px;
            padding: 16px 20px;
            text-align: center;
        }
        .kpi-label {
            font-size: 11px;
            color: #888780;
            text-transform: uppercase;
            letter-spacing: 0.6px;
            margin-bottom: 6px;
        }
        .kpi-value {
            font-size: 28px;
            font-weight: 600;
            line-height: 1.1;
        }
        .kpi-sub {
            font-size: 11px;
            color: #aaa;
            margin-top: 3px;
        }

        /* ── Panel badges ── */
        .badge-tier1 {
            background: #E1F5EE; color: #085041;
            padding: 2px 8px; border-radius: 10px;
            font-size: 11px; font-weight: 600;
        }
        .badge-topcon {
            background: #E6F1FB; color: #0C447C;
            padding: 2px 8px; border-radius: 10px;
            font-size: 11px;
        }
        .badge-hpbc {
            background: #EEEDFE; color: #3C3489;
            padding: 2px 8px; border-radius: 10px;
            font-size: 11px;
        }
        .badge-poly {
            background: #FAEEDA; color: #633806;
            padding: 2px 8px; border-radius: 10px;
            font-size: 11px;
        }

        /* ── Métricas resultado ── */
        div[data-testid="stMetric"] {
            background: #f8f7f4;
            border-radius: 8px;
            padding: 12px 16px;
            border: 1px solid #e8e6e0;
        }
        div[data-testid="stMetric"] label {
            font-size: 11px !important;
            color: #888780 !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
            font-size: 22px !important;
            font-weight: 600 !important;
        }

        /* ── Separadores y secciones ── */
        .section-title {
            font-size: 13px;
            font-weight: 600;
            color: #444441;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            margin: 20px 0 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .section-title::after {
            content: '';
            flex: 1;
            height: 1px;
            background: #e8e6e0;
        }

        /* ── Fórmula NOCT ── */
        .noct-formula {
            background: #0d1f2d;
            color: #7effd4;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 13px;
            border-radius: 8px;
            padding: 14px 20px;
            margin: 12px 0;
            letter-spacing: 0.2px;
        }

        /* ── Status online/offline ── */
        .status-online  { color: #1D9E75; font-weight: 600; font-size: 12px; }
        .status-offline { color: #D85A30; font-weight: 600; font-size: 12px; }

        /* ── Esconder elementos Streamlit por defecto ── */
        #MainMenu, footer { visibility: hidden; }
        .block-container { padding-top: 1rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )
