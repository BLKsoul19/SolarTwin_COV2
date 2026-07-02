# Checklist de revisión de Pull Request

Usa este checklist para revisar PRs y mantener la calidad del proyecto.

## Antes de abrir el PR

- [ ] Creada rama específica con nombre descriptivo.
- [ ] Commit messages claros y enfocados.
- [ ] Issue creado si el cambio es relevante.
- [ ] Documentación actualizada si aplica.

## Verificación del código

- [ ] El código está formateado con `ruff format`.
- [ ] No hay advertencias de `ruff check`.
- [ ] Se ejecutaron pruebas locales.
- [ ] El tipado con `mypy` no muestra errores nuevos.
- [ ] Se probó el path principal de la funcionalidad.

## Contenido del PR

- [ ] Título claro y descriptivo.
- [ ] Descripción concisa del cambio.
- [ ] Lista de verificación con pasos de validación.
- [ ] Enlace a issue relacionado si existe.
- [ ] Impacto en la documentación documentado.

## Revisión técnica

- [ ] El cambio respeta la separación de responsabilidades.
- [ ] No se introducen dependencias innecesarias.
- [ ] Se validan todos los casos relevantes.
- [ ] Si hay nuevo comportamiento, está cubierto con pruebas.
- [ ] Si es un cambio en datos/datos de catálogo, se revisa el versionado.

## Aprobación

- [ ] La CI pasa en el PR.
- [ ] El código fue revisado por al menos una persona.
- [ ] No hay conflictos de merge pendientes.
- [ ] El PR está listo para fusionar.
