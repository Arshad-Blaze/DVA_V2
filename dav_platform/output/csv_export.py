"""Output Layer — CSV Export."""

import csv
import os
from typing import Any, Dict, List, Optional


class CSVExporter:
    """Generates CSV files from report data."""

    def export(
        self,
        reports: List[Dict[str, Any]],
        file_path: str,
    ) -> str:
        """Export reports to a CSV file.

        If multiple reports are given, they are concatenated with
        a blank-line separator and a report title header.

        Args:
            reports: List of dicts with 'title', 'headers', 'rows'.
            file_path: Output file path.

        Returns:
            Absolute path to the generated file.
        """
        os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)

        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f)
            for i, report in enumerate(reports):
                if i > 0:
                    writer.writerow([])
                title = report.get("title", "")
                headers = report.get("headers", [])
                rows = report.get("rows", [])

                writer.writerow([title])
                if headers:
                    writer.writerow(headers)
                for row in rows:
                    writer.writerow(row)

        return os.path.abspath(file_path)

    def export_validation_results(
        self,
        issues: List[Any],
        file_path: str,
    ) -> str:
        """Export validation issues to a CSV file."""
        os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)

        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Rule", "Message", "Severity", "Column", "Row Count"])
            for issue in issues:
                writer.writerow([
                    issue.rule,
                    issue.message,
                    issue.severity.value if hasattr(issue.severity, "value") else str(issue.severity),
                    issue.column or "",
                    issue.row_count,
                ])

        return os.path.abspath(file_path)
