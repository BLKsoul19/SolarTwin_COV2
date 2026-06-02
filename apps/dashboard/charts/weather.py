"""Punto de extensión para futuros gráficos meteorológicos del dashboard.

Este módulo centralizará los constructores Plotly de señales meteorológicas para
mantener las páginas Streamlit como consumidoras de figuras ya preparadas.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WeatherChartSpec:
    """Describe un gráfico meteorológico planificado para el dashboard."""

    key: str
    title: str
    purpose: str


WEATHER_CHART_SPECS: tuple[WeatherChartSpec, ...] = (
    WeatherChartSpec(
        key="irradiance_time",
        title="Irradiancia vs tiempo",
        purpose="Comparar la evolución temporal de G_POA/GHI con ventanas de simulación PV.",
    ),
    WeatherChartSpec(
        key="ambient_vs_cell_temperature",
        title="Temperatura ambiente vs temperatura de celda",
        purpose="Visualizar el acoplamiento térmico entre clima local y desempeño del módulo.",
    ),
    WeatherChartSpec(
        key="cloudiness_vs_estimated_production",
        title="Nubosidad vs producción estimada",
        purpose="Relacionar cobertura nubosa con potencia esperada bajo escenarios operativos.",
    ),
    WeatherChartSpec(
        key="ideam_vs_external_apis",
        title="Comparación IDEAM vs otras APIs",
        purpose=(
            "Contrastar fuentes meteorológicas para validar consistencia "
            "de entradas al gemelo."
        ),
    ),
)

__all__ = ["WEATHER_CHART_SPECS", "WeatherChartSpec"]
