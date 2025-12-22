"""Table detection submodule."""
from .table_models import (
    TableIssue, TableDetectResult, TableAnalysis, FancyDetectResult,
    TableOverflowIssue, OverflowDetectResult,
)
from .table_layout_detector import TableLayoutDetector
from .fancy_table_detector import FancyTableDetector
from .table_overflow_detector import TableOverflowDetector

__all__ = [
    "TableLayoutDetector", "TableDetectResult", "TableIssue",
    "FancyTableDetector", "FancyDetectResult", "TableAnalysis",
    "TableOverflowDetector", "OverflowDetectResult", "TableOverflowIssue",
]
