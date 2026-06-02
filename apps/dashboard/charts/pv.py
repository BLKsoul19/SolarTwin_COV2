"""Constructores de figuras para curvas P-V."""

from __future__ import annotations

import plotly.graph_objects as go

from .theme import _fig_layout


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
            fillcolor=(
                color.replace(")", ", 0.08)").replace("rgb", "rgba")
                if color.startswith("rgb")
                else color + "14"
            ),
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
                marker=dict(
                    color=color,
                    size=10,
                    symbol="diamond",
                    line=dict(color="white", width=2),
                ),
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
