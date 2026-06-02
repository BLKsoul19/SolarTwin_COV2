from __future__ import annotations

import io
import json
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from apps.dashboard.api_client import (
    api_get_panel,
    api_iv_curve,
    api_list_panels,
    api_pv_curve,
)
from apps.dashboard.charts import _fig_layout, build_iv_fig, build_pv_fig
from apps.dashboard.config import COLORS, DEFAULT_COLOR, PANEL_COLORS


def render_simulator() -> None:
    """Renderiza la página simulator."""

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
