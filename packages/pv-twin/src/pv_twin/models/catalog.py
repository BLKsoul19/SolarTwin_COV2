import json
from pathlib import Path
from typing import Any, cast

from pv_twin.models.panel import PanelParameters


class PanelNotFoundError(LookupError):
    """Raised when a panel id does not exist in the local catalog."""


class PanelCatalogRepository:
    """Repository that loads panel parameters from JSON files."""

    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = data_dir or self._default_data_dir()

    def list_all(self) -> list[PanelParameters]:
        """Return every valid panel in the catalog sorted by id."""
        panels = [self._load_panel(path) for path in self.data_dir.glob("*.json")]
        return sorted(panels, key=lambda panel: panel.panel_id)

    def get_by_id(self, panel_id: str) -> PanelParameters:
        """Return one panel by canonical id."""
        path = self.data_dir / f"{panel_id}.json"
        if not path.exists():
            raise PanelNotFoundError(f"Panel not found: {panel_id}")
        return self._load_panel(path)

    def _load_panel(self, path: Path) -> PanelParameters:
        data = self._read_json(path)
        return PanelParameters.model_validate(data)

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        with path.open(encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, dict):
            raise ValueError(f"Panel catalog file must contain an object: {path}")
        return cast(dict[str, Any], data)

    @staticmethod
    def _default_data_dir() -> Path:
        return Path(__file__).resolve().parents[5] / "data" / "panels"
