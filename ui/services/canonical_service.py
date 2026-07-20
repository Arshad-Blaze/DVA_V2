"""Canonical service — manages column mapping state, business schema, quantity/UOM.

Consumes ColumnMapping, CanonicalMetadata from backend contracts.
UI never maps columns or resolves quantity — only visualizes and collects choices.
"""

from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
from dataclasses import asdict

from dav_platform.core.contracts import (
    CANONICAL_COLUMNS,
    ColumnMapping,
    CanonicalMetadata,
)


# Essentials shown by default; Advanced under collapsible section
ESSENTIAL_FIELDS = ["store", "upc", "description", "quantity", "sales", "date"]
ADVANCED_FIELDS = [
    "category", "brand", "department", "price", "promotion",
    "currency", "uom", "weight", "time", "store_name",
    "record_type", "region", "division",
]

class CanonicalService:
    """Manages canonical mapping state within the UI session.

    Never performs actual mapping — only stores user choices and
    visualizes suggestions from the Canonical Layer.
    """

    def __init__(self, context=None):
        self._context = context
        self._mappings: Dict[str, ColumnMapping] = {}
        self._physical_columns: List[Dict[str, Any]] = []
        self._suggestions: List[Dict[str, Any]] = []
        self._quantity_strategy: str = "units"
        self._uom_value: str = "each"
        self._accepted: bool = False
        self._on_change: Optional[Callable] = None
        self._ignored_physical: List[str] = []

    def get_metadata(self) -> CanonicalMetadata:
        mapped = [m for m in self._mappings.values() if m.physical_column]
        physical_names = {c["name"] for c in self._physical_columns}
        mapped_phys = {m.physical_column for m in mapped}
        unmapped = physical_names - mapped_phys
        ignored = set(self._ignored_physical)
        all_mapped_or_ignored = mapped_phys | ignored
        unmapped_count = len(physical_names - all_mapped_or_ignored)

        return CanonicalMetadata(
            mapped_columns=len(mapped),
            unmapped_columns=unmapped_count,
            quantity_column=self._resolve_quantity_column_name(),
            quantity_type=self._quantity_strategy,
            confidence=self._overall_confidence(),
            uom_strategy="detected",
            ignored_columns=list(self._ignored_physical),
            transformation_log=[
                f"Mapped {len(mapped)} of {len(self._physical_columns)} columns",
                f"Quantity: {self._quantity_strategy}",
                f"UOM: {self._uom_value}",
            ],
        )

    def get_mapping(self, business_field: str) -> Optional[ColumnMapping]:
        return self._mappings.get(business_field)

    def set_mapping(self, business_field: str, physical_column: str) -> None:
        if physical_column:
            self._mappings[business_field] = ColumnMapping(
                physical_column=physical_column,
                canonical_name=business_field,
                confidence=self._compute_mapping_confidence(physical_column, business_field),
                source="user",
            )
        else:
            self._mappings.pop(business_field, None)
        self._notify()

    def clear_mapping(self, business_field: str) -> None:
        self._mappings.pop(business_field, None)
        self._notify()

    def clear_all_mappings(self) -> None:
        self._mappings.clear()
        self._notify()

    def ignore_physical(self, column_name: str) -> None:
        if column_name not in self._ignored_physical:
            self._ignored_physical.append(column_name)
            self._notify()

    def unignore_physical(self, column_name: str) -> None:
        if column_name in self._ignored_physical:
            self._ignored_physical.remove(column_name)
            self._notify()

    def set_quantity_strategy(self, strategy: str) -> None:
        self._quantity_strategy = strategy
        self._notify()

    def set_uom(self, value: str) -> None:
        self._uom_value = value
        self._notify()

    def accept(self) -> None:
        self._accepted = True
        self._notify()

    @property
    def accepted(self) -> bool:
        return self._accepted

    @property
    def mappings(self) -> Dict[str, ColumnMapping]:
        return dict(self._mappings)

    @property
    def physical_columns(self) -> List[Dict[str, Any]]:
        return list(self._physical_columns)

    @property
    def suggestions(self) -> List[Dict[str, Any]]:
        return list(self._suggestions)

    @property
    def quantity_strategy(self) -> str:
        return self._quantity_strategy

    @property
    def uom_value(self) -> str:
        return self._uom_value

    @property
    def ignored_physical(self) -> List[str]:
        return list(self._ignored_physical)

    @property
    def has_changes(self) -> bool:
        return any(m.source == "user" for m in self._mappings.values())

    def get_mapped_physical(self) -> List[str]:
        return [m.physical_column for m in self._mappings.values() if m.physical_column]

    def get_unmapped_physical(self) -> List[str]:
        mapped = set(self.get_mapped_physical())
        ignored = set(self._ignored_physical)
        all_phys = {c["name"] for c in self._physical_columns}
        return list(all_phys - mapped - ignored)

    def get_required_missing(self) -> List[str]:
        essentials = set(ESSENTIAL_FIELDS)
        mapped = set(self._mappings.keys())
        return [f for f in essentials - mapped if self._is_missing_essential(f)]

    def auto_map(self) -> None:
        self._notify()

    def _compute_mapping_confidence(self, physical: str, business: str) -> float:
        return 0.5

    def _is_missing_essential(self, field: str) -> bool:
        return field not in self._mappings or not self._mappings[field].physical_column

    def get_summary(self) -> Dict[str, Any]:
        mapped = [m for m in self._mappings.values() if m.physical_column]
        total = len(self._physical_columns)
        ignored = len(self._ignored_physical)
        mapped_pct = len(mapped) / max(total, 1) * 100
        return {
            "mapped": len(mapped),
            "total": total,
            "ignored": ignored,
            "mapped_pct": round(mapped_pct, 1),
            "unmapped": len(self.get_unmapped_physical()),
            "required_missing": len(self.get_required_missing()),
            "confidence": self._overall_confidence(),
            "quantity": self._quantity_strategy,
            "uom": self._uom_value,
        }

    def _overall_confidence(self) -> float:
        mapped = [m for m in self._mappings.values() if m.physical_column]
        if not mapped:
            return 0.0
        return round(sum(m.confidence for m in mapped) / len(mapped), 2)

    def _resolve_quantity_column_name(self) -> Optional[str]:
        mapping = self._mappings.get("quantity")
        return mapping.physical_column if mapping else None

    def on_change(self, callback: Callable) -> None:
        self._on_change = callback

    def _notify(self) -> None:
        if self._on_change:
            self._on_change()

    @staticmethod
    def get_business_schema_fields() -> Dict[str, str]:
        return dict(CANONICAL_COLUMNS)

    @staticmethod
    def get_field_category(field: str) -> str:
        return "essential" if field in ESSENTIAL_FIELDS else "advanced"
