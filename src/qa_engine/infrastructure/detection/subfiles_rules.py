"""
Subfiles detection rules definitions.

Rules for detecting subfiles-related issues in LaTeX documents.
"""

from ...domain.models.issue import Severity

SUBFILES_RULES = {
    # Rule 1: Chapter file without subfiles documentclass
    "subfiles-missing-class": {
        "description": "Chapter file not using subfiles documentclass",
        "pattern": r"\\documentclass\{(?!subfiles)[^}]+\}",
        "severity": Severity.WARNING,
        "file_pattern": r"chapter|chap|ch\d",
        "fix_template": "Use \\documentclass[../main.tex]{{subfiles}}",
    },
    # Rule 2: Subfiles without main reference
    "subfiles-no-main-ref": {
        "description": "Subfiles documentclass without main.tex reference",
        "pattern": r"\\documentclass\{subfiles\}",
        "severity": Severity.CRITICAL,
        "fix_template": "Add path to main: \\documentclass[../main.tex]{{subfiles}}",
    },
    # Rule 3: Chapter without standalone preamble setup
    "subfiles-no-preamble": {
        "description": "Chapter subfile missing standalone compilation support",
        "pattern": r"\\documentclass\[[^\]]*\]\{subfiles\}",
        "severity": Severity.INFO,
        "negative_pattern": r"\\ifSubfilesClassLoaded|\\setcounter\{chapter\}",
        "fix_template": "Add \\setcounter{{chapter}}{{N}} for standalone",
    },
}
