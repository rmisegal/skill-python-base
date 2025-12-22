"""
Table detection rules definitions.

Rules for RTL table issues in Hebrew-English LaTeX documents.
"""

from ...domain.models.issue import Severity

TABLE_RULES = {
    # Rule 1: Table without RTL-aware environment
    "table-no-rtl-env": {
        "description": "Table using tabular without rtltabular in Hebrew context",
        "pattern": r"\\begin\{tabular\}",
        "severity": Severity.WARNING,
        "context_pattern": r"[א-ת]",
        "document_context": True,
        "exclude_pattern": r"\\begin\{rtltabular\}",
        "fix_template": "Use \\begin{{rtltabular}} for RTL tables",
    },
    # Rule 2: Caption before table (should be after in RTL)
    "table-caption-position": {
        "description": "Table caption before table content (RTL convention: after)",
        "pattern": r"\\caption\{[^}]*\}[^\\]*\\begin\{tabular",
        "severity": Severity.INFO,
        "fix_template": "Move \\caption after table content for RTL",
    },
    # Rule 3: Table cell with Hebrew without wrapper
    "table-cell-hebrew": {
        "description": "Hebrew text in table cell without proper direction",
        "pattern": r"&\s*([א-ת][^&\\]*)\s*(?:&|\\\\)",
        "severity": Severity.WARNING,
        "fix_template": "Wrap Hebrew cell content with \\texthebrew{{}}",
    },
    # Rule 4: Plain table without styling (fancy-detect)
    "table-plain-unstyled": {
        "description": "Plain tabular without fancy styling in RTL document",
        "pattern": r"\\begin\{tabular\}\{[|lcrp]+\}",
        "severity": Severity.INFO,
        "context_pattern": r"[א-ת]",
        "document_context": True,
        "fix_template": "Consider using rtltabular with proper styling",
    },
    # Rule 4b: Missing header row color
    "table-missing-header-color": {
        "description": "Table header row missing rowcolor{blue!15} styling",
        "pattern": r"\\begin\{(?:tabular|rtltabular)\}",
        "severity": Severity.WARNING,
        "exclude_pattern": r"\\rowcolor\{blue!15\}",
        "fix_template": "Add \\rowcolor{blue!15} to first row after \\begin{tabular}",
    },
    # Rule 4c: Using table instead of hebrewtable in Hebrew doc
    "table-not-hebrewtable": {
        "description": "Uses table instead of hebrewtable environment in Hebrew document",
        "pattern": r"\\begin\{table\}",
        "severity": Severity.WARNING,
        "context_pattern": r"[א-ת]",
        "document_context": True,
        "exclude_pattern": r"\\begin\{hebrewtable\}",
        "fix_template": "Replace \\begin{table} with \\begin{hebrewtable}",
    },
    # Rule 5: Wide table without resizebox (overflow-detect)
    "table-overflow": {
        "description": "Wide table without resizebox may cause overfull hbox",
        "pattern": r"\\begin\{tabular\}\{[^}]{6,}\}",
        "severity": Severity.WARNING,
        "exclude_pattern": r"\\resizebox",
        "fix_template": "Wrap with \\resizebox{{\\textwidth}}{{!}}{{...}}",
    },
    # Rule 6: Caption setup with wrong justification (raggedleft = left in RTL)
    "caption-setup-raggedleft": {
        "description": "captionsetup with justification=raggedleft (wrong for RTL)",
        "pattern": r"\\captionsetup\{[^}]*justification=raggedleft[^}]*\}",
        "severity": Severity.WARNING,
        "fix_template": "Change to justification=centering",
    },
    # Rule 7: Caption wrapped in flushleft (wrong for RTL)
    "caption-flushleft-wrapped": {
        "description": "Caption wrapped in flushleft environment (wrong for RTL)",
        "pattern": r"\\begin\{flushleft\}[^}]*\\caption",
        "severity": Severity.WARNING,
        "fix_template": "Use \\centering instead of flushleft",
    },
    # Rule 8: Table-specific caption with wrong justification
    "caption-table-raggedleft": {
        "description": "Table captionsetup with justification=raggedleft",
        "pattern": r"\\captionsetup\[table\]\{[^}]*justification=raggedleft[^}]*\}",
        "severity": Severity.WARNING,
        "fix_template": "Change to justification=centering",
    },
}
