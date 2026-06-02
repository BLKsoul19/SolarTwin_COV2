"""Configuración compartida del dashboard SolarTwin CO."""

from __future__ import annotations

API_BASE_URL: str = "http://127.0.0.1:8000"
REQUEST_TIMEOUT: float = 15.0

PAGE_TITLE = "SolarTwin CO"
PAGE_ICON = "☀️"
PAGE_LAYOUT = "wide"
INITIAL_SIDEBAR_STATE = "expanded"
MENU_ITEMS = {
    "Get Help": "https://github.com/your-repo/SolarTwin_COV2",
    "About": "SolarTwin CO · Gemelo digital PV · Eje Cafetero",
}

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

NAVIGATION_PAGES = ["🏠 General", "⚡ Simulador I-V", "🔄 Comparador", "🌡 Análisis NOCT"]

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
