from __future__ import annotations


import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from apps.dashboard.api_client import (
    api_iv_curve,
    api_list_panels,
    api_pv_curve,
)
from apps.dashboard.charts import _fig_layout
from apps.dashboard.config import COLORS


def render_comparator() -> None:
    """Renderiza la página comparator."""

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
