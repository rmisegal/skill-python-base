"""
Bibliography detection rules definitions.

Rules for detecting citation and bibliography issues in LaTeX.
"""

from ...domain.models.issue import Severity

BIB_RULES = {
    # Rule 0: Malformed citation key with LaTeX commands
    "bib-malformed-cite-key": {
        "description": "Citation key contains LaTeX commands which is invalid",
        "pattern": r"\\cite(?:\[[^\]]*\])?\{([^}]*\\(?:hebyear|en|num|percent|textenglish)\{[^}]*)",
        "severity": Severity.WARNING,
        "fix_template": "Remove LaTeX commands from citation key",
    },
    # Rule 1: Missing bibliography file
    "bib-missing-file": {
        "description": "Bibliography command references missing .bib file",
        "pattern": r"\\(?:addbibresource|bibliography)\{([^}]+)\}",
        "severity": Severity.CRITICAL,
        "fix_template": "Ensure {}.bib file exists in project",
    },
    # Rule 2: Undefined citation
    "bib-undefined-cite": {
        "description": "Citation key may not be defined in bibliography",
        "pattern": r"\\cite\{([^}]+)\}",
        "severity": Severity.WARNING,
        "log_pattern": r"Citation.*undefined",
        "fix_template": "Add entry for '{}' to .bib file",
    },
    # Rule 3: Empty citation
    "bib-empty-cite": {
        "description": "Empty citation command found",
        "pattern": r"\\cite\{\s*\}",
        "severity": Severity.CRITICAL,
        "fix_template": "Add citation key or remove empty \\cite{{}}",
    },
    # Rule 4: Standalone missing biblatex
    "bib-standalone-missing": {
        "description": "Subfile missing biblatex configuration",
        "pattern": r"\\documentclass\[[^\]]*\]\{subfiles\}",
        "severity": Severity.WARNING,
        "negative_pattern": r"\\usepackage.*biblatex|\\addbibresource",
        "has_cite_pattern": r"\\cite\{",
        "fix_template": "Add biblatex setup for standalone compilation",
    },
    # Rule 5: Bibliography style mismatch
    "bib-style-mismatch": {
        "description": "Using bibtex style with biblatex package",
        "pattern": r"\\bibliographystyle\{([^}]+)\}",
        "severity": Severity.WARNING,
        "context_pattern": r"\\usepackage.*biblatex",
        "document_context": True,
        "fix_template": "Remove \\bibliographystyle - not needed with biblatex",
    },
}
