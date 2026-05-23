from pathlib import Path

import pytest
from pv_twin.models import PanelCatalogRepository, PanelNotFoundError, PanelParameters


def test_panel_catalog_loads_all_panels() -> None:
    catalog = PanelCatalogRepository()

    panels = catalog.list_all()

    assert len(panels) >= 2
    assert all(isinstance(panel, PanelParameters) for panel in panels)
    assert [panel.panel_id for panel in panels] == sorted(panel.panel_id for panel in panels)


def test_panel_catalog_get_by_id() -> None:
    catalog = PanelCatalogRepository()

    panel = catalog.get_by_id("generic_poly_330")

    assert panel.panel_id == "generic_poly_330"
    assert panel.pmax_stc_w == 330.0


def test_panel_catalog_missing_id_raises() -> None:
    catalog = PanelCatalogRepository()

    with pytest.raises(PanelNotFoundError):
        catalog.get_by_id("missing_panel")


def test_panel_catalog_rejects_non_object_json(tmp_path: Path) -> None:
    data_dir = tmp_path / "panels"
    data_dir.mkdir()
    (data_dir / "invalid.json").write_text("[]", encoding="utf-8")
    catalog = PanelCatalogRepository(data_dir=data_dir)

    with pytest.raises(ValueError, match="must contain an object"):
        catalog.list_all()
