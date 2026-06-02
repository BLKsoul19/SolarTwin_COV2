"""Constructores de figuras para curvas I-V."""

from __future__ import annotations

import plotly.graph_objects as go

from .theme import _fig_layout


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
                marker=dict(
                    color=color,
                    size=10,
                    symbol="diamond",
                    line=dict(color="white", width=2),
                ),
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
