"""
TOC (Table of Contents) configuration detection rules.

Detects issues in CLS files related to counter definitions and numberline
that cause BiDi rendering problems in TOC.

These rules provide DETECTION only - fixing remains LLM-only due to
the semantic understanding required for CLS macro modifications.
"""

from ...domain.models.issue import Severity

# Counter-related rules (file-wide pattern matching)
TOC_COUNTER_RULES = {
    "toc-missing-thechapter": {
        "description": "Missing \\thechapter with \\textenglish{} wrapper",
        "pattern": r"\\renewcommand\{\\thesection\}",
        "negative_pattern": r"\\renewcommand\{\\thechapter\}\{\\textenglish",
        "severity": Severity.WARNING,
        "file_pattern": r"\.cls$",
        "fix_template": "Add \\renewcommand{\\thechapter}{\\textenglish{\\arabic{chapter}}}",
    },
    "toc-numberline-double-wrap": {
        "description": "\\numberline adds \\textenglish{} causing double-wrap",
        "pattern": r"\\renewcommand\{\\numberline\}\[1\]\{[^}]*\\textenglish\{#1\}",
        "severity": Severity.WARNING,
        "file_pattern": r"\.cls$",
        "fix_template": "Remove \\textenglish{} from \\numberline",
    },
    "toc-thechapter-no-wrapper": {
        "description": "\\thechapter without \\textenglish{} wrapper",
        "pattern": r"\\renewcommand\{\\thechapter\}\{\\arabic\{chapter\}\}",
        "severity": Severity.WARNING,
        "file_pattern": r"\.cls$",
        "fix_template": "Wrap: \\renewcommand{\\thechapter}{\\textenglish{\\arabic{chapter}}}",
    },
    "toc-thesection-no-wrapper": {
        "description": "\\thesection without \\textenglish{} wrapper",
        "pattern": r"\\renewcommand\{\\thesection\}\{\\arabic\{section\}\}",
        "severity": Severity.WARNING,
        "file_pattern": r"\.cls$",
        "fix_template": "Wrap: \\renewcommand{\\thesection}{\\textenglish{\\arabic{section}}}",
    },
    "toc-thesubsection-no-wrapper": {
        "description": "\\thesubsection without \\textenglish{} wrapper",
        "pattern": r"\\renewcommand\{\\thesubsection\}\{\\arabic\{section\}\.\\arabic\{subsection\}\}",
        "severity": Severity.WARNING,
        "file_pattern": r"\.cls$",
        "fix_template": "Wrap: \\thesubsection with \\textenglish{}",
    },
}

# l@ command rules (block-aware detection)
# These need special handling to check RTL within each block
L_AT_BLOCK_RULES = {
    "toc-lchapter-no-rtl": {
        "description": "\\l@chapter missing RTL direction (\\pardir TRT)",
        "command": "l@chapter",
        "start_pattern": r"\\renewcommand\*?\\l@chapter\[2\]",
        "rtl_check": r"\\pardir\s*TRT|\\beginR",
        "severity": Severity.CRITICAL,
        "file_pattern": r"\.cls$",
        "fix_template": "Add \\pardir TRT\\textdir TRT after \\begingroup",
    },
    "toc-lsection-no-rtl": {
        "description": "\\l@section missing RTL direction (\\pardir TRT)",
        "command": "l@section",
        "start_pattern": r"\\renewcommand\*?\\l@section\[2\]",
        "rtl_check": r"\\pardir\s*TRT|\\beginR",
        "severity": Severity.CRITICAL,
        "file_pattern": r"\.cls$",
        "fix_template": "Add \\pardir TRT\\textdir TRT after \\begingroup",
    },
    "toc-lsubsection-no-rtl": {
        "description": "\\l@subsection missing RTL direction (\\pardir TRT)",
        "command": "l@subsection",
        "start_pattern": r"\\renewcommand\*?\\l@subsection\[2\]",
        "rtl_check": r"\\pardir\s*TRT|\\beginR",
        "severity": Severity.CRITICAL,
        "file_pattern": r"\.cls$",
        "fix_template": "Add \\pardir TRT\\textdir TRT after \\begingroup",
    },
}

# Combined rules for backward compatibility
TOC_RULES = {**TOC_COUNTER_RULES}
