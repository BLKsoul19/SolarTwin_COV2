# IMPLEMENTACIÓN PRÁCTICA: Antes vs Después
## Cambios concretos de código para cada mejora

---

## 1️⃣ MEJORA: Simulador Reactivo (Live-update)

### PROBLEMA ACTUAL
```python
# Página 2: ⚡ Simulador I-V — ANTES
elif page == "⚡ Simulador I-V":
    # ... código de setup ...
    
    with st.sidebar:
        st.markdown("---")
        selected_panel = st.selectbox("Panel", panel_ids)
        g_poa = st.slider("G_POA (W/m²)", 10, 1400, 1000)
        t_cell = st.slider("T_cell (°C)", -10, 85, 25)
        n_points = st.number_input("Resolución", 50, 500, 100)
        
        # ❌ Usuario debe hacer click en botón
        if st.button("▶️ Ejecutar simulación"):
            # Calcular
            iv_resp = api_iv_curve(selected_panel, g_poa, t_cell, n_points)
            # ...
```

**Problema**: Usuario cambia slider → nada pasa → debe hacer click  
**UX**: 3 pasos (cambio + búsqueda + click)  
**Flujo**: Interrumpido, no natural

---

### SOLUCIÓN: Reactividad con session_state

```python
# ============================================================================
# NUEVA SECCIÓN AL INICIO DEL SCRIPT (después de imports)
# ============================================================================

# Inicializar session state para simulador
if "sim_state" not in st.session_state:
    st.session_state.sim_state = {
        "g_poa": 1000,
        "t_cell": 25,
        "n_points": 100,
        "last_panel": None,
        "needs_update": True,
    }

# ============================================================================
# PÁGINA 2: SIMULADOR REACTIVO — DESPUÉS
# ============================================================================

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

        # Panel selection (may trigger update)
        selected_panel = st.selectbox(
            "Panel",
            panel_ids,
            key="sel_panel_sim"
        )

        # Sliders with reactive keys
        g_poa = st.slider(
            "Irradiancia G_POA (W/m²)",
            min_value=10,
            max_value=1400,
            value=st.session_state.sim_state["g_poa"],
            step=10,
            key="g_poa_sim",  # ← Reactive key
        )

        t_cell = st.slider(
            "Temperatura T_cell (°C)",
            min_value=-10,
            max_value=85,
            value=st.session_state.sim_state["t_cell"],
            step=1,
            key="t_cell_sim",  # ← Reactive key
        )

        n_points = st.number_input(
            "Resolución curva (puntos)",
            min_value=50,
            max_value=500,
            value=st.session_state.sim_state["n_points"],
            step=10,
            key="n_points_sim",
        )

    # ── DETECTOR AUTOMÁTICO DE CAMBIOS ──
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
    if not panel_ids:
        st.error("API no disponible o catálogo vacío.")
        st.stop()

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

    # ... resto del código (gráficos, métricas, etc.) sin cambios ...
```

**Resultado**:
- ✅ Sliders actualizan automáticamente (sin botón)
- ✅ Feedback instantáneo (<1 segundo)
- ✅ Flujo natural: cambio → resultado
- ✅ Session state persiste durante sesión

---

## 2️⃣ MEJORA: Historial de Simulaciones

### CÓDIGO A AGREGAR

```python
# ============================================================================
# INICIALIZACIÓN DE HISTORIAL (al inicio del script, después de session_state)
# ============================================================================

if "sim_history" not in st.session_state:
    st.session_state.sim_history = []

# ============================================================================
# EN PÁGINA 2: SIMULADOR (DESPUÉS DE LOS GRÁFICOS)
# ============================================================================

st.markdown("---")

# Guardar simulación en historial
if panel_data and iv_data:
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
                "p_mp_w": iv_data.get("p_mp_w", 0),
                "v_mp_v": iv_data.get("v_mp_v", 0),
                "i_mp_a": iv_data.get("i_mp_a", 0),
                "efficiency_loss_pct": (
                    ((iv_data.get("p_mp_w", 1) - panel_data.get("pmax_stc_w", 1)) /
                     panel_data.get("pmax_stc_w", 1) * 100)
                    if panel_data.get("pmax_stc_w") else 0
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
```

**Resultado**:
- ✅ Últimas 10 simulaciones guardadas
- ✅ Botón para recargar simulación anterior
- ✅ Exportar historial a CSV
- ✅ Notas opcionales para cada simulación

---

## 3️⃣ MEJORA: Búsqueda & Filtro de Paneles

### CÓDIGO A AGREGAR EN PÁGINA 3 (COMPARADOR)

```python
# ============================================================================
# PÁGINA 3: COMPARADOR CON BÚSQUEDA
# ============================================================================

elif page == "🔄 Comparador":

    panels_resp = api_list_panels()
    panels = panels_resp.get("data", []) if panels_resp["ok"] else []
    panel_ids = [p["panel_id"] for p in panels] if panels else []

    if len(panel_ids) < 2:
        st.warning("Se requieren al menos 2 paneles en el catálogo para comparar.")
        st.stop()

    # ── BÚSQUEDA Y FILTRADO ──
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
    if "fav_panels" not in st.session_state:
        st.session_state.fav_panels = []

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

    # ... resto del código de comparación (gráficos, tablas, etc.) sin cambios ...
```

**Resultado**:
- ✅ Búsqueda en tiempo real
- ✅ Filtro por Tier
- ✅ Botones ⭐ para favoritos
- ✅ Acceso rápido a últimos paneles usados

---

## 4️⃣ MEJORA: Exportación de Datos (CSV, JSON, Excel)

### CÓDIGO A AGREGAR EN PÁGINA 2 (SIMULADOR)

```python
# ============================================================================
# EN PÁGINA 2: SIMULADOR (NUEVA SECCIÓN DESPUÉS DE TABLA DE PARÁMETROS)
# ============================================================================

# Agregar al final de la página 2, después de mostrar resultados

if panel_data and iv_data and pv_data:
    st.markdown("---")
    st.markdown(
        '<div class="section-title">📥 Exportar resultados</div>',
        unsafe_allow_html=True,
    )

    col_csv, col_json, col_xlsx, col_png = st.columns(4)

    # ── EXPORTAR CSV ──
    with col_csv:
        # Preparar datos
        export_df = pd.DataFrame({
            "Voltaje_V": iv_data.get("v_v", []),
            "Corriente_A": iv_data.get("i_a", []),
            "Potencia_W": pv_data.get("p_w", []),
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
                "v_mp_v": iv_data.get("v_mp_v"),
                "i_mp_a": iv_data.get("i_mp_a"),
                "p_mp_w": iv_data.get("p_mp_w"),
                "v_oc_v": iv_data.get("v_oc_v"),
                "i_sc_a": iv_data.get("i_sc_a"),
            },
            "curves": {
                "iv": {
                    "v_v": iv_data.get("v_v", []),
                    "i_a": iv_data.get("i_a", []),
                },
                "pv": {
                    "v_v": pv_data.get("v_v", []),
                    "p_w": pv_data.get("p_w", []),
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
                "V (V)": iv_data.get("v_v", []),
                "I (A)": iv_data.get("i_a", []),
            })
            df_iv.to_excel(writer, sheet_name="IV Curve", index=False)
            
            # Sheet 2: Curva P-V
            df_pv = pd.DataFrame({
                "V (V)": pv_data.get("v_v", []),
                "P (W)": pv_data.get("p_w", []),
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
                    f"{iv_data.get('v_mp_v', 0):.2f}",
                    f"{iv_data.get('i_mp_a', 0):.3f}",
                    f"{iv_data.get('p_mp_w', 0):.1f}",
                    f"{iv_data.get('v_oc_v', 0):.2f}",
                    f"{iv_data.get('i_sc_a', 0):.3f}",
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

    # ── EXPORTAR PNG (Gráficos) ──
    with col_png:
        st.download_button(
            label="🖼️ PNG (gráficos)",
            data=None,  # Plotly auto-genera en cliente
            file_name=f"curves_{selected_panel}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
            help="Click en 🎥 (camera icon) en gráficos para descargar",
            key="btn_export_png",
            disabled=True,  # Plotly maneja esto automáticamente
        )
        st.caption("Use el botón 📷 de cada gráfico para descargar PNG")
```

**Resultado**:
- ✅ CSV para análisis rápido
- ✅ JSON estructurado para integración
- ✅ Excel multi-sheet para reportes
- ✅ PNG nativo de Plotly

---

## 5️⃣ MEJORA: Anotaciones en Simulaciones

### CÓDIGO YA INCLUIDO EN MEJORA #2

Ver sección "Historial de Simulaciones" arriba (parámetro `sim_note`).

---

## 📦 IMPORTS NECESARIOS (Agregar al inicio del archivo)

```python
from datetime import datetime
import json
import io
import pandas as pd
import numpy as np
```

---

## 📋 CHECKLIST DE IMPLEMENTACIÓN

```
✅ Mejora 1: Simulador Reactivo
   ├─ Crear st.session_state.sim_state al inicio
   ├─ Cambiar botón ▶️ por detección automática de cambios
   ├─ Usar st.rerun() para actualizar (Streamlit 1.27+)
   └─ Testear: Cambiar sliders debe redibujar gráficos

✅ Mejora 2: Historial de Simulaciones
   ├─ Crear st.session_state.sim_history al inicio
   ├─ Agregar botón "💾 Guardar" + text_input para notas
   ├─ Mostrar expander "📜 Historial" con tabla
   ├─ Botones: [🔄 Recargar] [📥 Exportar CSV] [🗑️ Limpiar]
   └─ Testear: Guardar 5 simulaciones y verificar historial

✅ Mejora 3: Búsqueda & Filtro
   ├─ Agregar text_input "🔍 Buscar panel"
   ├─ Agregar multiselect para Tier
   ├─ Filtrar panel_ids antes de selectbox
   ├─ Agregar favoritos (st.session_state.fav_panels)
   └─ Testear: Buscar "jinko" debe mostrar solo ese panel

✅ Mejora 4: Exportación de Datos
   ├─ Crear CSV con V, I, P
   ├─ Crear JSON con metadata + curvas
   ├─ Crear Excel con múltiples sheets
   ├─ Botones de download para cada formato
   └─ Testear: Descargar y abrir en Excel

✅ Mejora 5: Anotaciones
   ├─ Incluida en Mejora 2 (field sim_note)
   └─ Mostrar notas en historial expander

Testing general:
  ├─ Ejecutar: streamlit run apps/dashboard/main.py
  ├─ Verificar que los 4 cambios no rompan nada
  ├─ Probar cada mejora independientemente
  └─ Validar performance (cache sigue funcionando)
```

---

## 🚀 PRÓXIMOS PASOS

1. **Copiar** las secciones de código arriba
2. **Editar** `/workspaces/SolarTwin_COV2/apps/dashboard/main.py`
3. **Testear** localmente: `streamlit run apps/dashboard/main.py`
4. **Validar** que cada mejora funcione
5. **Commit** con mensaje claro: `feat: add reactive simulator + history`

---

**Documento**: Implementation Guide - Antes vs Después  
**Versión**: 1.0  
**Estado**: ✅ LISTO PARA COPIAR Y PEGAR
