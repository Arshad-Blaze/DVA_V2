"""Modular computation pipeline."""
from typing import List, Optional, Callable
from dataclasses import dataclass
import time
import polars as pl
from dav_platform.core.contracts import CanonicalDataset, ProcessingConfig, ProcessingResult


@dataclass
class PipelineStage:
    """A single stage in the processing pipeline."""
    name: str
    processor: Callable[[pl.DataFrame, ProcessingConfig], pl.DataFrame]
    enabled: bool = True


class ProcessingPipeline:
    """Modular pipeline that chains computation stages."""

    def __init__(self, stages: Optional[List[PipelineStage]] = None):
        self._stages: List[PipelineStage] = stages or []

    def add_stage(self, stage: PipelineStage) -> "ProcessingPipeline":
        """Add a stage (builder pattern)."""
        self._stages.append(stage)
        return self

    def execute(self, dataset: CanonicalDataset, config: ProcessingConfig) -> ProcessingResult:
        """Execute all enabled stages in order.

        - Start with dataset.dataframe
        - Apply each enabled stage
        - Return ProcessingResult with final DataFrame
        - Time overall execution
        """
        start = time.time()
        errors: List[str] = []

        if dataset.dataframe is None or dataset.dataframe.is_empty():
            return ProcessingResult.error("pipeline", "Dataset has no dataframe")

        df = dataset.dataframe.clone()

        for stage in self._stages:
            if not stage.enabled:
                continue
            try:
                df = stage.processor(df, config)
            except Exception as e:
                errors.append(f"Stage '{stage.name}' failed: {e}")

        elapsed = time.time() - start

        return ProcessingResult.from_df(
            df,
            operation="pipeline",
            elapsed_seconds=elapsed,
            metadata={
                "stages_executed": sum(1 for s in self._stages if s.enabled),
                "stages_total": len(self._stages),
                "stage_names": [s.name for s in self._stages if s.enabled],
            },
            errors=errors,
        )

    def list_stages(self) -> List[str]:
        """Return names of all registered stages."""
        return [s.name for s in self._stages]
