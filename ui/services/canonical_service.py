"""Canonical service — manages column mapping state, business schema, quantity/UOM.

Consumes ColumnMapping, CanonicalMetadata from backend contracts.
Delegates mapping generation to the real CanonicalEngine.
UI never maps columns or resolves quantity — only visualizes and collects choices.
"""

from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
from dataclasses import asdict

import polars as pl

from dav_platform.core.contracts import (
    CANONICAL_COLUMNS,
    ColumnMapping,
    CanonicalMetadata,
    CanonicalDataset,
    DiscoveryResult,
)
from dav_platform.canonical.engine import CanonicalEngine
from dav_platform.canonical.mapping import map_columns


# Essentials shown by default; Advanced under collapsible section
ESSENTIAL_FIELDS = ["store", "upc", "description", "quantity", "price", "date"]
ADVANCED_FIELDS = [
    "category", "brand", "department", "price", "promotion",
    "currency", "uom", "weight", "time", "store_name",
    "record_type", "region", "division",
]

DATAFRAME_TYPES = {
    "Int64": "integer", "Int32": "integer", "Float64": "float", "Float32": "float",
    "Utf8": "string", "String": "string", "Boolean": "boolean",
    "Date": "date", "Datetime": "datetime", "Categorical": "string",
}


class CanonicalService:
    """Manages canonical mapping state within the UI session.

    Consumes a DiscoveryResult from the Detection layer and generates
    mappings via the backend CanonicalEngine. User overrides are stored
    on top of the auto-detected mapping base.
    """

    def __init__(self, context=None):
        self._context = context
        self._engine = CanonicalEngine()
        self._result: Optional[DiscoveryResult] = None
        self._dataset: Optional[CanonicalDataset] = None
        self._dataframe: Optional[pl.DataFrame] = None
        self._mappings: Dict[str, ColumnMapping] = {}
        self._physical_columns: List[Dict[str, Any]] = []
        self._suggestions: List[Dict[str, Any]] = []
        self._quantity_strategy: str = "units"
        self._uom_value: str = "each"
        self._accepted: bool = False
        self._on_change: Optional[Callable] = None
        self._ignored_physical: List[str] = []

    # ── Data loading from Detection layer ────────────────────

    def load_discovery(self, result: DiscoveryResult, dataframe: Optional[pl.DataFrame] = None) -> None:
        """Consume a DiscoveryResult (and optional parsed data) from Detection.

        Auto-generates the mapping base from the backend CanonicalEngine.
        """
        self._result = result
        self._dataframe = dataframe
        self._build_physical_columns(result, dataframe)
        self.auto_map()

    def load_dataset(self, dataset: CanonicalDataset) -> None:
        """Consume a pre-built CanonicalDataset (used by tests/integration)."""
        self._dataset = dataset
        self._dataframe = dataset.dataframe
        self._result = None
        self._mappings = {}
        for m in dataset.column_mappings or []:
            self._mappings[m.canonical_name] = m
        self._rebuild_physical_columns(dataset.dataframe)
        if dataset.metadata:
            self._quantity_strategy = dataset.metadata.quantity_type or self._quantity_strategy
        self._notify()

    def _build_physical_columns(self, result: DiscoveryResult, dataframe: Optional[pl.DataFrame]) -> None:
        """Build physical column descriptors from discovery + data."""
        cols: List[Dict[str, Any]] = []
        sample_map: Dict[str, str] = {}
        type_map: Dict[str, str] = {}
        null_map: Dict[str, float] = {}

        if dataframe is not None and not dataframe.is_empty():
            for c in dataframe.columns:
                sample_map[c] = self._first_values(dataframe, c)
                type_map[c] = self._col_type(dataframe, c)
                null_map[c] = self._null_pct(dataframe, c)

        for name in (result.columns or []):
            cols.append({
                "name": name,
                "sample": sample_map.get(name, ""),
                "type": type_map.get(name, "string"),
                "null_pct": null_map.get(name, 0.0),
                "conf": result.confidence,
            })
        self._physical_columns = cols

    def _rebuild_physical_columns(self, dataframe: Optional[pl.DataFrame]) -> None:
        cols: List[Dict[str, Any]] = []
        if dataframe is not None and not dataframe.is_empty():
            for c in dataframe.columns:
                cols.append({
                    "name": c,
                    "sample": self._first_values(dataframe, c),
                    "type": self._col_type(dataframe, c),
                    "null_pct": self._null_pct(dataframe, c),
                    "conf": 1.0,
                })
        self._physical_columns = cols

    @staticmethod
    def _first_values(df: pl.DataFrame, col: str, n: int = 3) -> str:
        try:
            return ", ".join(str(v) for v in df[col].head(n).to_list() if v is not None)
        except Exception:
            return ""

    @staticmethod
    def _col_type(df: pl.DataFrame, col: str) -> str:
        try:
            dt = str(df[col].dtype)
            return DATAFRAME_TYPES.get(dt, "string")
        except Exception:
            return "string"

    @staticmethod
    def _null_pct(df: pl.DataFrame, col: str) -> float:
        try:
            total = df.height
            if not total:
                return 0.0
            nulls = df[col].null_count()
            return round(nulls / total * 100, 1)
        except Exception:
            return 0.0

    def get_metadata(self) -> CanonicalMetadata:
        mapped = [m for m in self._mappings.values() if m.physical_column]
        physical_names = {c["name"] for c in self._physical_columns}
        mapped_phys = {m.physical_column for m in mapped}
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
        """Generate mappings via the backend CanonicalEngine."""
        if self._result is not None:
            try:
                self._dataset = self._engine.transform(self._result, data=self._dataframe)
                self._mappings = {}
                for m in self._dataset.column_mappings or []:
                    self._mappings[m.canonical_name] = m
                if self._dataset.metadata:
                    self._quantity_strategy = self._dataset.metadata.quantity_type or self._quantity_strategy
                    if self._dataset.metadata.quantity_type == "weighted_qty":
                        self._uom_value = "kg"
                self._build_suggestions()
            except Exception:
                fallback = map_columns(self._result)
                self._mappings = {}
                for m in fallback:
                    self._mappings[m.canonical_name] = m
        self._notify()

    def _build_suggestions(self) -> None:
        self._suggestions = [
            {"business_field": m.canonical_name, "physical_column": m.physical_column,
             "confidence": m.confidence, "source": m.source}
            for m in self._mappings.values() if m.physical_column
        ]

    def _compute_mapping_confidence(self, physical: str, business: str) -> float:
        for m in self._mappings.values():
            if m.physical_column == physical:
                return m.confidence
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
