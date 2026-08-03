"""Output Layer — Excel Export.

Generates production-quality Excel workbooks with multiple sheets.
"""

import os
from typing import Any, Dict, List, Optional

from dav_platform.output.exceptions import ExportError

try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False


HEADER_FILL = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
HEADER_FONT = Font(bold=True, color="FFFFFF", size=11)
TITLE_FONT = Font(bold=True, size=14)
BORDER_THIN = Border(
    left=Side(style="thin"),
    right=Side(style="thin"),
    top=Side(style="thin"),
    bottom=Side(style="thin"),
)


class ExcelExporter:
    """Generates multi-sheet Excel workbooks."""

    def export(
        self,
        reports: List[Dict[str, Any]],
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Export reports to an Excel workbook.

        Args:
            reports: List of dicts with 'title', 'headers', 'rows'.
            file_path: Output file path.
            metadata: Optional metadata dict for a summary row.

        Returns:
            Absolute path to the generated file.
        """
        if not HAS_OPENPYXL:
            raise ExportError("openpyxl is not installed")

        os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)

        wb = Workbook()
        wb.remove(wb.active)

        if not reports:
            ws = wb.create_sheet(title="Empty Report")
            ws.cell(row=1, column=1, value="No reports generated").font = Font(italic=True)
            wb.save(file_path)
            return os.path.abspath(file_path)

        for report in reports:
            title = report.get("title", "Sheet")
            headers = report.get("headers", [])
            rows = report.get("rows", [])

            ws = wb.create_sheet(title=title[:31])

            if title:
                ws.cell(row=1, column=1, value=title).font = TITLE_FONT
                ws.merge_cells(
                    start_row=1, start_column=1,
                    end_row=1, end_column=max(len(headers), 1)
                )
                start_row = 2
            else:
                start_row = 1

            if headers:
                for col_idx, header in enumerate(headers, start=1):
                    cell = ws.cell(row=start_row, column=col_idx, value=header)
                    cell.font = HEADER_FONT
                    cell.fill = HEADER_FILL
                    cell.alignment = Alignment(horizontal="center")
                    cell.border = BORDER_THIN
                start_row += 1

            for row_idx, row_data in enumerate(rows, start=start_row):
                for col_idx, value in enumerate(row_data, start=1):
                    cell = ws.cell(row=row_idx, column=col_idx, value=value)
                    cell.border = BORDER_THIN

            if headers:
                for col_idx in range(1, len(headers) + 1):
                    col_letter = get_column_letter(col_idx)
                    if rows:
                        max_length = max(
                            len(str(headers[col_idx - 1])),
                            *(
                                len(str(row[col_idx - 1])) if col_idx - 1 < len(row) else 0
                                for row in rows
                            ),
                        )
                    else:
                        max_length = len(str(headers[col_idx - 1]))
                    ws.column_dimensions[col_letter].width = min(max_length + 3, 50)

            if headers and rows:
                ws.auto_filter.ref = (
                    f"A{start_row}:{get_column_letter(len(headers))}"
                    f"{start_row + len(rows)}"
                )

            ws.freeze_panes = ws.cell(row=start_row, column=1)

        wb.save(file_path)
        return os.path.abspath(file_path)
