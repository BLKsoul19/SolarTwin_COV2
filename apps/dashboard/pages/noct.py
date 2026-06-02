from __future__ import annotations


import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from apps.dashboard.api_client import (
    api_cell_temperature,
    api_get_panel,
    api_list_panels,
)
from apps.dashboard.charts import _fig_layout
from apps.dashboard.config import COLORS


def render_noct() -> None:
    """Renderiza la página noct."""

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
                hovertemplate="G: %{x} W/m²<br>T_cell: %{y:.1f} °C<extra></extra>",
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
