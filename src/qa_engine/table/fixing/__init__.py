"""Table fixing submodule."""
from .table_parser import TableParser, ParsedTable, TableRow, TableCell
from .column_transformer import ColumnTransformer
from .fancy_table_fixer import FancyTableFixer, FancyFixResult, FixResult
from .column_fixer import TableColumnFixer, ColumnFixResult, ColumnFixChange
from .overflow_fixer import TableOverflowFixer, OverflowFixResult, OverflowFix
from .header_color_fixer import HeaderColorFixer, HeaderColorResult, HeaderColorFix

__all__ = [
    "TableParser", "ParsedTable", "TableRow", "TableCell",
    "ColumnTransformer",
    "FancyTableFixer", "FancyFixResult", "FixResult",
    "TableColumnFixer", "ColumnFixResult", "ColumnFixChange",
    "TableOverflowFixer", "OverflowFixResult", "OverflowFix",
    "HeaderColorFixer", "HeaderColorResult", "HeaderColorFix",
]
