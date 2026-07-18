"""UI Tests — Canonical Mapping Service & Controller (Sprint 4A)."""

import pytest
from ui.services.canonical_service import CanonicalService
from ui.controllers.canonical_controller import CanonicalController
from ui.services.notification_service import NotificationService
from dav_platform.core.contracts import CANONICAL_COLUMNS


class TestCanonicalService:
    def test_default_state(self):
        svc = CanonicalService()
        assert len(svc.mappings) == 9  # 9 suggested mappings
        assert len(svc.physical_columns) == 9
        assert len(svc.suggestions) == 9
        assert svc.quantity_strategy == "units"
        assert svc.uom_value == "each"
        assert svc.accepted is False

    def test_get_mapping(self):
        svc = CanonicalService()
        m = svc.get_mapping("store")
        assert m is not None
        assert m.physical_column == "Store"
        assert m.canonical_name == "store"
        assert m.confidence == 0.99

    def test_set_mapping(self):
        svc = CanonicalService()
        svc.set_mapping("brand", "Sales")
        m = svc.get_mapping("brand")
        assert m is not None
        assert m.physical_column == "Sales"
        assert m.source == "user"

    def test_clear_mapping(self):
        svc = CanonicalService()
        svc.clear_mapping("store")
        assert svc.get_mapping("store") is None

    def test_clear_all_mappings(self):
        svc = CanonicalService()
        svc.clear_all_mappings()
        assert len(svc.mappings) == 0

    def test_auto_map(self):
        svc = CanonicalService()
        svc.clear_all_mappings()
        svc.auto_map()
        assert len(svc.mappings) == 9
        assert svc.get_mapping("store").physical_column == "Store"

    def test_ignore_physical(self):
        svc = CanonicalService()
        svc.ignore_physical("Promotion")
        assert "Promotion" in svc.ignored_physical
        svc.ignore_physical("Promotion")  # duplicate
        assert len(svc.ignored_physical) == 1

    def test_unignore_physical(self):
        svc = CanonicalService()
        svc.ignore_physical("Promotion")
        svc.unignore_physical("Promotion")
        assert "Promotion" not in svc.ignored_physical

    def test_set_quantity_strategy(self):
        svc = CanonicalService()
        svc.set_quantity_strategy("weighted_qty")
        assert svc.quantity_strategy == "weighted_qty"

    def test_set_uom(self):
        svc = CanonicalService()
        svc.set_uom("case")
        assert svc.uom_value == "case"

    def test_accept(self):
        svc = CanonicalService()
        svc.accept()
        assert svc.accepted is True

    def test_get_summary(self):
        svc = CanonicalService()
        s = svc.get_summary()
        assert s["mapped"] == 9
        assert s["total"] == 9
        assert s["confidence"] == 0.96
        assert "quantity" in s
        assert "uom" in s

    def test_get_metadata(self):
        svc = CanonicalService()
        meta = svc.get_metadata()
        assert meta.mapped_columns == 9
        assert meta.quantity_type == "units"
        assert meta.uom_strategy == "detected"

    def test_get_mapped_physical(self):
        svc = CanonicalService()
        mapped = svc.get_mapped_physical()
        assert "Store" in mapped
        assert len(mapped) == 9

    def test_get_unmapped_physical(self):
        svc = CanonicalService()
        svc.clear_all_mappings()
        unmapped = svc.get_unmapped_physical()
        assert len(unmapped) == 9

    def test_get_required_missing(self):
        svc = CanonicalService()
        svc.clear_mapping("store")
        missing = svc.get_required_missing()
        assert "store" in missing

    def test_has_changes(self):
        svc = CanonicalService()
        assert svc.has_changes is False  # all auto-mapped
        svc.set_mapping("brand", "Sales")
        assert svc.has_changes is True

    def test_business_schema_fields(self):
        fields = CanonicalService.get_business_schema_fields()
        assert "store" in fields
        assert "upc" in fields
        assert "description" in fields

    def test_field_category(self):
        assert CanonicalService.get_field_category("store") == "essential"
        assert CanonicalService.get_field_category("brand") == "advanced"

    def test_on_change_callback(self):
        svc = CanonicalService()
        calls = []
        svc.on_change(lambda: calls.append(1))
        svc.set_mapping("store", "UPC")
        assert len(calls) >= 1


class TestCanonicalController:
    def test_auto_map_notifies(self):
        notify = NotificationService()
        svc = CanonicalService()
        ctrl = CanonicalController(svc, notify)
        svc.clear_all_mappings()
        ctrl.auto_map()
        assert len(svc.mappings) == 9
        assert len(notify.notifications) == 1

    def test_set_mapping(self):
        notify = NotificationService()
        svc = CanonicalService()
        ctrl = CanonicalController(svc, notify)
        ctrl.set_mapping("brand", "Sales")
        assert svc.get_mapping("brand").physical_column == "Sales"

    def test_clear_mapping(self):
        notify = NotificationService()
        svc = CanonicalService()
        ctrl = CanonicalController(svc, notify)
        ctrl.clear_mapping("store")
        assert svc.get_mapping("store") is None

    def test_clear_all(self):
        notify = NotificationService()
        svc = CanonicalService()
        ctrl = CanonicalController(svc, notify)
        ctrl.clear_all()
        assert len(svc.mappings) == 0

    def test_ignore_column(self):
        notify = NotificationService()
        svc = CanonicalService()
        ctrl = CanonicalController(svc, notify)
        ctrl.ignore_column("Promotion")
        assert "Promotion" in svc.ignored_physical

    def test_unignore_column(self):
        notify = NotificationService()
        svc = CanonicalService()
        ctrl = CanonicalController(svc, notify)
        ctrl.ignore_column("Promotion")
        ctrl.unignore_column("Promotion")
        assert "Promotion" not in svc.ignored_physical

    def test_set_quantity(self):
        notify = NotificationService()
        svc = CanonicalService()
        ctrl = CanonicalController(svc, notify)
        ctrl.set_quantity("weighted_qty")
        assert svc.quantity_strategy == "weighted_qty"

    def test_set_uom(self):
        notify = NotificationService()
        svc = CanonicalService()
        ctrl = CanonicalController(svc, notify)
        ctrl.set_uom("pound")
        assert svc.uom_value == "pound"

    def test_accept_blocks_with_missing(self):
        """Accept blocked when required fields missing."""
        notify = NotificationService()
        svc = CanonicalService()
        ctrl = CanonicalController(svc, notify)
        svc.clear_mapping("store")
        svc.clear_mapping("upc")
        ctrl.accept()
        assert svc.accepted is False
        assert len(notify.notifications) == 1
        assert notify.notifications[0]["type_value"] == "warning"

    def test_accept_succeeds(self):
        notify = NotificationService()
        svc = CanonicalService()
        ctrl = CanonicalController(svc, notify)
        ctrl.accept()
        assert svc.accepted is True

    def test_get_business_schema(self):
        notify = NotificationService()
        svc = CanonicalService()
        ctrl = CanonicalController(svc, notify)
        schema = ctrl.get_business_schema()
        assert "store" in schema

    def test_summary_property(self):
        notify = NotificationService()
        svc = CanonicalService()
        ctrl = CanonicalController(svc, notify)
        s = ctrl.summary
        assert s["mapped"] == 9

    def test_get_unmapped_physical(self):
        notify = NotificationService()
        svc = CanonicalService()
        ctrl = CanonicalController(svc, notify)
        svc.clear_all_mappings()
        unmapped = ctrl.get_unmapped_physical()
        assert len(unmapped) == 9
