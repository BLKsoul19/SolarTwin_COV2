# Contribuir a SolarTwin CO

Gracias por interesarte en este proyecto. SolarTwin CO es un proyecto científico-industrial que mezcla modelado físico, datos y UX; por eso buscamos contribuciones bien estructuradas y reproducibles.

## Flujo recomendado

1. Crea un issue si el cambio es relevante o requiere discusión.
2. Crea una rama específica desde `develop` o `main` según corresponda.
3. Implementa cambios pequeños y enfocados.
4. Añade o actualiza pruebas unitarias/integración cuando sea posible.
5. Actualiza la documentación si el comportamiento, API o flujo de datos cambia.
6. Abre un pull request usando la plantilla de PR.
7. Espera la revisión y corrige los comentarios antes de fusionar.

## Nomenclatura de ramas

Usa nombres claros y coherentes:

- `feature/<descripción>` para nuevas funcionalidades.
- `fix/<descripción>` para correcciones de bug.
- `docs/<descripción>` para cambios de documentación.
- `research/<descripción>` para experimentos o análisis de datos.
- `hotfix/<descripción>` para correcciones urgentes en `main`.
- `release/<versión>` para preparar versiones.

Ejemplos:

- `feature/dashboard-search-panel`
- `fix/api-panel-endpoint`
- `docs/github-workflow`
- `research/noct-thermal-fit`

## Etiquetas y categorías

Usa estas etiquetas en issues y PRs para facilitar la priorización:

- `bug`
- `enhancement`
- `documentation`
- `research`
- `performance`
- `test`
- `good first issue`
- `needs review`
- `needs testing`
- `blocked`

## Checklist de PR

Antes de enviar un pull request, asegúrate de:

- [ ] Incluir un título claro y una descripción concisa.
- [ ] Explicar por qué el cambio es necesario.
- [ ] Referenciar el issue relacionado cuando exista.
- [ ] Añadir pruebas si el cambio afecta funcionalidad.
- [ ] Incluir pasos de validación en la descripción del PR.
- [ ] Verificar que no hayas roto tests existentes.
- [ ] Confirmar que la documentación se actualizó si es necesario.

## Requisitos locales

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## Verificación mínima

Ejecuta siempre estas comprobaciones:

```bash
pytest tests/unit tests/integration -q
ruff check .
ruff format . --check
mypy packages/pv-twin/src/pv_twin apps
```

Si trabajas en el dashboard localmente, también valida:

```bash
streamlit run apps/dashboard/main.py
```

## Criterios de revisión específicos para SolarTwin CO

### Calidad de código

- Mantén el código claro y legible.
- Usa nombres descriptivos con unidades cuando corresponda (`g_poa_w_m2`, `t_cell_c`, `p_dc_w`).
- Evita variables ambiguas como `G`, `T`, `P`, `E` sin unidades.
- Sigue el line-length de `ruff` y las reglas de estilo del repositorio.

### Ciencia y datos

- Documenta supuestos físicos y fuentes de datos.
- Valida los resultados con pruebas numéricas, no solo con valores no nulos.
- Si agregas o modificas paneles, actualiza la información de `data/panels/` y verifica las claves esperadas.
- Para cambios en modelos físicos, agrega casos de prueba que cubran límites y comportamiento físico.

### Documentación

- Cualquier cambio de comportamiento debe reflejarse en `README.md`, `docs/` o `apps/dashboard` si aplica.
- Usa el formato de la plantilla de PR para describir qué se hizo y cómo verificarlo.
- En el dashboard, agrega textos UX breves para que el usuario entienda qué hace cada control.

### Pull request y merge

- Los PRs deben revisarse antes de fusionar.
- Evita merges directos a `main` salvo hotfixes críticos.
- Usa la rama `develop` o `JH_DEV` para trabajo en curso y características integradas.
- Asegúrate de que la CI en GitHub pase antes del merge.

## Cómo trabajar con datos de paneles

- Añade nuevos paneles como archivos JSON en `data/panels/`.
- Mantén el catálogo versionado con nombres descriptivos.
- Valida que el panel tenga todos los campos esperados por la API y el dashboard.
- No modifiques valores históricos sin documentación de por qué cambian.

## Recursos útiles

- `docs/GITHUB_WORKFLOW.md` — Flujo de ramas, PRs y releases.
- `docs/PR_REVIEW_CHECKLIST.md` — Checklist de revisión de PR.
- `.github/pull_request_template.md` — Plantilla para PRs.
- `.github/ISSUE_TEMPLATE/` — Plantillas de issues.
- `README.md` — Guía de uso y setup.

Gracias por contribuir a SolarTwin CO. Tu aporte ayuda a convertir este proyecto científico en una herramienta profesional y confiable.
