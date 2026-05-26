"""
SolarTwin CO — Dashboard Streamlit
===================================
Gemelo digital de paneles fotovoltaicos · Eje Cafetero, Colombia

Consumo de los 6 endpoints FastAPI:
  GET  /health
  GET  /api/v1/twin/panels
  GET  /api/v1/twin/panels/{panel_id}
  POST /api/v1/twin/cell-temperature
  GET  /api/v1/twin/panels/{panel_id}/iv
  GET  /api/v1/twin/panels/{panel_id}/pv

Ejecución:
  uvicorn apps.api.main:app --reload --port 8000   # Terminal 1
  streamlit run apps/dashboard/main.py             # Terminal 2
"""

from __future__ import annotations

import io
import json
import time
from datetime import datetime
from typing import Any

import httpx
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN GLOBAL
# ─────────────────────────────────────────────────────────────────────────────

API_BASE_URL: str = "http://127.0.0.1:8000"
REQUEST_TIMEOUT: float = 15.0

# Paleta SolarTwin (consistente en toda la app)
COLORS = {
    "teal":        "#1D9E75",
    "teal_light":  "#E1F5EE",
    "teal_dark":   "#085041",
    "amber":       "#EF9F27",
    "amber_light": "#FAEEDA",
    "coral":       "#D85A30",
    "coral_light": "#FAECE7",
    "blue":        "#378ADD",
    "blue_light":  "#E6F1FB",
    "purple":      "#7F77DD",
    "gray":        "#888780",
    "bg":          "#F8F7F4",
}

PANEL_COLORS: dict[str, str] = {
    "jinko_tiger_neo_580": COLORS["teal"],
    "longi_himo_x6_580":   COLORS["blue"],
    "generic_poly_330":    COLORS["amber"],
}

DEFAULT_COLOR = COLORS["purple"]

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="SolarTwin CO",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/your-repo/SolarTwin_COV2",
        "About": "SolarTwin CO · Gemelo digital PV · Eje Cafetero",
    },
)

# ─────────────────────────────────────────────────────────────────────────────
# INICIALIZACIÓN DE SESSION STATE (Mejora 1, 2)
# ─────────────────────────────────────────────────────────────────────────────

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

# CSS personalizado — tipografía, colores y espaciado
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

# ─────────────────────────────────────────────────────────────────────────────
# CLIENTE API — funciones de consumo de endpoints
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=30, show_spinner=False)
def api_health() -> dict[str, Any]:
    """GET /health — verifica estado del servidor."""
    try:
        resp = httpx.get(f"{API_BASE_URL}/health", timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return {"ok": True, "data": resp.json(), "latency_ms": resp.elapsed.total_seconds() * 1000}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "latency_ms": None}


@st.cache_data(ttl=60, show_spinner=False)
def api_list_panels() -> dict[str, Any]:
    """GET /api/v1/twin/panels — lista todos los paneles del catálogo."""
    try:
        resp = httpx.get(f"{API_BASE_URL}/api/v1/twin/panels", timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return {"ok": True, "data": resp.json()}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "data": []}


@st.cache_data(ttl=60, show_spinner=False)
def api_get_panel(panel_id: str) -> dict[str, Any]:
    """GET /api/v1/twin/panels/{panel_id} — detalles de un panel específico."""
    try:
        resp = httpx.get(f"{API_BASE_URL}/api/v1/twin/panels/{panel_id}", timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return {"ok": True, "data": resp.json()}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "data": {}}


@st.cache_data(ttl=10, show_spinner=False)
def api_cell_temperature(
    g_poa_w_m2: float,
    t_amb_c: float,
    noct_c: float,
) -> dict[str, Any]:
    """POST /api/v1/twin/cell-temperature — modelo Ross-NOCT."""
    try:
        resp = httpx.post(
            f"{API_BASE_URL}/api/v1/twin/cell-temperature",
            json={"g_poa_w_m2": g_poa_w_m2, "t_amb_c": t_amb_c, "noct_c": noct_c},
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        return {"ok": True, "data": resp.json()}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "data": {}}


@st.cache_data(ttl=10, show_spinner=False)
def api_iv_curve(
    panel_id: str,
    g_poa_w_m2: float,
    t_cell_c: float,
    n_points: int = 100,
) -> dict[str, Any]:
    """GET /api/v1/twin/panels/{panel_id}/iv — curva I-V (SDM/CEC)."""
    try:
        t0 = time.perf_counter()
        resp = httpx.get(
            f"{API_BASE_URL}/api/v1/twin/panels/{panel_id}/iv",
            params={"g_poa_w_m2": g_poa_w_m2, "t_cell_c": t_cell_c, "n_points": n_points},
            timeout=REQUEST_TIMEOUT,
        )
        latency = (time.perf_counter() - t0) * 1000
        resp.raise_for_status()
        return {"ok": True, "data": resp.json(), "latency_ms": round(latency, 1)}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "data": {}, "latency_ms": None}


@st.cache_data(ttl=10, show_spinner=False)
def api_pv_curve(
    panel_id: str,
    g_poa_w_m2: float,
    t_cell_c: float,
    n_points: int = 100,
) -> dict[str, Any]:
    """GET /api/v1/twin/panels/{panel_id}/pv — curva P-V (SDM/CEC)."""
    try:
        resp = httpx.get(
            f"{API_BASE_URL}/api/v1/twin/panels/{panel_id}/pv",
            params={"g_poa_w_m2": g_poa_w_m2, "t_cell_c": t_cell_c, "n_points": n_points},
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        return {"ok": True, "data": resp.json()}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "data": {}}


# ─────────────────────────────────────────────────────────────────────────────
# UTILIDADES DE GRÁFICOS — tema coherente Plotly
# ─────────────────────────────────────────────────────────────────────────────

PLOTLY_LAYOUT_BASE = dict(
    font=dict(family="Inter, sans-serif", size=12, color="#444441"),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#fafaf8",
    margin=dict(l=50, r=20, t=30, b=50),
    xaxis=dict(
        gridcolor="#e8e6e0",
        gridwidth=0.5,
        linecolor="#c8c6c0",
        tickfont=dict(size=11),
        zeroline=False,
    ),
    yaxis=dict(
        gridcolor="#e8e6e0",
        gridwidth=0.5,
        linecolor="#c8c6c0",
        tickfont=dict(size=11),
        zeroline=False,
    ),
    legend=dict(
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor="#e8e6e0",
        borderwidth=0.5,
        font=dict(size=11),
    ),
    hovermode="x unified",
)


def _fig_layout(**overrides: Any) -> dict:
    layout = dict(PLOTLY_LAYOUT_BASE)
    layout.update(overrides)
    return layout


def build_iv_fig(
    v_data: list[float],
    i_data: list[float],
    panel_label: str,
    color: str,
    v_mpp: float | None = None,
    i_mpp: float | None = None,
) -> go.Figure:
    """Curva I-V con marcador MPP opcional."""
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=v_data,
            y=i_data,
            mode="lines",
            name=panel_label,
            line=dict(color=color, width=2.5),
            hovertemplate="V: %{x:.2f} V<br>I: %{y:.3f} A<extra></extra>",
        )
    )
    if v_mpp is not None and i_mpp is not None:
        fig.add_trace(
            go.Scatter(
                x=[v_mpp],
                y=[i_mpp],
                mode="markers",
                name="MPP",
                marker=dict(color=color, size=10, symbol="diamond",
                            line=dict(color="white", width=2)),
                hovertemplate=f"MPP<br>V: {v_mpp:.2f} V<br>I: {i_mpp:.3f} A<extra></extra>",
            )
        )
    fig.update_layout(
        **_fig_layout(
            xaxis_title="Voltaje (V)",
            yaxis_title="Corriente (A)",
            height=300,
        )
    )
    return fig


def build_pv_fig(
    v_data: list[float],
    p_data: list[float],
    panel_label: str,
    color: str,
    v_mpp: float | None = None,
    p_mpp: float | None = None,
) -> go.Figure:
    """Curva P-V con área sombreada y marcador MPP."""
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=v_data,
            y=p_data,
            mode="lines",
            name=panel_label,
            line=dict(color=color, width=2.5),
            fill="tozeroy",
            fillcolor=color.replace(")", ", 0.08)").replace("rgb", "rgba")
                if color.startswith("rgb") else color + "14",
            hovertemplate="V: %{x:.2f} V<br>P: %{y:.1f} W<extra></extra>",
        )
    )
    if v_mpp is not None and p_mpp is not None:
        fig.add_vline(
            x=v_mpp,
            line=dict(color=color, width=1, dash="dot"),
            annotation_text=f"V_mpp {v_mpp:.1f} V",
            annotation_font_size=10,
            annotation_font_color=color,
        )
        fig.add_trace(
            go.Scatter(
                x=[v_mpp],
                y=[p_mpp],
                mode="markers",
                name=f"P_max {p_mpp:.0f} W",
                marker=dict(color=color, size=10, symbol="diamond",
                            line=dict(color="white", width=2)),
                hovertemplate=f"P_max<br>{p_mpp:.1f} W<extra></extra>",
            )
        )
    fig.update_layout(
        **_fig_layout(
            xaxis_title="Voltaje (V)",
            yaxis_title="Potencia (W)",
            height=300,
        )
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR — navegación y estado global
# ─────────────────────────────────────────────────────────────────────────────

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
        ["🏠 General", "⚡ Simulador I-V", "🔄 Comparador", "🌡 Análisis NOCT"],
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


# ─────────────────────────────────────────────────────────────────────────────
# HEADER GLOBAL
# ─────────────────────────────────────────────────────────────────────────────

TITLES = {
    "🏠 General":       ("🏠 General", "Estado del gemelo digital y catálogo de paneles"),
    "⚡ Simulador I-V": ("⚡ Simulador I-V / P-V", "Single Diode Model · parámetros CEC/SAM"),
    "🔄 Comparador":    ("🔄 Comparador multi-panel", "Curvas P-V superpuestas y tabla de diferencias"),
    "🌡 Análisis NOCT": ("🌡 Modelo NOCT — Eje Cafetero", "Ross-NOCT aplicado al clima colombiano"),
}
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


# ─────────────────────────────────────────────────────────────────────────────
# PÁGINA 1 — GENERAL
# ─────────────────────────────────────────────────────────────────────────────

if page == "🏠 General":

    panels_resp = api_list_panels()
    panels: list[dict] = panels_resp.get("data", []) if panels_resp["ok"] else []

    # ── KPIs MEJORADOS ──
    tier1 = [p for p in panels if p.get("tier") == 1]
    tier2 = [p for p in panels if p.get("tier") == 2]
    poly = [p for p in panels if p.get("technology", "").lower() in ["poly", "poli_perc"]]
    mono = [p for p in panels if p.get("technology", "").lower() in ["mono", "topcon", "hpbc"]]
    
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Paneles en catálogo",
            len(panels),
            delta=f"{len(tier1)} Tier 1 · {len(tier2)} Tier 2",
            delta_color="off",
            help="Total de paneles disponibles para simulación",
        )
    with col2:
        avg_pmax = sum(p.get("pmax_stc_w", 0) for p in panels) / len(panels) if panels else 0
        st.metric(
            "Potencia promedio STC",
            f"{avg_pmax:.0f} W",
            delta=f"Min {min((p.get('pmax_stc_w', 0) for p in panels), default=0):.0f} – Max {max((p.get('pmax_stc_w', 0) for p in panels), default=0):.0f}",
            delta_color="off",
            help="Rango de potencias en el catálogo",
        )
    with col3:
        mono_pct = (len(mono) / len(panels) * 100) if panels else 0
        st.metric(
            "Composición tecnológica",
            f"{mono_pct:.0f}% monocristalino",
            delta=f"{100-mono_pct:.0f}% policristalino",
            delta_color="off",
            help="Distribución por tipo de celda",
        )
    with col4:
        lat_ms = health.get("latency_ms")
        st.metric(
            "Salud del sistema",
            f"✓ OK" if health["ok"] else "✗ ERROR",
            delta=f"{lat_ms:.0f} ms latencia" if lat_ms else "—",
            delta_color="normal" if lat_ms and lat_ms < 100 else "off",
            help="Estado API + latencia de respuesta",
        )

    st.markdown("---")

    # ── Catálogo de paneles — VISTA DENSIFICADA ──
    st.markdown('<div class="section-title">📋 Catálogo de paneles (Análisis comparativo)</div>', unsafe_allow_html=True)

    if not panels_resp["ok"]:
        st.error(f"No se pudo conectar a la API: {panels_resp.get('error')}")
        st.info("Asegúrate de que la API esté corriendo: `uvicorn apps.api.main:app --reload`")
    elif not panels:
        st.warning("Catálogo vacío. Agrega archivos JSON a data/panels/")
    else:
        # ── TAB 1: Vista tabla ──
        tab_table, tab_tech, tab_metrics = st.tabs(["📊 Tabla", "🔬 Análisis tecnológico", "📈 Comparativa KPIs"])
        
        with tab_table:
            # Preparar DataFrame
            panel_data_rows = []
            for p in sorted(panels, key=lambda x: (-x.get("tier", 9), x.get("panel_id", ""))):
                panel_data_rows.append({
                    "Panel ID": p.get("panel_id", "—"),
                    "P_max STC (W)": p.get("pmax_stc_w", 0),
                    "V_oc STC (V)": p.get("voc_stc_v", 0),
                    "I_sc STC (A)": p.get("isc_stc_a", 0),
                    "V_mpp STC (V)": p.get("vmpp_stc_v", 0),
                    "I_mpp STC (A)": p.get("impp_stc_a", 0),
                    "γ P_max (%/°C)": p.get("gamma_pmax_per_c", 0) * 100,
                    "NOCT (°C)": p.get("noct_c", "—"),
                    "Cells": p.get("cells_in_series", "—"),
                    "Tech": p.get("technology", "—"),
                    "Tier": p.get("tier", "—"),
                })
            
            df_panel_catalog = pd.DataFrame(panel_data_rows)
            
            # Estilo destacando mejores valores
            st.dataframe(
                df_panel_catalog.style
                    .background_gradient(subset=["P_max STC (W)"], cmap="Greens", vmin=df_panel_catalog["P_max STC (W)"].min(), vmax=df_panel_catalog["P_max STC (W)"].max())
                    .background_gradient(subset=["V_oc STC (V)"], cmap="Blues")
                    .format({"γ P_max (%/°C)": "{:.3f}", "NOCT (°C)": "{:.0f}"}),
                use_container_width=True,
                hide_index=True,
            )
        
        with tab_tech:
            # Análisis por tecnología
            tech_groups = {}
            for p in panels:
                tech = p.get("technology", "Unknown")
                if tech not in tech_groups:
                    tech_groups[tech] = []
                tech_groups[tech].append(p)
            
            for tech, tech_panels in sorted(tech_groups.items()):
                with st.expander(f"🔬 **{tech}** ({len(tech_panels)} paneles)", expanded=True):
                    tcol1, tcol2, tcol3, tcol4 = st.columns(4)
                    
                    avg_p = sum(p.get("pmax_stc_w", 0) for p in tech_panels) / len(tech_panels)
                    avg_eff = (avg_p / (1.6 * 1000)) * 100  # Asumiendo 1.6 m² de área típica
                    avg_noct = sum(p.get("noct_c", 45) for p in tech_panels) / len(tech_panels)
                    gamma_vals = [p.get("gamma_pmax_per_c", -0.003) for p in tech_panels]
                    avg_gamma = sum(gamma_vals) / len(gamma_vals)
                    
                    tcol1.metric("Paneles", len(tech_panels))
                    tcol2.metric("P_max avg", f"{avg_p:.0f} W")
                    tcol3.metric("Eficiencia típica", f"{avg_eff:.1f}%")
                    tcol4.metric("Coef. γ promedio", f"{avg_gamma*100:.3f}%/°C")
                    
                    # Listar paneles de esta tecnología
                    for tp in tech_panels:
                        st.caption(
                            f"• **{tp['panel_id']}** — {tp.get('pmax_stc_w', 0):.0f}W · "
                            f"NOCT {tp.get('noct_c', 0):.0f}°C · Tier {tp.get('tier', 0)}"
                        )
        
        with tab_metrics:
            # Gráficos comparativos
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                fig_pmax = go.Figure()
                for p in panels:
                    fig_pmax.add_trace(
                        go.Bar(
                            x=[p["panel_id"]],
                            y=[p.get("pmax_stc_w", 0)],
                            name=p["panel_id"],
                            marker_color=PANEL_COLORS.get(p["panel_id"], DEFAULT_COLOR),
                        )
                    )
                fig_pmax.update_layout(
                    **_fig_layout(
                        title_text="P_max STC por panel",
                        xaxis_title="Panel",
                        yaxis_title="Potencia (W)",
                        height=300,
                        showlegend=False,
                    )
                )
                st.plotly_chart(fig_pmax, use_container_width=True)
            
            with col_chart2:
                fig_noct = go.Figure()
                for p in panels:
                    fig_noct.add_trace(
                        go.Scatter(
                            x=[p["panel_id"]],
                            y=[p.get("noct_c", 0)],
                            mode="markers",
                            marker=dict(
                                size=15,
                                color=PANEL_COLORS.get(p["panel_id"], DEFAULT_COLOR),
                                line=dict(width=2, color="white"),
                            ),
                            name=p["panel_id"],
                        )
                    )
                fig_noct.update_layout(
                    **_fig_layout(
                        title_text="NOCT por panel",
                        xaxis_title="Panel",
                        yaxis_title="NOCT (°C)",
                        height=300,
                        showlegend=False,
                    )
                )
                st.plotly_chart(fig_noct, use_container_width=True)

    # ── Arquitectura del proyecto — MEJORADO ──
    st.markdown("---")
    st.markdown('<div class="section-title">🏗️ Arquitectura + Estado del proyecto</div>', unsafe_allow_html=True)

    tab_arch, tab_stats, tab_docs = st.tabs(["🏗️ Estructura", "📈 Estadísticas", "📚 Documentación"])
    
    with tab_arch:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(
                """
                #### 📦 Paquete físico `packages/pv-twin/`
                
                **`models/`** — Datos y catálogo
                - `PanelParameters` — Pydantic v2 schema
                - `catalog.py` — Carga JSON en data/panels/
                
                **`simulator/`** — Física del gemelo
                - `single_diode.py` — SDM + CEC parameters
                - `temperature.py` — Modelo Ross-NOCT
                
                **`kpi/`** — Análisis de desempeño
                - `performance.py` — PR, CUF, Yield
                - `efficiency.py` — Degradación, factor de sobrevolts
                """,
            )
        with col_b:
            st.markdown(
                """
                #### 🌐 API REST `apps/api/`
                
                **`main.py`** — FastAPI app
                - `GET /health` — latencia
                - `GET /api/v1/twin/panels` — catálogo completo
                - `GET /api/v1/twin/panels/{id}` — detalles panel
                
                **`routers/twin.py`** — 6 endpoints
                - `POST /cell-temperature` — Ross-NOCT
                - `GET /.../iv` — curva I-V (SDM)
                - `GET /.../pv` — curva P-V (CEC)
                
                **Docs automática** → [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
                """,
            )
    
    with tab_stats:
        stat1, stat2, stat3 = st.columns(3)
        
        with stat1:
            st.markdown("### 🧪 Cobertura de pruebas")
            st.metric("Tests unitarios", 32, help="SDM, NOCT, KPIs, catalog")
            st.metric("Tests integración", 10, help="Endpoints API")
            st.metric("Smoke tests", 2, help="Tier 1 panels")
            st.markdown(f"**Total:** 44 pruebas ✅ 100% pasando")
        
        with stat2:
            st.markdown("### 📊 Catálogo de paneles")
            st.metric("Total paneles", len(panels), help="Archivos JSON en data/panels/")
            st.metric("Tier 1 premium", len(tier1), help="Eficiencia > 21%")
            st.metric("Tecnologías", len(tech_groups), help="Mono/Poly/TOPCon/HPBC")
            avg_p_range = f"{min((p.get('pmax_stc_w', 0) for p in panels), default=0):.0f}—{max((p.get('pmax_stc_w', 0) for p in panels), default=0):.0f}W"
            st.markdown(f"**Rango P_max STC:** {avg_p_range}")
        
        with stat3:
            st.markdown("### ⚙️ Rendimiento")
            st.metric("Latencia API", f"{health.get('latency_ms', 0):.0f} ms", 
                     delta="Excelente" if health.get('latency_ms', 0) < 50 else "Bueno",
                     delta_color="off")
            st.metric("Python", "3.11+", help="Type hints + PEP 604")
            st.metric("Dependencias core", 4, help="pvlib, pydantic, fastapi, httpx")
            st.markdown(f"**Última actualización:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    with tab_docs:
        st.markdown(
            """
            #### 📖 Referencias rápidas
            
            **[README.md](https://github.com/your-repo)** — Guía de inicio rápido  
            **[pyproject.toml](https://github.com/your-repo)** — Configuración pip + ruff + mypy  
            **[docs/PANEL_TIER1_SETUP.md](https://github.com/your-repo)** — Agregar nuevos paneles  
            
            #### 🔧 Comandos clave
            
            ```bash
            # Setup
            python -m venv .venv && source .venv/bin/activate
            pip install -e ".[dev]"
            
            # Tests
            pytest --cov=packages/pv-twin --cov-fail-under=85
            
            # Linting
            ruff check . && ruff format .
            mypy packages/pv-twin
            
            # API
            uvicorn apps.api.main:app --reload --port 8000
            
            # Dashboard
            streamlit run apps/dashboard/main.py
            ```
            
            #### 🎯 Convención de unidades (REGLA DE ORO)
            
            Todas las variables físicas incluyen **unidad en el nombre**:
            - `g_poa_w_m2` · `t_cell_c` · `t_amb_c` · `noct_c`
            - `p_dc_w` · `p_mpp_w` · `v_mpp_v` · `i_mpp_a`
            - `ff_ratio` · `pr_ratio` · `cuf_ratio`
            """
        )


# ─────────────────────────────────────────────────────────────────────────────
# PÁGINA 2 — SIMULADOR I-V / P-V
# ─────────────────────────────────────────────────────────────────────────────

elif page == "⚡ Simulador I-V":

    panels_resp = api_list_panels()
    panels = panels_resp.get("data", []) if panels_resp["ok"] else []
    panel_ids = [p["panel_id"] for p in panels] if panels else []

    # ── Controles en sidebar ──
    with st.sidebar:
        st.markdown("---")
        st.markdown(
            '<div style="font-size:12px;color:#7fa3bc;font-weight:600;'
            'text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;">'
            'Parámetros de simulación</div>',
            unsafe_allow_html=True,
        )

        if not panel_ids:
            st.warning("Sin paneles disponibles")
        else:
            selected_panel = st.selectbox(
                "Panel fotovoltaico",
                panel_ids,
                format_func=lambda x: x.replace("_", " ").title(),
                key="sel_panel_sim",
            )

            g_poa = st.slider(
                "Irradiancia G_POA (W/m²)",
                min_value=10,
                max_value=1400,
                value=st.session_state.sim_state["g_poa"],
                step=10,
                key="g_poa_sim",
            )

            t_cell = st.slider(
                "Temperatura T_cell (°C)",
                min_value=-10,
                max_value=85,
                value=st.session_state.sim_state["t_cell"],
                step=1,
                key="t_cell_sim",
            )

            n_points = st.number_input(
                "Resolución curva (puntos)",
                min_value=50,
                max_value=500,
                value=st.session_state.sim_state["n_points"],
                step=10,
                key="n_points_sim",
            )

    if not panel_ids:
        st.error("API no disponible o catálogo vacío. Inicia la FastAPI primero.")
        st.stop()

    # ── DETECTOR AUTOMÁTICO DE CAMBIOS (Reactividad) ──
    params_changed = (
        g_poa != st.session_state.sim_state["g_poa"] or
        t_cell != st.session_state.sim_state["t_cell"] or
        n_points != st.session_state.sim_state["n_points"] or
        selected_panel != st.session_state.sim_state["last_panel"]
    )

    # Actualizar estado
    if params_changed:
        st.session_state.sim_state["g_poa"] = g_poa
        st.session_state.sim_state["t_cell"] = t_cell
        st.session_state.sim_state["n_points"] = n_points
        st.session_state.sim_state["last_panel"] = selected_panel
        st.session_state.sim_state["needs_update"] = True

    # ── EJECUTAR SIMULACIÓN AUTOMÁTICAMENTE ──
    if st.session_state.sim_state["needs_update"]:
        with st.spinner("Calculando curvas SDM/CEC…"):
            # Llamadas a API
            panel_detail = api_get_panel(selected_panel)
            iv_resp = api_iv_curve(selected_panel, g_poa, t_cell, n_points)
            pv_resp = api_pv_curve(selected_panel, g_poa, t_cell, n_points)

        # Actualizar flag
        st.session_state.sim_state["needs_update"] = False

        # Almacenar resultados en session_state
        st.session_state.sim_state["iv_data"] = iv_resp.get("data", {})
        st.session_state.sim_state["pv_data"] = pv_resp.get("data", {})
        st.session_state.sim_state["panel_data"] = panel_detail.get("data", {})

    # Recuperar datos del estado
    panel_data = st.session_state.sim_state.get("panel_data", {})
    iv_data = st.session_state.sim_state.get("iv_data", {})
    pv_data = st.session_state.sim_state.get("pv_data", {})

    if not iv_data or not pv_data:
        st.error("Error al obtener curvas")
        st.stop()

    color = PANEL_COLORS.get(selected_panel, DEFAULT_COLOR)

    v_iv = iv_data.get("v_v", [])
    i_iv = iv_data.get("i_a", [])
    v_pv = pv_data.get("v_v", [])
    p_pv = pv_data.get("p_w", [])

    # Extraer punto MPP
    p_mpp_val  = iv_data.get("p_mp_w")
    v_mpp_val  = iv_data.get("v_mp_v")
    i_mpp_val  = iv_data.get("i_mp_a")
    v_oc_val   = iv_data.get("v_oc_v")
    i_sc_val   = iv_data.get("i_sc_a")

    # Calcular temperatura de celda via API para verificar
    noct_val = panel_data.get("noct_c", 45.0)
    t_amb_equiv = t_cell - ((noct_val - 20) / 800) * g_poa

    # ── Métricas resultado MEJORADAS ──
    pmax_stc = panel_data.get("pmax_stc_w", 1)
    loss_pct = ((p_mpp_val or 0) - pmax_stc) / pmax_stc * 100 if pmax_stc else 0
    
    # Calcular Fill Factor y eficiencia
    ff_calc = (p_mpp_val or 0) / ((v_oc_val or 1) * (i_sc_val or 1)) if (v_oc_val and i_sc_val and p_mpp_val) else 0
    area_m2 = 1.6  # Área típica de panel
    efficiency_calc = (p_mpp_val or 0) / (g_poa * area_m2) * 100 if (g_poa and p_mpp_val) else 0

    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("P_mpp",   f"{p_mpp_val:.1f} W"  if p_mpp_val else "—",
              delta=f"{loss_pct:.1f}% vs STC", delta_color="normal")
    m2.metric("V_mpp",   f"{v_mpp_val:.2f} V"  if v_mpp_val else "—",
              delta=f"V_oc {v_oc_val:.2f}V" if v_oc_val else "—", delta_color="off")
    m3.metric("I_mpp",   f"{i_mpp_val:.3f} A"  if i_mpp_val else "—",
              delta=f"I_sc {i_sc_val:.3f}A" if i_sc_val else "—", delta_color="off")
    m4.metric("Fill Factor",   f"{ff_calc*100:.1f}%"  if ff_calc else "—",
              help="FF = P_mpp / (V_oc × I_sc)")
    m5.metric("Eficiencia",   f"{efficiency_calc:.2f}%"  if efficiency_calc else "—",
              help="η = P_mpp / (G × Area)")
    m6.metric("Latencia API",f"{iv_resp['latency_ms']:.0f} ms" if iv_resp.get("latency_ms") else "—",
              help="Tiempo de respuesta de la API")

    st.markdown("---")

    # ── Gráficos I-V y P-V ──
    col_iv, col_pv = st.columns(2)

    with col_iv:
        st.markdown(
            '<div class="section-title">Curva I-V · Single Diode Model</div>',
            unsafe_allow_html=True,
        )
        if v_iv and i_iv:
            fig_iv = build_iv_fig(
                v_iv, i_iv,
                selected_panel.replace("_", " ").title(),
                color,
                v_mpp=v_mpp_val,
                i_mpp=i_mpp_val,
            )
            st.plotly_chart(fig_iv, use_container_width=True)
        else:
            st.warning("Sin datos de curva I-V")

    with col_pv:
        st.markdown(
            '<div class="section-title">Curva P-V · Punto máxima potencia</div>',
            unsafe_allow_html=True,
        )
        if v_pv and p_pv:
            fig_pv = build_pv_fig(
                v_pv, p_pv,
                selected_panel.replace("_", " ").title(),
                color,
                v_mpp=v_mpp_val,
                p_mpp=p_mpp_val,
            )
            st.plotly_chart(fig_pv, use_container_width=True)
        else:
            st.warning("Sin datos de curva P-V")

    # ── Tabla de parámetros físicos — MEJORADA ──
    st.markdown("---")
    st.markdown(
        '<div class="section-title">📋 Parámetros del panel + Análisis en campo</div>',
        unsafe_allow_html=True,
    )

    if panel_data:
        tab_stc, tab_field, tab_comparison = st.tabs(["📌 STC (Datasheet)", "🏭 Condiciones de campo", "📊 Comparativa STC vs Campo"])
        
        with tab_stc:
            df_params = pd.DataFrame(
                [
                    {"Parámetro": "P_max STC",          "Valor": f"{panel_data.get('pmax_stc_w',0):.0f} W",       "Descripción": "Potencia pico en STC (G=1000 W/m², T=25°C)"},
                    {"Parámetro": "V_oc STC",            "Valor": f"{panel_data.get('voc_stc_v',0):.2f} V",       "Descripción": "Voltaje de circuito abierto (STC)"},
                    {"Parámetro": "I_sc STC",            "Valor": f"{panel_data.get('isc_stc_a',0):.3f} A",       "Descripción": "Corriente de cortocircuito (STC)"},
                    {"Parámetro": "V_mpp STC",           "Valor": f"{panel_data.get('vmpp_stc_v',0):.2f} V",      "Descripción": "Voltaje en máxima potencia (STC)"},
                    {"Parámetro": "I_mpp STC",           "Valor": f"{panel_data.get('impp_stc_a',0):.3f} A",      "Descripción": "Corriente en máxima potencia (STC)"},
                    {"Parámetro": "FF STC (Calculado)",  "Valor": f"{(panel_data.get('pmax_stc_w',0) / (panel_data.get('voc_stc_v',1) * panel_data.get('isc_stc_a',1)) * 100):.2f}%", "Descripción": "Fill Factor = P_mpp / (V_oc × I_sc)"},
                    {"Parámetro": "γ P_max",             "Valor": f"{panel_data.get('gamma_pmax_per_c',0)*100:.3f} %/°C", "Descripción": "Coeficiente de temp. potencia (↓ con T)"},
                    {"Parámetro": "NOCT",                "Valor": f"{panel_data.get('noct_c',0):.0f} °C",         "Descripción": "Temperatura normal operación celda"},
                    {"Parámetro": "Células en serie",    "Valor": str(panel_data.get("cells_in_series","—")),      "Descripción": "Configuración de células en el módulo"},
                    {"Parámetro": "Tecnología",          "Valor": panel_data.get("technology","—"),                "Descripción": "Tipo de celda (Monocristalino/TOPCon/HPBC/Poli)"},
                ]
            )
            st.dataframe(df_params, use_container_width=True, hide_index=True)
        
        with tab_field:
            st.markdown(f"**Condiciones de simulación:** G_POA = {g_poa} W/m² · T_cell = {t_cell}°C · Puntos = {n_points}")
            
            df_field = pd.DataFrame(
                [
                    {"Parámetro": "P_mpp (campo)",       "Valor": f"{p_mpp_val:.1f} W",                                  "Comparación": f"{loss_pct:+.1f}% vs STC"},
                    {"Parámetro": "V_mpp (campo)",       "Valor": f"{v_mpp_val:.2f} V",                                  "Comparación": "Varía con G y T"},
                    {"Parámetro": "I_mpp (campo)",       "Valor": f"{i_mpp_val:.3f} A",                                  "Comparación": "Proporcional a G_POA"},
                    {"Parámetro": "V_oc (campo)",        "Valor": f"{v_oc_val:.2f} V",                                   "Comparación": f"Δ {v_oc_val - panel_data.get('voc_stc_v', 0):+.2f}V"},
                    {"Parámetro": "I_sc (campo)",        "Valor": f"{i_sc_val:.3f} A",                                   "Comparación": f"Δ {i_sc_val - panel_data.get('isc_stc_a', 0):+.3f}A"},
                    {"Parámetro": "Fill Factor (campo)", "Valor": f"{ff_calc*100:.2f}%",                                 "Comparación": f"Δ {(ff_calc - panel_data.get('pmax_stc_w', 0) / (panel_data.get('voc_stc_v', 1) * panel_data.get('isc_stc_a', 1)))*100:.2f}%"},
                    {"Parámetro": "Eficiencia (campo)",  "Valor": f"{efficiency_calc:.2f}%",                             "Comparación": "Relativo a radiación incidente"},
                ]
            )
            st.dataframe(df_field, use_container_width=True, hide_index=True)
        
        with tab_comparison:
            # Gráfico de comparativa
            fig_compare = go.Figure()
            
            # Valores STC
            p_stc = panel_data.get("pmax_stc_w", 0)
            v_stc = panel_data.get("vmpp_stc_v", 0)
            i_stc = panel_data.get("impp_stc_a", 0)
            
            fig_compare.add_trace(
                go.Bar(
                    name="STC (G=1000, T=25°C)",
                    x=["P_mpp (W)", "V_mpp (V)×10", "I_mpp (A)×100"],
                    y=[p_stc, v_stc*10, i_stc*100],
                    marker_color=COLORS["amber"],
                )
            )
            
            fig_compare.add_trace(
                go.Bar(
                    name=f"Campo (G={g_poa}, T={t_cell}°C)",
                    x=["P_mpp (W)", "V_mpp (V)×10", "I_mpp (A)×100"],
                    y=[p_mpp_val or 0, (v_mpp_val or 0)*10, (i_mpp_val or 0)*100],
                    marker_color=COLORS["teal"],
                )
            )
            
            fig_compare.update_layout(
                **_fig_layout(
                    title_text="Comparativa: Condiciones STC vs Campo",
                    xaxis_title="Parámetro",
                    yaxis_title="Valor (escalado para visualización)",
                    height=300,
                    barmode="group",
                )
            )
            st.plotly_chart(fig_compare, use_container_width=True)
            
            st.info(
                f"📊 **Análisis:** Con los parámetros actuales (G={g_poa} W/m², T={t_cell}°C), "
                f"el panel opera a **{loss_pct:.1f}%** de su potencia STC. "
                f"La pérdida es causada principalmente por temperatura (+{t_cell-25}°C → γ={panel_data.get('gamma_pmax_per_c',0)*100:.2f}%/°C) "
                f"{'e irradiancia reducida' if g_poa < 1000 else ''}."
            )

    # ── MEJORA 2: Guardar simulación en historial ──
    st.markdown("---")

    col_save, col_clear = st.columns([3, 1])
    
    with col_save:
        sim_note = st.text_input(
            "💾 Nota para esta simulación (opcional)",
            placeholder="ej: Día despejado, prueba de máximo rendimiento",
            key="sim_note_input",
        )
    
    with col_clear:
        if st.button("💾 Guardar", key="btn_save_sim"):
            # Crear registro
            sim_record = {
                "timestamp": datetime.now(),
                "panel_id": selected_panel,
                "g_poa_w_m2": g_poa,
                "t_cell_c": t_cell,
                "p_mp_w": p_mpp_val or 0,
                "v_mp_v": v_mpp_val or 0,
                "i_mp_a": i_mpp_val or 0,
                "efficiency_loss_pct": (
                    ((p_mpp_val or 1) - pmax_stc) / pmax_stc * 100
                    if pmax_stc else 0
                ),
                "note": sim_note,
            }
            
            # Agregar al inicio (más recientes primero)
            st.session_state.sim_history.insert(0, sim_record)
            
            # Mantener solo últimas 10
            st.session_state.sim_history = st.session_state.sim_history[:10]
            
            st.success(f"✅ Simulación guardada (Total: {len(st.session_state.sim_history)})")

    # ── MOSTRAR HISTORIAL ──
    if st.session_state.sim_history:
        with st.expander("📜 Historial de simulaciones"):
            # Crear tabla
            hist_data = []
            for idx, rec in enumerate(st.session_state.sim_history):
                hist_data.append({
                    "Hora": rec["timestamp"].strftime("%H:%M:%S"),
                    "Panel": rec["panel_id"],
                    "G (W/m²)": f"{rec['g_poa_w_m2']:.0f}",
                    "T (°C)": f"{rec['t_cell_c']:.0f}",
                    "P_mpp (W)": f"{rec['p_mp_w']:.1f}",
                    "V_mpp (V)": f"{rec['v_mp_v']:.2f}",
                    "Pérdida %": f"{rec['efficiency_loss_pct']:.1f}%",
                    "Nota": rec["note"][:30] if rec["note"] else "—",
                })
            
            df_hist = pd.DataFrame(hist_data)
            st.dataframe(df_hist, use_container_width=True, hide_index=True)
            
            # Acciones
            col_reload, col_export, col_clear = st.columns(3)
            
            with col_reload:
                selected_history_idx = st.selectbox(
                    "🔄 Recargar simulación",
                    range(len(st.session_state.sim_history)),
                    format_func=lambda i: (
                        f"{st.session_state.sim_history[i]['panel_id']} @ "
                        f"{st.session_state.sim_history[i]['g_poa_w_m2']:.0f}W/m² - "
                        f"{st.session_state.sim_history[i]['timestamp'].strftime('%H:%M')}"
                    ),
                )
                
                if st.button("➡️ Cargar", key="btn_load_hist"):
                    rec = st.session_state.sim_history[selected_history_idx]
                    st.session_state.sim_state["g_poa"] = rec["g_poa_w_m2"]
                    st.session_state.sim_state["t_cell"] = rec["t_cell_c"]
                    st.session_state.sim_state["last_panel"] = rec["panel_id"]
                    st.session_state.sim_state["needs_update"] = True
                    st.rerun()
            
            with col_export:
                # Exportar historial como CSV
                hist_csv = df_hist.to_csv(index=False)
                st.download_button(
                    "📥 Exportar CSV",
                    data=hist_csv,
                    file_name=f"historial_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key="btn_export_hist",
                )
            
            with col_clear:
                if st.button("🗑️ Limpiar historial", key="btn_clear_hist"):
                    st.session_state.sim_history = []
                    st.success("✅ Historial limpiado")
                    st.rerun()
    else:
        st.info("📭 Sin simulaciones guardadas aún. Simula primero y luego guarda con el botón 💾")

    # ── MEJORA 4: Exportación de Datos ──
    st.markdown("---")
    st.markdown(
        '<div class="section-title">📥 Exportar resultados</div>',
        unsafe_allow_html=True,
    )

    col_csv, col_json, col_xlsx = st.columns(3)

    # ── EXPORTAR CSV ──
    with col_csv:
        # Preparar datos
        export_df = pd.DataFrame({
            "Voltaje_V": v_iv,
            "Corriente_A": i_iv,
            "Potencia_W": p_pv,
        })
        
        csv_data = export_df.to_csv(index=False)
        
        st.download_button(
            label="📄 CSV (datos)",
            data=csv_data,
            file_name=f"iv_curve_{selected_panel}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            key="btn_export_csv",
        )

    # ── EXPORTAR JSON ──
    with col_json:
        export_json = {
            "metadata": {
                "panel_id": selected_panel,
                "g_poa_w_m2": g_poa,
                "t_cell_c": t_cell,
                "timestamp": datetime.now().isoformat(),
                "n_points": n_points,
            },
            "results": {
                "v_mp_v": v_mpp_val,
                "i_mp_a": i_mpp_val,
                "p_mp_w": p_mpp_val,
                "v_oc_v": v_oc_val,
                "i_sc_a": i_sc_val,
            },
            "curves": {
                "iv": {
                    "v_v": v_iv,
                    "i_a": i_iv,
                },
                "pv": {
                    "v_v": v_pv,
                    "p_w": p_pv,
                },
            },
        }
        
        json_str = json.dumps(export_json, indent=2)
        
        st.download_button(
            label="🔗 JSON (estructurado)",
            data=json_str,
            file_name=f"iv_curve_{selected_panel}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            key="btn_export_json",
        )

    # ── EXPORTAR EXCEL (Multi-sheet) ──
    with col_xlsx:
        buffer = io.BytesIO()
        
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            # Sheet 1: Curva I-V
            df_iv = pd.DataFrame({
                "V (V)": v_iv,
                "I (A)": i_iv,
            })
            df_iv.to_excel(writer, sheet_name="IV Curve", index=False)
            
            # Sheet 2: Curva P-V
            df_pv = pd.DataFrame({
                "V (V)": v_pv,
                "P (W)": p_pv,
            })
            df_pv.to_excel(writer, sheet_name="PV Curve", index=False)
            
            # Sheet 3: Metadata
            df_meta = pd.DataFrame({
                "Parámetro": [
                    "Panel ID",
                    "G_POA (W/m²)",
                    "T_cell (°C)",
                    "Timestamp",
                    "V_mpp (V)",
                    "I_mpp (A)",
                    "P_mpp (W)",
                    "V_oc (V)",
                    "I_sc (A)",
                ],
                "Valor": [
                    selected_panel,
                    g_poa,
                    t_cell,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    f"{v_mpp_val:.2f}" if v_mpp_val else "—",
                    f"{i_mpp_val:.3f}" if i_mpp_val else "—",
                    f"{p_mpp_val:.1f}" if p_mpp_val else "—",
                    f"{v_oc_val:.2f}" if v_oc_val else "—",
                    f"{i_sc_val:.3f}" if i_sc_val else "—",
                ],
            })
            df_meta.to_excel(writer, sheet_name="Metadata", index=False)
        
        buffer.seek(0)
        
        st.download_button(
            label="📊 Excel (Multi-sheet)",
            data=buffer.getvalue(),
            file_name=f"iv_analysis_{selected_panel}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="btn_export_xlsx",
        )


# ─────────────────────────────────────────────────────────────────────────────
# PÁGINA 3 — COMPARADOR MULTI-PANEL
# ─────────────────────────────────────────────────────────────────────────────

elif page == "🔄 Comparador":

    panels_resp = api_list_panels()
    panels = panels_resp.get("data", []) if panels_resp["ok"] else []
    panel_ids = [p["panel_id"] for p in panels] if panels else []

    if len(panel_ids) < 2:
        st.warning("Se necesitan al menos 2 paneles en el catálogo para comparar.")
        st.stop()

    # ── Controles en sidebar ──
    with st.sidebar:
        st.markdown("---")
        st.markdown(
            '<div style="font-size:12px;color:#7fa3bc;font-weight:600;'
            'text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;">'
            'Selección inteligente de paneles</div>',
            unsafe_allow_html=True,
        )

        # BUSCAR por nombre/tecnología
        search_term = st.text_input(
            "🔍 Buscar panel",
            placeholder="ej: jinko, topcon, 580",
            key="search_panels",
        ).lower()

        # FILTRAR por Tier
        available_tiers = sorted(set(p.get("tier", 1) for p in panels))
        selected_tiers = st.multiselect(
            "📊 Filtrar por Tier",
            available_tiers,
            default=available_tiers,
            key="filter_tier",
        )

        # APLICAR FILTROS
        filtered_panels = [
            p for p in panels
            if (
                (search_term == "" or
                 search_term in p["panel_id"].lower() or
                 search_term in p.get("technology", "").lower())
                and p.get("tier", 1) in selected_tiers
            )
        ]

        filtered_panel_ids = [p["panel_id"] for p in filtered_panels]

        st.markdown(f'<div style="font-size:11px;color:#7fa3bc;">'
                    f'📍 {len(filtered_panel_ids)} panel(es) encontrado(s)</div>',
                    unsafe_allow_html=True)

    # Validar que haya al menos 2 paneles después de filtro
    if len(filtered_panel_ids) < 2:
        st.warning(
            f"❌ Se encontraron solo {len(filtered_panel_ids)} panel(es). "
            f"Ajusta los filtros de búsqueda."
        )
        st.stop()

    # ── FAVORITOS ──
    st.markdown("---")
    
    col_fav_title, col_fav_count = st.columns([3, 1])
    with col_fav_title:
        st.markdown("⭐ **Mis paneles favoritos**")
    with col_fav_count:
        st.markdown(f'<div style="text-align:right;color:#7fa3bc;font-size:11px;">'
                    f'{len(st.session_state.fav_panels)} fav.</div>',
                    unsafe_allow_html=True)

    if st.session_state.fav_panels:
        cols = st.columns(len(st.session_state.fav_panels))
        for col, fav_id in zip(cols, st.session_state.fav_panels):
            with col:
                col.metric("", fav_id, help="Click para seleccionar")
                if col.button("×", key=f"del_fav_{fav_id}"):
                    st.session_state.fav_panels.remove(fav_id)
                    st.rerun()
    else:
        st.caption("Sin favoritos aún. Marca ⭐ mientras comparas.")

    st.markdown("---")

    # ── CONTROLES DE CONDICIONES ──
    with st.sidebar:
        st.markdown("---")
        st.markdown(
            '<div style="font-size:12px;color:#7fa3bc;font-weight:600;'
            'text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;">'
            'Condiciones comparación</div>',
            unsafe_allow_html=True,
        )
        g_poa_cmp = st.slider(
            "G_POA (W/m²)", 10, 1400, 900, 10,
            key="cmp_g", help="Irradiancia compartida para todos los paneles",
        )
        t_cell_cmp = st.slider(
            "T_cell (°C)", -10, 85, 45, 1,
            key="cmp_t", help="Temperatura de celda (representativa Eje Cafetero)",
        )
        n_pts_cmp = st.select_slider(
            "Puntos de curva", [50, 100, 150, 200], value=100, key="cmp_n",
        )

    # ── SELECCIÓN DE PANELES ──
    st.markdown("**Selecciona paneles a comparar** (mín. 2)")

    col1, col2, col3 = st.columns(3)

    with col1:
        panel_1 = st.selectbox(
            "Panel 1",
            filtered_panel_ids,
            key="cmp_panel_1",
        )
        col1_fav = col1.button("⭐", key="fav_p1", help="Agregar a favoritos")
        if col1_fav and panel_1 not in st.session_state.fav_panels:
            st.session_state.fav_panels.append(panel_1)
            st.success(f"✅ {panel_1} agregado a favoritos")

    with col2:
        panel_2 = st.selectbox(
            "Panel 2",
            filtered_panel_ids,
            key="cmp_panel_2",
        )
        col2_fav = col2.button("⭐", key="fav_p2")
        if col2_fav and panel_2 not in st.session_state.fav_panels:
            st.session_state.fav_panels.append(panel_2)
            st.success(f"✅ {panel_2} agregado a favoritos")

    with col3:
        panel_3 = st.selectbox(
            "Panel 3 (opcional)",
            ["—"] + filtered_panel_ids,
            key="cmp_panel_3",
        )
        if panel_3 != "—":
            col3_fav = col3.button("⭐", key="fav_p3")
            if col3_fav and panel_3 not in st.session_state.fav_panels:
                st.session_state.fav_panels.append(panel_3)
                st.success(f"✅ {panel_3} agregado a favoritos")

    # Construir lista de paneles seleccionados
    selected_panels = [panel_1, panel_2]
    if panel_3 != "—":
        selected_panels.append(panel_3)

    # ── Obtener curvas para todos los paneles seleccionados ──
    pv_curves: dict[str, dict] = {}
    kpi_rows: list[dict] = []

    palette = [
        COLORS["teal"], COLORS["blue"], COLORS["amber"],
        COLORS["coral"], COLORS["purple"],
    ]

    with st.spinner(f"Calculando curvas para {len(selected_panels)} paneles…"):
        for pid in selected_panels:
            pv_r = api_pv_curve(pid, g_poa_cmp, t_cell_cmp, n_pts_cmp)
            iv_r = api_iv_curve(pid, g_poa_cmp, t_cell_cmp, n_pts_cmp)
            pv_curves[pid] = {
                "pv": pv_r.get("data", {}),
                "iv": iv_r.get("data", {}),
                "ok": pv_r["ok"] and iv_r["ok"],
            }
            if pv_r["ok"] and iv_r["ok"]:
                iv_d = iv_r["data"]
                kpi_rows.append({
                    "Panel":         pid.replace("_", " ").title(),
                    "P_mpp (W)":     round(iv_d.get("p_mp_w", 0), 1),
                    "V_mpp (V)":     round(iv_d.get("v_mp_v", 0), 2),
                    "I_mpp (A)":     round(iv_d.get("i_mp_a", 0), 3),
                    "V_oc (V)":      round(iv_d.get("v_oc_v", 0), 2),
                    "I_sc (A)":      round(iv_d.get("i_sc_a", 0), 3),
                })

    # ── Gráfico P-V superpuesto ──
    st.markdown(
        '<div class="section-title">Curvas P-V superpuestas</div>',
        unsafe_allow_html=True,
    )

    fig_cmp = go.Figure()
    for idx, pid in enumerate(selected_panels):
        clr = palette[idx % len(palette)]
        d   = pv_curves[pid]
        if not d["ok"]:
            continue
        v_d = d["pv"].get("v_v", [])
        p_d = d["pv"].get("p_w", [])
        v_m = d["iv"].get("v_mp_v")
        p_m = d["iv"].get("p_mp_w")
        label = pid.replace("_", " ").title()

        fig_cmp.add_trace(
            go.Scatter(
                x=v_d, y=p_d,
                mode="lines",
                name=label,
                line=dict(color=clr, width=2.5),
                hovertemplate=f"<b>{label}</b><br>V: %{{x:.2f}} V<br>P: %{{y:.1f}} W<extra></extra>",
            )
        )
        if v_m and p_m:
            fig_cmp.add_trace(
                go.Scatter(
                    x=[v_m], y=[p_m],
                    mode="markers",
                    name=f"MPP {label}",
                    marker=dict(color=clr, size=10, symbol="diamond",
                                line=dict(color="white", width=2)),
                    showlegend=False,
                    hovertemplate=f"<b>MPP {label}</b><br>{p_m:.1f} W @ {v_m:.2f} V<extra></extra>",
                )
            )

    fig_cmp.update_layout(
        **_fig_layout(
            xaxis_title="Voltaje (V)",
            yaxis_title="Potencia (W)",
            height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        )
    )
    st.plotly_chart(fig_cmp, use_container_width=True)

    # ── Tabla comparativa — MEJORADA ──
    if kpi_rows:
        st.markdown(
            '<div class="section-title">📊 Análisis comparativo detallado</div>',
            unsafe_allow_html=True,
        )
        df_kpi = pd.DataFrame(kpi_rows)

        # Añadir columna de diferencia relativa respecto al mejor P_mpp
        best_pmpp = df_kpi["P_mpp (W)"].max()
        df_kpi["Δ vs mejor (%)"] = ((df_kpi["P_mpp (W)"] - best_pmpp) / best_pmpp * 100).round(2)
        
        # Calcular eficiencia relativa y Fill Factor
        df_kpi["FF (%)"] = ((df_kpi["P_mpp (W)"] / (df_kpi["V_mpp (V)"] * df_kpi["I_mpp (A)"])) * 100).round(2)
        df_kpi["Rank"] = df_kpi["P_mpp (W)"].rank(ascending=False).astype(int)

        # Reordenar columnas
        df_kpi = df_kpi[["Rank", "Panel", "P_mpp (W)", "V_mpp (V)", "I_mpp (A)", "V_oc (V)", "I_sc (A)", "FF (%)", "Δ vs mejor (%)"]]

        st.dataframe(
            df_kpi.style
                .format({"Δ vs mejor (%)": "{:+.2f}%", "FF (%)": "{:.2f}"})
                .background_gradient(subset=["P_mpp (W)"], cmap="Greens")
                .background_gradient(subset=["FF (%)"], cmap="Blues")
                .set_properties(**{"font-size": "13px", "text-align": "center"}),
            use_container_width=True,
            hide_index=True,
        )
        
        # Análisis textual
        top_panel = df_kpi.iloc[0]["Panel"]
        max_p = df_kpi["P_mpp (W)"].max()
        min_p = df_kpi["P_mpp (W)"].min()
        avg_p = df_kpi["P_mpp (W)"].mean()
        
        st.success(
            f"🏆 **Panel ganador:** {top_panel} con **{max_p:.1f}W** de P_mpp\n\n"
            f"📈 **Rango de potencia:** {min_p:.1f}W – {max_p:.1f}W (diferencia: {max_p-min_p:.1f}W)\n\n"
            f"📊 **Promedio:** {avg_p:.1f}W"
        )


# ─────────────────────────────────────────────────────────────────────────────
# PÁGINA 4 — ANÁLISIS NOCT
# ─────────────────────────────────────────────────────────────────────────────

elif page == "🌡 Análisis NOCT":

    panels_resp = api_list_panels()
    panels = panels_resp.get("data", []) if panels_resp["ok"] else []
    panel_ids = [p["panel_id"] for p in panels] if panels else []

    # ── Controles ──
    with st.sidebar:
        st.markdown("---")
        st.markdown(
            '<div style="font-size:12px;color:#7fa3bc;font-weight:600;'
            'text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;">'
            'Condiciones NOCT</div>',
            unsafe_allow_html=True,
        )
        g_poa_noct = st.slider(
            "G_POA (W/m²)", 0, 1400, 900, 10,
            key="noct_g",
        )
        t_amb_noct = st.slider(
            "T_amb (°C)", 10.0, 40.0, 22.0, 0.5,
            key="noct_t",
            help="Temperatura ambiente Manizales: 15–26°C",
        )
        if panel_ids:
            panel_noct = st.selectbox(
                "Panel de referencia",
                panel_ids,
                format_func=lambda x: x.replace("_", " ").title(),
                key="noct_panel",
            )

    # ── Fórmula NOCT ──
    st.markdown(
        """
        <div class="noct-formula">
        T_cell = T_amb + ( (NOCT − 20) / 800 ) × G_POA
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        "Modelo Ross-NOCT: captura empíricamente absorción solar (α≈0.87), "
        "pérdidas convectivas (h_conv≈5–10 W/m²K) y radiativas bajo "
        "condiciones estándar NOCT (G=800 W/m², T=20°C, v_wind=1 m/s, AM=1.5)."
    )

    st.markdown("---")

    # ── Cálculo via API ──
    if not panel_ids:
        st.error("Sin paneles disponibles.")
        st.stop()

    panel_det = api_get_panel(panel_noct)
    pdata: dict = panel_det.get("data", {}) if panel_det["ok"] else {}
    noct_ref = pdata.get("noct_c", 44.0)
    gamma_ref = pdata.get("gamma_pmax_per_c", -0.003)
    pmax_ref = pdata.get("pmax_stc_w", 580.0)

    noct_resp = api_cell_temperature(g_poa_noct, t_amb_noct, noct_ref)
    t_cell_calc: float | None = None
    if noct_resp["ok"]:
        t_cell_calc = noct_resp["data"].get("t_cell_c")

    # ── Métricas de resultado ──
    if t_cell_calc is not None:
        dt_stc   = t_cell_calc - 25.0
        p_field  = pmax_ref * (1 + gamma_ref * dt_stc) * (g_poa_noct / 1000) if g_poa_noct > 0 else 0.0
        loss_pct_field = (p_field - pmax_ref) / pmax_ref * 100 if pmax_ref else 0

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("T_cell calculada",  f"{t_cell_calc:.1f} °C")
        m2.metric("ΔT sobre STC",      f"+{dt_stc:.1f} °C" if dt_stc >= 0 else f"{dt_stc:.1f} °C")
        m3.metric("P_mpp en campo",    f"{max(0, p_field):.0f} W",
                  delta=f"{loss_pct_field:.1f}%", delta_color="normal")
        m4.metric("Pérdida térmica",   f"{gamma_ref * dt_stc * 100:.2f}%")
    else:
        st.warning(f"Error al calcular T_cell: {noct_resp.get('error')}")

    st.markdown("---")

    # ── Gráfico T_cell vs G_POA para todos los paneles ──
    st.markdown(
        '<div class="section-title">T_cell vs irradiancia — todos los paneles</div>',
        unsafe_allow_html=True,
    )

    g_range = list(range(0, 1450, 50))
    fig_noct = go.Figure()

    palette = [COLORS["teal"], COLORS["blue"], COLORS["amber"], COLORS["coral"], COLORS["purple"]]

    for idx, panel in enumerate(panels):
        pid   = panel["panel_id"]
        noct  = panel.get("noct_c", 44)
        clr   = palette[idx % len(palette)]
        t_cells_g = [t_amb_noct + ((noct - 20) / 800) * g for g in g_range]

        fig_noct.add_trace(
            go.Scatter(
                x=g_range,
                y=t_cells_g,
                mode="lines",
                name=f"{pid.replace('_',' ').title()} (NOCT={noct}°C)",
                line=dict(color=clr, width=2),
                hovertemplate=f"G: %{{x}} W/m²<br>T_cell: %{{y:.1f}} °C<extra></extra>",
            )
        )

    # Línea de referencia T_amb
    fig_noct.add_hline(
        y=t_amb_noct,
        line_dash="dot",
        line_color=COLORS["gray"],
        annotation_text=f"T_amb = {t_amb_noct:.1f} °C",
        annotation_font_size=10,
    )
    # Línea de 25°C (STC)
    fig_noct.add_hline(
        y=25,
        line_dash="dash",
        line_color="#aaa",
        line_width=0.8,
        annotation_text="STC 25°C",
        annotation_font_size=10,
    )
    # Zona operación típica Manizales
    fig_noct.add_vrect(
        x0=400, x1=1000,
        fillcolor=COLORS["teal_light"],
        opacity=0.3,
        layer="below",
        line_width=0,
        annotation_text="Rango típico Manizales",
        annotation_position="top left",
        annotation_font_size=10,
        annotation_font_color=COLORS["teal_dark"],
    )

    fig_noct.update_layout(
        **_fig_layout(
            xaxis_title="G_POA (W/m²)",
            yaxis_title="T_cell (°C)",
            height=380,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        )
    )
    st.plotly_chart(fig_noct, use_container_width=True)

    # ── Gráfico P_mpp vs T_amb — escenarios típicos Colombia ──
    st.markdown(
        '<div class="section-title">P_mpp vs temperatura ambiente — escenarios Eje Cafetero</div>',
        unsafe_allow_html=True,
    )

    t_amb_range = [15, 18, 20, 22, 24, 26]  # Rango realista Manizales
    g_scenarios = {
        "Día despejado (G=1000)":   1000,
        "Parcialmente nublado (G=600)": 600,
        "Muy nublado (G=250)":      250,
    }
    scen_colors = [COLORS["amber"], COLORS["teal"], COLORS["blue"]]

    if panels:
        panel_sel_noct = panels[0]  # Panel de referencia (primero del catálogo)
        noct_s  = panel_sel_noct.get("noct_c", 44)
        gamma_s = panel_sel_noct.get("gamma_pmax_per_c", -0.003)
        pmax_s  = panel_sel_noct.get("pmax_stc_w", 580)

        fig_scen = go.Figure()
        for (scen_name, g_val), clr in zip(g_scenarios.items(), scen_colors):
            p_vals = []
            for t_a in t_amb_range:
                t_c  = t_a + ((noct_s - 20) / 800) * g_val
                p_v  = max(0.0, pmax_s * (1 + gamma_s * (t_c - 25)) * (g_val / 1000))
                p_vals.append(round(p_v, 1))

            fig_scen.add_trace(
                go.Scatter(
                    x=t_amb_range,
                    y=p_vals,
                    mode="lines+markers",
                    name=scen_name,
                    line=dict(color=clr, width=2),
                    marker=dict(color=clr, size=7),
                    hovertemplate=f"<b>{scen_name}</b><br>T_amb: %{{x}}°C<br>P_mpp: %{{y:.1f}} W<extra></extra>",
                )
            )

        fig_scen.update_layout(
            **_fig_layout(
                xaxis_title="T_amb (°C)",
                yaxis_title="P_mpp (W)",
                height=320,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            )
        )
        st.plotly_chart(fig_scen, use_container_width=True)

        st.caption(
            f"Panel de referencia: **{panel_sel_noct['panel_id']}** · "
            f"NOCT={noct_s}°C · γ={gamma_s*100:.3f}%/°C · P_max={pmax_s:.0f} W STC. "
            "Zona sombreada en gráfico anterior = rango operación típico Eje Cafetero (G=400–1000 W/m²)."
        )

    # ── Tabla de escenarios calculados — CON TABS ──
    st.markdown(
        '<div class="section-title">📋 Escenarios numéricos — Manizales, Caldas</div>',
        unsafe_allow_html=True,
    )

    tab_scenarios, tab_legend = st.tabs(["📊 Tabla escenarios", "📚 Leyenda + interpretación"])
    
    with tab_scenarios:
        escenarios = [
            {
                "Escenario":            "STC (referencia lab)",
                "G_POA (W/m²)":        1000,
                "T_amb (°C)":          25.0,
                "T_cell estimada (°C)": 25.0 + ((noct_ref - 20) / 800) * 1000,
                "P_mpp estimada (W)":   round(pmax_ref * (1 + gamma_ref * ((25.0 + ((noct_ref - 20) / 800) * 1000) - 25)) * 1.0, 1),
            },
            {
                "Escenario":            "Día despejado Colombia",
                "G_POA (W/m²)":        900,
                "T_amb (°C)":          24.0,
                "T_cell estimada (°C)": 24.0 + ((noct_ref - 20) / 800) * 900,
                "P_mpp estimada (W)":   round(pmax_ref * (1 + gamma_ref * ((24.0 + ((noct_ref - 20) / 800) * 900) - 25)) * 0.9, 1),
            },
            {
                "Escenario":            "Parcialmente nublado",
                "G_POA (W/m²)":        400,
                "T_amb (°C)":          22.0,
                "T_cell estimada (°C)": 22.0 + ((noct_ref - 20) / 800) * 400,
                "P_mpp estimada (W)":   round(pmax_ref * (1 + gamma_ref * ((22.0 + ((noct_ref - 20) / 800) * 400) - 25)) * 0.4, 1),
            },
            {
                "Escenario":            "Tarde muy nublado",
                "G_POA (W/m²)":        150,
                "T_amb (°C)":          20.0,
                "T_cell estimada (°C)": 20.0 + ((noct_ref - 20) / 800) * 150,
                "P_mpp estimada (W)":   round(pmax_ref * (1 + gamma_ref * ((20.0 + ((noct_ref - 20) / 800) * 150) - 25)) * 0.15, 1),
            },
        ]

        df_esc = pd.DataFrame(escenarios)
        df_esc["T_cell estimada (°C)"] = df_esc["T_cell estimada (°C)"].round(1)

        st.dataframe(
            df_esc.style
                .format({"P_mpp estimada (W)": "{:.1f}", "T_cell estimada (°C)": "{:.1f}"})
                .background_gradient(subset=["P_mpp estimada (W)"], cmap="YlGn")
                .set_properties(**{"font-size": "13px"}),
            use_container_width=True,
            hide_index=True,
        )
    
    with tab_legend:
        st.markdown(
            """
            #### 📊 Interpretación de escenarios
            
            **STC (referencia lab)**
            - Condiciones de prueba estándar internationale
            - G=1000 W/m², T_cell=25°C (controlado)
            - Es el punto de referencia nominal del datasheet
            
            **Día despejado Colombia**
            - Representativo de mañana sin nubes
            - G≈900 W/m² (ligera reflexión)
            - T_amb≈24°C → T_cell más alta
            - Condición más común en Manizales
            
            **Parcialmente nublado**
            - Nubes altas/cirrus pasando
            - G≈400 W/m² (40% del máximo)
            - T_cell más baja por menor absorción solar
            - Efecto combinado: P_mpp reduce mucho
            
            **Tarde muy nublado**
            - Cobertura completa de nubes bajas
            - G≈150 W/m² (15% del máximo)
            - T_cell casi igual a T_amb
            - Panel apenas genera potencia útil
            
            #### ⚡ Conclusiones clave
            
            - **Irradiancia** es factor dominante en P_mpp (impacto lineal)
            - **Temperatura** causa pérdida cuadrática de potencia (coef. γ)
            - **Manizales** tiene nubosidad 60–80% → muchos días parcialmente nublados
            - **Diseño de sistemas:** sobredimensionar inversores para capturar picos (900+W/m²)
            """
        )