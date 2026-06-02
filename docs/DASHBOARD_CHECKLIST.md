# SolarTwin CO Dashboard - Checklist de Implementación

## Fase 1: Setup Inicial (4-6 horas)

### 1.1 Estructura de Carpetas
```
- [ ] Crear directorio: apps/dashboard/
- [ ] Crear subdirectorio: apps/dashboard/pages/
- [ ] Crear subdirectorio: apps/dashboard/components/
- [ ] Crear archivo: apps/dashboard/config.py
- [ ] Crear archivo: apps/dashboard/constants.py
- [ ] Crear archivo: apps/dashboard/main.py
```

### 1.2 Configuración Streamlit
```
- [ ] Crear: apps/dashboard/.streamlit/config.toml
  └─ Configurar tema, puerto 8501, altura máxima
- [ ] Crear: apps/dashboard/requirements.txt
  └─ streamlit>=1.35
  └─ plotly>=5.17
  └─ pandas>=2.2
  └─ httpx>=0.27
```

### 1.3 Conexión a API
```
- [ ] Crear cliente HTTP wrapper en config.py
- [ ] Implementar manejo de errores centralizado
- [ ] Crear funciones de cache (@st.cache_resource)
- [ ] Validar conexión a http://localhost:8000
```

---

## Fase 2: Página Home (4-6 horas)

### 2.1 Layout Base
```
- [ ] Configurar st.set_page_config()
- [ ] Crear sidebar con navegación
- [ ] Agregar logo/branding SolarTwin
- [ ] Implementar multi-page routing
```

### 2.2 KPI Metrics
```
- [ ] Métrica: Paneles disponibles (con conteo)
- [ ] Métrica: API Status (online/offline)
- [ ] Métrica: Versión del sistema
- [ ] Métrica: Última actualización
```

### 2.3 Panel Grid
```
- [ ] Llamada a GET /api/v1/twin/panels
- [ ] Renderizar DataFrame con pandas
- [ ] Columnas: panel_id, pmax_stc_w, voc_stc_v, isc_stc_a, noct_c, tier, technology
- [ ] Formateo de números con precisión
- [ ] Manejo de errores con st.error()
```

### 2.4 Status Cards
```
- [ ] Card: API Connection Status
- [ ] Card: Data Quality Score
- [ ] Card: Last Sync Timestamp
- [ ] Visuales: Color coding (green/red/yellow)
```

---

## Fase 3: Página Simulation (8-12 horas)

### 3.1 Sidebar Controls
```
- [ ] Selector de panel (dropdown)
- [ ] Slider G_POA (10-1400, step=50)
- [ ] Slider T_cell (-10-85, step=5)
- [ ] Slider n_points (10-500, step=10)
- [ ] Botón: "Run Simulation"
```

### 3.2 Gráfico I-V Curve
```
- [ ] Plotly figure con scatter line
- [ ] Eje X: Voltaje (V)
- [ ] Eje Y: Corriente (A)
- [ ] Hover info: V, I, P para cada punto
- [ ] Subrayar punto MPP (color diferente)
- [ ] Legend: "I-V Curve @ G={g_poa}W/m², T={t_cell}°C"
```

### 3.3 Gráfico P-V Curve
```
- [ ] Plotly figure con scatter line + fill
- [ ] Eje X: Voltaje (V)
- [ ] Eje Y: Potencia (W)
- [ ] Fill to zero para visualizar área
- [ ] Hover info: V, P
- [ ] Marcar Vmpp con línea vertical
- [ ] Legend: "P-V Curve @ G={g_poa}W/m², T={t_cell}°C"
```

### 3.4 Tabla de Parámetros
```
Columnas:
- [ ] Parámetro (nombre)
- [ ] Valor (numérico)
- [ ] Unidad (V, A, W, W/m², °C, %)

Filas:
- [ ] Voc [V]
- [ ] Isc [A]
- [ ] Vmpp [V]
- [ ] Impp [A]
- [ ] Pmpp [W]
- [ ] G_POA [W/m²]
- [ ] T_cell [°C]
- [ ] Eficiencia vs STC [%]
```

### 3.5 Error Handling
```
- [ ] Try-except para timeout (>10s)
- [ ] Try-except para validación (G_POA out of range)
- [ ] Try-except para panel no encontrado (404)
- [ ] Mensajes de error en st.error()
- [ ] Warnings en st.warning()
```

---

## Fase 4: Página Comparison (6-8 horas)

### 4.1 Multi-Panel Selector
```
- [ ] 3 selectboxes para panel selection
- [ ] Panel 1, Panel 2, Panel 3 (independientes)
- [ ] Permitir mismo panel en múltiples slots
- [ ] Update en tiempo real
```

### 4.2 Controles Comunes
```
- [ ] Slider G_POA (compartido)
- [ ] Slider T_cell (compartido)
- [ ] Botón: "Compare"
```

### 4.3 Gráficos Superpuestos
```
Columna 1: I-V Curves
- [ ] 3 líneas con colores diferentes
- [ ] Legend: Panel 1 (blue), Panel 2 (green), Panel 3 (red)
- [ ] Mismos ejes para comparación fácil

Columna 2: P-V Curves
- [ ] 3 líneas con mismos colores
- [ ] Resaltar Pmpp de cada panel

Columna 3: Scatter Comparativo
- [ ] X: Vmpp [V]
- [ ] Y: Pmpp [W]
- [ ] Tamaño de punto: Isc
- [ ] Color: Panel
```

### 4.4 Tabla Comparativa
```
- [ ] Filas: Parámetros (Pmax, Voc, Isc, Vmpp, Impp, γ, NOCT)
- [ ] Columnas: Panel 1, Panel 2, Panel 3
- [ ] Formateo: Diferencias en % (vs Panel 1)
- [ ] Resaltar mejor valor de cada parámetro
```

### 4.5 Export
```
- [ ] Botón: "Export to CSV"
- [ ] Botón: "Export to PNG" (gráficos)
- [ ] Nombre archivo: comparison_{timestamp}.csv
```

---

## Fase 5: Página Analysis (8-10 horas)

### 5.1 Selector de Escenarios
```
- [ ] Dropdown: Clima (Dry, Temperate, Tropical)
- [ ] Dropdown: Altitud (1000m, 1500m, 2000m)
- [ ] Slider: Cloud Coverage (0%-100%)
- [ ] Botón: "Run Analysis"
```

### 5.2 Parámetros Preconfigurados
```
Por clima:
- [ ] Dry: T_amb=35°C, Cloud=10%, GHI_peak=1100 W/m²
- [ ] Temperate: T_amb=20°C, Cloud=50%, GHI_peak=900 W/m²
- [ ] Tropical: T_amb=28°C, Cloud=80%, GHI_peak=850 W/m²

Por altitud:
- [ ] 1000m: NOCT_correction=0°C
- [ ] 1500m: NOCT_correction=+1°C
- [ ] 2000m: NOCT_correction=+2°C
```

### 5.3 Simulación de Día Típico
```
- [ ] Generar array horario (6am-6pm, step=1h)
- [ ] Para cada hora: calcular G_POA(hora) → T_cell → IV curve
- [ ] Gráfico 1: Irradiancia horaria (GHI, POA)
- [ ] Gráfico 2: Temperatura de célula (T_cell vs hora)
- [ ] Gráfico 3: Potencia generada vs hora
- [ ] Tabla: Resumen horario (Hora, G_POA, T_cell, P_max)
```

### 5.4 Análisis de Pérdidas
```
Tabla de pérdidas:
- [ ] Pérdida térmica vs STC [%]
- [ ] Pérdida por ángulo [%] (si G_POA < max)
- [ ] Pérdida por espectro (si nubosidad > 50%)
- [ ] Total pérdida estimada [%]
```

### 5.5 Modelos NOCT Visuales
```
- [ ] Gráfico: Ross-NOCT T_cell vs G_POA (con ecuación)
- [ ] Gráfico: Pérdida de eficiencia vs temperatura
- [ ] Tabla: Comparación NOCT entre paneles a mismas condiciones
```

---

## Fase 6: Página About (2-3 horas)

### 6.1 Sistema Info
```
- [ ] Versión del sistema
- [ ] Versión del API
- [ ] Versión del modelo físico
- [ ] Timestamp de build
```

### 6.2 Paneles Disponibles
```
- [ ] Tabla con count por Tier
- [ ] Detalles: Panel ID, Pmax, Technology, NOCT
- [ ] Link a datasheet (si disponible)
```

### 6.3 Especificaciones Técnicas
```
- [ ] Modelo: Single Diode Model
- [ ] Parámetros: CEC 5-parámetros
- [ ] Temperatura: Ross-NOCT
- [ ] Radiación: POA transposición
- [ ] Localización: Eje Cafetero, Colombia
```

### 6.4 Documentación Links
```
- [ ] Link: NOCT_MODEL_PHYSICS.md
- [ ] Link: PANEL_TIER1_SETUP.md
- [ ] Link: README.md
- [ ] Link: GitHub repository
```

---

## Fase 7: Utilities & Infrastructure (4-6 horas)

### 7.1 config.py
```python
- [ ] API_BASE_URL = "http://localhost:8000"
- [ ] TIMEOUT_SECONDS = 10
- [ ] CACHE_TTL = 3600
- [ ] MAX_RETRIES = 3
- [ ] THEME_COLORS (primary, secondary, success, error)
```

### 7.2 components/charts.py
```
- [ ] plot_iv_curve(data, title)
- [ ] plot_pv_curve(data, title)
- [ ] plot_comparison_iv(data_list, titles)
- [ ] plot_daily_generation(hourly_data)
- [ ] plot_efficiency_loss(temp_range)
```

### 7.3 components/inputs.py
```
- [ ] panel_selector()
- [ ] irradiance_slider()
- [ ] temperature_slider()
- [ ] resolution_slider()
- [ ] scenario_selector()
```

### 7.4 components/stats.py
```
- [ ] kpi_metric(label, value, unit, delta)
- [ ] status_card(title, status, message)
- [ ] efficiency_gauge(efficiency_percent)
```

### 7.5 Error Handling Wrapper
```python
- [ ] @retry_on_timeout
- [ ] @handle_api_errors
- [ ] @cache_with_error_fallback
```

---

## Fase 8: Testing & Refinement (4-6 horas)

### 8.1 Manual Testing
```
- [ ] Test cada página carga sin errores
- [ ] Test sliders funcionen correctamente
- [ ] Test dropdowns actualicen gráficos
- [ ] Test números se formateen correctamente
- [ ] Test error messages se muestren apropiadamente
```

### 8.2 Browser Testing
```
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (si disponible)
- [ ] Mobile responsive (opcional para MVP)
```

### 8.3 API Integration Testing
```
- [ ] Test con API offline (error handling)
- [ ] Test con panel inexistente (404)
- [ ] Test con parámetros inválidos (422)
- [ ] Test timeout (>10s)
- [ ] Test diferentes valores de G_POA, T_cell
```

### 8.4 Performance Testing
```
- [ ] Dashboard inicial load: < 3s
- [ ] Gráfico render: < 2s
- [ ] Slider interaction: smooth (sin lag)
- [ ] Memory usage: < 500MB
```

---

## Fase 9: Documentation (2-3 horas)

### 9.1 User Guide
```
- [ ] Cómo ejecutar dashboard
- [ ] Descripción de cada página
- [ ] Explicación de parámetros
- [ ] Interpretación de resultados
- [ ] Troubleshooting
```

### 9.2 Developer Guide
```
- [ ] Architecture overview
- [ ] File structure
- [ ] Adding new pages
- [ ] Component reusability
- [ ] Common pitfalls
```

### 9.3 README Dashboard
```
- [ ] Setup instructions
- [ ] Dependencies
- [ ] Running locally
- [ ] Building for production
- [ ] Screenshots/GIFs
```

---

## Fase 10: Deployment (3-4 horas)

### 10.1 Local Deployment
```
- [ ] Validar requirements.txt completo
- [ ] Test venv aislado
- [ ] Script start.sh para ambos (API + Dashboard)
```

### 10.2 Streamlit Cloud (Optional)
```
- [ ] Crear cuenta Streamlit Cloud
- [ ] Conectar GitHub repository
- [ ] Deploy main branch
- [ ] Validar en https://app.streamlit.io
- [ ] Configurar secrets (API_URL si es remota)
```

### 10.3 Docker (Optional)
```
- [ ] Crear Dockerfile para dashboard
- [ ] Docker compose: API + Dashboard
- [ ] Test con: docker-compose up
```

---

## Estimación de Horas

| Fase | Horas | Días (8h/día) |
|------|-------|--------------|
| 1. Setup | 5 | 0.6 |
| 2. Home | 5 | 0.6 |
| 3. Simulation | 10 | 1.3 |
| 4. Comparison | 7 | 0.9 |
| 5. Analysis | 9 | 1.1 |
| 6. About | 2.5 | 0.3 |
| 7. Utilities | 5 | 0.6 |
| 8. Testing | 5 | 0.6 |
| 9. Documentation | 2.5 | 0.3 |
| 10. Deployment | 3.5 | 0.4 |
| **TOTAL** | **54** | **7 días (1.4 sprints)** |

---

## Timeline Sugerido

```
Semana 1:
└─ Día 1-2: Fases 1-2 (Setup + Home)
└─ Día 3-4: Fase 3 (Simulation)
└─ Día 5: Fase 4 (Comparison)

Semana 2:
└─ Día 1-2: Fase 5 (Analysis)
└─ Día 3: Fases 6-7 (About + Utils)
└─ Día 4-5: Fases 8-10 (Testing + Deploy)

Total: ~10 días de desarrollo (1-2 sprints dedicados)
```

---

## Criterios de Aceptación

### Mínimo MVP (Semana 1)
- [x] Todas las páginas navegan sin errores
- [x] Home muestra paneles correctamente
- [x] Simulation genera gráficos I-V y P-V
- [x] API conecta correctamente
- [x] Error handling básico funciona

### Completo (Semana 2)
- [x] Todas las funcionalidades del plan implementadas
- [x] Testing manual completado
- [x] Documentación básica escrita
- [x] Deployment en localhost funcionando
- [x] Zero console errors/warnings

### Production-Ready (Post-MVP)
- [ ] Performance benchmarks < 2s por gráfico
- [ ] Responsive design (opcional)
- [ ] Containerization (Docker)
- [ ] CI/CD workflow
- [ ] Unit tests para componentes críticos

---

## Priorización Fallback

Si falta tiempo:

```
MUST HAVE (Semana 1):
├─ Home page
├─ Simulation (I-V + P-V básicas)
└─ Error handling

SHOULD HAVE (Semana 2):
├─ Comparison page
├─ Analysis page
└─ About page

NICE TO HAVE (Sprint 4+):
├─ Export to PDF/PNG
├─ Theme customization
├─ Mobile responsive
└─ Analytics tracking
```

---

**Documento**: Dashboard Implementation Checklist  
**Versión**: 1.0  
**Actualización**: 2026-05-25  
**Estado**: ✅ LISTO PARA INICIAR SPRINT 3  
