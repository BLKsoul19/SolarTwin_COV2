"""
SolarTwin CO — Dashboard Streamlit
===================================
Gemelo digital de paneles fotovoltaicos · Eje Cafetero, Colombia.
Gemelo digital de paneles fotovoltaicos · Eje Cafetero, Colombia.

Ejecución:
  uvicorn apps.api.main:app --reload --port 8000   # Terminal 1
  streamlit run apps/dashboard/main.py             # Terminal 2
"""

from __future__ import annotations

import streamlit as st
<<<<<<< ours
<<<<<<< ours
<<<<<<< ours

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
=======
=======
>>>>>>> theirs
=======
>>>>>>> theirs
from charts.iv import build_iv_fig
from charts.pv import build_pv_fig
from charts.theme import _fig_layout

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
>>>>>>> theirs
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


main()
}