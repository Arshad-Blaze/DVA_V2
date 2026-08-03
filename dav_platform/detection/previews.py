"""Preview generation for detection results.

Generates Raw and Flatten previews.
Canonical preview is canonical layer responsibility.
UI should only render these — never generate them.
"""

from typing import List, Optional

import polars as pl

from dav_platform.core.contracts import (
    FileType,
    LayoutField,
    RecordTypeInfo,
)


def generate_raw_preview(
    lines: List[str],
    max_rows: int = 20,
) -> Optional[pl.DataFrame]:
    """Generate raw preview DataFrame from lines."""
    if not lines:
        return None

    preview_lines = lines[:max_rows]
    return pl.DataFrame({
        "line_number": list(range(1, len(preview_lines) + 1)),
        "content": preview_lines,
    })


def generate_flatten_preview(
    lines: List[str],
    delimiter: Optional[str],
    file_type: FileType,
    record_types: List[RecordTypeInfo],
    layout_fields: List[LayoutField],
    header_prefix: Optional[str] = None,
    trailer_prefix: Optional[str] = None,
    max_rows: int = 20,
) -> Optional[pl.DataFrame]:
    """Generate flatten preview — data with record type annotations."""
    if not lines:
        return None

    rows = []
    for i, line in enumerate(lines[:max_rows]):
        row = {"line_number": i + 1, "content": line, "record_type": "data"}

        # Classify record type
        if record_types:
            for rt in record_types:
                if line.startswith(rt.prefix):
                    row["record_type"] = rt.prefix
                    break

        # For delimited, split by delimiter
        if delimiter and file_type in (FileType.DELIMITED, FileType.MULTILINE_DELIMITED):
            parts = line.split(delimiter)
            for j, part in enumerate(parts[:20]):  # Limit columns
                row[f"field_{j}"] = part.strip()
            row["field_count"] = len(parts)

        rows.append(row)

    if not rows:
        return None

    return pl.DataFrame(rows)



