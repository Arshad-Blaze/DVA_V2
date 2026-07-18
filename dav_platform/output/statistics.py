"""Output Layer — Output Statistics Engine."""

from typing import List

from dav_platform.core.contracts import OutputStatistics


class OutputStatisticsEngine:
    """Computes statistics about the output generation."""

    def compute(
        self,
        total_files: int,
        total_sheets: int,
        total_rows: int,
        total_size_bytes: int,
        generation_time: float,
        warnings: List[str],
    ) -> OutputStatistics:
        return OutputStatistics(
            total_files_generated=total_files,
            total_sheets_created=total_sheets,
            total_rows_exported=total_rows,
            total_size_bytes=total_size_bytes,
            generation_time_seconds=generation_time,
            success_rate=100.0 if len(warnings) == 0 else 50.0,
            warnings=warnings,
        )
