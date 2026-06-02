# SolarTwin CO - Sprint 3 Mejoras Roadmap
## Plan de Mejoras Ejecutable · Fase Post-Modularización

**Fecha**: 2026-06-02  
**Rama Base**: `JH_DEV`  
**Estado**: ✅ Conflictos resueltos, Tests 48/48 pasando  

---

## 📋 Estado Actual

```
✅ Núcleo Físico: COMPLETO
   - 7 paneles Tier 1 en catálogo
   - Single Diode Model validado
   - Modelos de temperatura (NOCT, Faiman, Sandia)
   - 48/48 tests unitarios e integración pasando

✅ API: COMPLETO (FastAPI)
   - 8 endpoints operacionales
   - Cache inteligente
   - Validación de parámetros

✅ Dashboard: MODULARIZADO
   - Estructura limpia (componentes, páginas, config)
   - 4 páginas funcionales (General, Simulador, Comparador, NOCT)
   - Gráficos Plotly interactivos
   - Sidebar contextual

⚠️ MEJORAS PENDIENTES: 3 fases
```

---

## 🎯 Fase 1: INTERACTIVIDAD EN TIEMPO REAL (2-3 días)

### Tarea 1.1: Simulador Reactivo
**Archivo**: `apps/dashboard/pages/simulator.py`  
**Descripción**: Eliminar botón "Ejecutar", hacer sliders reactivos

- [ ] Modificar session_state para trackear últimos parámetros
- [ ] Detectar cambios en g_poa, t_cell, panel_id automáticamente
- [ ] Ejecutar api_iv_curve y api_pv_curve sin botón
- [ ] Agregar debounce para no saturar API
- [ ] Test: Simular cambio de slider → verificar actualización de gráfico

**Cambios esperados**:
```python
# ANTES
if st.button("Ejecutar"):
    iv_data = api_iv_curve(...)

# DESPUÉS
g_poa = st.slider("...", key="g_poa_sim")
if g_poa != st.session_state.last_g_poa:
    st.session_state.last_g_poa = g_poa
    st.rerun()  # Actualiza automáticamente
```

### Tarea 1.2: Historial de Simulaciones
**Archivo**: `apps/dashboard/pages/simulator.py` (extension)  
**Descripción**: Guardar últimas 10 simulaciones

- [ ] Agregar session_state["sim_history"] (ya existe, mejorarlo)
- [ ] Renderizar tabla con panel_id, g_poa, t_cell, timestamp
- [ ] Botón para "Restaurar" simulación anterior
- [ ] Botón para "Limpiar historial"
- [ ] Persistencia (si es posible con SQLite o solo session)

### Tarea 1.3: Búsqueda y Filtrado de Paneles
**Archivo**: `apps/dashboard/pages/general.py`  
**Descripción**: Agregar search box en catálogo

- [ ] Text input para buscar por nombre/modelo
- [ ] Filter chips por tecnología (TOPCon, PERC, HPBC, etc.)
- [ ] Filter chips por tier (Tier 1, Tier 2)
- [ ] Actualizar tabla en tiempo real

---

## 🎯 Fase 2: EXPORTACIÓN Y ANÁLISIS (2-3 días)

### Tarea 2.1: Exportar Simulación a CSV
**Archivo**: `apps/dashboard/pages/simulator.py`  
**Descripción**: Descargar curva I-V y P-V como CSV

- [ ] Botón "📥 Descargar I-V" en simulador
- [ ] Generar CSV con columnas [v_v, i_a, p_w] + metadata
- [ ] Botón "📥 Descargar P-V"
- [ ] Test: Verificar que CSV se genera con datos correctos

### Tarea 2.2: Exportar Gráficos como PNG
**Archivo**: `apps/dashboard/pages/simulator.py`  
**Descripción**: Captura de pantalla de gráficos

- [ ] Botón "📸 Exportar I-V.png" (Plotly built-in)
- [ ] Botón "📸 Exportar P-V.png"
- [ ] Opción de resolución (72dpi, 300dpi)

### Tarea 2.3: Tabla de Diferencias en Comparador
**Archivo**: `apps/dashboard/pages/comparator.py`  
**Descripción**: Análisis numérico detallado

- [ ] Calcular diferencias absolutas (∆P, ∆V, ∆I) entre paneles
- [ ] Calcular diferencias porcentuales (%, mejora relativa)
- [ ] Renderizar tabla con formato condicional (verde/rojo)
- [ ] Test: Comparar 2 paneles → verificar cálculos

---

## 🎯 Fase 3: ANÁLISIS AVANZADO (3-4 días)

### Tarea 3.1: Heatmap de Sensibilidad
**Archivo**: `apps/dashboard/pages/sensitivity.py` (NEW PAGE)  
**Descripción**: Matriz 10x10 de P_mpp vs G_POA y T_cell

- [ ] Nueva página "🔥 Sensibilidad"
- [ ] Grid G_POA [100:1400] x T_cell [-10:85]
- [ ] Calcular P_mpp para cada combinación (100 puntos)
- [ ] Heatmap interactivo con Plotly
- [ ] Hover tooltip muestra valor exacto
- [ ] Test: Verificar que valores P_mpp son correctos

**Nota**: Esto puede ser LENTO (100 llamadas API). Considerar cache agresivo.

### Tarea 3.2: Curva de Eficiencia vs Temperatura
**Archivo**: `apps/dashboard/pages/simulator.py` (extension)  
**Descripción**: Gráfico η(T) para panel seleccionado

- [ ] Simular curva P_mpp vs T para G_POA fija (1000 W/m²)
- [ ] Mostrar pendiente (dP/dT)
- [ ] Comparar con especificación de catálogo (gamma_pmax)

### Tarea 3.3: Predicción Diaria Simplificada
**Archivo**: `apps/dashboard/pages/simulator.py` (extension)  
**Descripción**: Perfil de potencia típico de un día

- [ ] Generar G_POA(t) para un día típico (curva senoidal + nubes)
- [ ] Calcular T_cell(t) usando Faiman con viento
- [ ] Plotear P_out(t) resultante
- [ ] Calcular energía total producida (kWh)

---

## 🛠️ Tareas Técnicas Transversales

### T.1: Mejorar typing en dashboard
- [ ] Agregar `from typing import Any, Dict, List`
- [ ] Reemplazar `dict` con `dict[str, Any]` en todas partes
- [ ] Mypy check: 0 errores en apps/dashboard

### T.2: Tests para nuevas páginas
- [ ] Crear `tests/unit/test_dashboard_simulator.py`
- [ ] Crear `tests/unit/test_dashboard_comparator.py`
- [ ] Mock de api_iv_curve, api_pv_curve
- [ ] Verificar que componentes se renderizan sin error

### T.3: Optimización de Cache
- [ ] Revisar TTL de @st.cache_data (actualmente 10-60s)
- [ ] Considerar `@st.cache_resource` para cliente HTTP
- [ ] Usar st.session_state para evitar re-fetches innecesarios

### T.4: Documentación
- [ ] Agregar docstrings en funciones de dashboard
- [ ] Crear DASHBOARD_QUICK_START.md para usuarios
- [ ] Agregar ejemplos de curvas esperadas

---

## 📊 Matriz de Prioridad

| Tarea | Impacto | Esfuerzo | Prioridad | Duración |
|-------|---------|----------|-----------|----------|
| 1.1: Simulador Reactivo | 🔴 Alto | 🟢 Bajo | 🔴 P1 | 4h |
| 1.2: Historial | 🟡 Medio | 🟢 Bajo | 🟡 P2 | 2h |
| 1.3: Búsqueda | 🟡 Medio | 🟢 Bajo | 🟡 P2 | 3h |
| 2.1: Exportar CSV | 🟡 Medio | 🟢 Bajo | 🟡 P2 | 3h |
| 2.2: Exportar PNG | 🟢 Bajo | 🟢 Bajo | 🟢 P3 | 1h |
| 2.3: Tabla Diferencias | 🟡 Medio | 🟡 Medio | 🟡 P2 | 4h |
| 3.1: Heatmap | 🔴 Alto | 🔴 Alto | 🟡 P2 | 6h |
| 3.2: Curva η(T) | 🟡 Medio | 🟡 Medio | 🟢 P3 | 3h |
| 3.3: Predicción Diaria | 🟡 Medio | 🔴 Alto | 🟢 P3 | 5h |

---

## 📅 Timeline Recomendado

**Semana 1**:
- Lunes-Martes: Fase 1 (1.1, 1.2, 1.3)
- Miércoles-Viernes: Fase 2 (2.1, 2.2, 2.3)

**Semana 2**:
- Lunes-Martes: Fase 3 (3.1 - Heatmap)
- Miércoles-Viernes: Fase 3 (3.2, 3.3) + Tests finales

**Resultado Final**: Dashboard profesional MVP con capacidades de análisis avanzado

---

## 🚀 Próximos Pasos

1. **Crear rama feature**: `git checkout -b feat/dashboard-interactive-v2`
2. **Implementar Tarea 1.1** primero (máximo impacto rápido)
3. **PR a `JH_DEV` después de 1.1, 1.2, 1.3**
4. **QA y testing** en JH_DEV antes de mergear a main
5. **Documentar** cambios en README.md

---

## 📝 Notas

- ⚠️ El Heatmap (3.1) puede ser LENTO: considerar ejecutar en background o cachear resultados
- ⚠️ No romper API existente: todos los cambios son retrocompatibles
- ✅ Mantener coverage >85% en tests
- ✅ Ejecutar `ruff check . && mypy` antes de cada commit
