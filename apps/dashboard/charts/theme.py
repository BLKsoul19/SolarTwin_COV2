"""Tema Plotly compartido para los gráficos del dashboard SolarTwin."""

from __future__ import annotations

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


def _fig_layout(**overrides: object) -> dict[str, object]:
    """Retorna el layout base Plotly con overrides específicos por figura."""
    layout = dict(PLOTLY_LAYOUT_BASE)
    layout.update(overrides)
    return layout
