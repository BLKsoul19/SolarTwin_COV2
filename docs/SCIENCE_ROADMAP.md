# Roadmap Científico SolarTwin CO

Este documento define los próximos pasos científicos y técnicos para evolucionar el proyecto desde un prototipo funcional hacia una plataforma de análisis fotovoltaico profesional.

## Fase 1 — Núcleo físico y validación

### Objetivos
- Asegurar que el modelo de un diodo simple (SDM) sea consistente con datos de paneles reales.
- Verificar la temperatura de celda y el comportamiento térmico bajo diferentes condiciones.
- Validar la tabla de parámetros de paneles en `data/panels/`.

### Entregables
- `tests/unit/test_single_diode.py` con comparaciones físicas adicionales.
- `tests/unit/test_temperature.py` con casos NOCT y Faiman.
- `docs/NOCT_MODEL_PHYSICS.md` revisado y ampliado.
- Pruebas de humo en `tests/smoke_test.py` documentadas.

## Fase 2 — Dashboard y UX

### Objetivos
- Mejorar la experiencia de uso del dashboard sin sacrificar la reproducibilidad.
- Hacer el dashboard más informativo y menos «vacío».
- Agregar análisis de sensibilidad simple y exportación de resultados.

### Entregables
- Interactividad reactiva con `st.session_state`.
- Historial de simulaciones en la UI.
- Comparador de paneles con filtros y búsqueda.
- Documentación de uso de la app en `docs/DASHBOARD_QUICK_REFERENCE.md`.

## Fase 3 — GitHub y calidad del proyecto

### Objetivos
- Establecer un flujo de trabajo GitHub robusto y fácil de seguir.
- Mantener la calidad del código con CI, pruebas y review.
- Publicar releases con versionado semántico.

### Entregables
- `docs/GITHUB_WORKFLOW.md` completado y referenciado en el README.
- `docs/PR_REVIEW_CHECKLIST.md` con criterios científicos y técnicos.
- `.github/workflows/release.yml` funcionando.
- `CONTRIBUTING.md` con reglas de ramas y etiquetas.

## Fase 4 — Análisis de datos y decisiones

### Objetivos
- Agregar métricas clave para decisiones de rendimiento.
- Preprocesar datos de paneles para comparativas significativas.
- Facilitar análisis de sensibilidad G/T y pérdidas térmicas.

### Entregables
- `apps/dashboard/pages/analysis.py` o similar.
- Funciones de KPI en `packages/pv-twin/src/pv_twin/kpi/`.
- Tablero de métricas de rendimiento, eficiencia y PR.
- Informes básicos exportables en CSV/JSON.

## Recomendaciones de trabajo

- Mantener cada cambio en ramas pequeñas y revisables.
- Acompañar los cambios con pruebas concretas y resultados numéricos.
- Documentar supuestos físicos y limitaciones de los modelos.
- Usar `issue` + `PR` para coordinar cambios de mayor alcance.

## Prioridades inmediatas

1. Consolidar `feature/science-roadmap` con el siguiente entregable:
   - Documento `docs/SCIENCE_ROADMAP.md`
   - Nueva rama de trabajo para análisis científico
2. Verificar `main` y `develop` como base limpia.
3. Aplicar el checklist del PR actual para asegurar una integración ordenada.
