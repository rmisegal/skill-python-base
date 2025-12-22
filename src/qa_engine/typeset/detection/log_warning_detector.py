"""
Log warning detector for LaTeX log files.

Implements qa-typeset-detect skill.md v1.5 - parses .log files for typeset warnings.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .typeset_models import (
    TypesetDetectResult, HboxWarning, VboxWarning, UndefinedReference,
    UndefinedCitation, FloatTooLarge, KnownIssue, LatexError, PackageError,
)

# Known issues whitelist (from skill.md)
KNOWN_ISSUE_PATTERNS = [
    (r"\\begin\{pythonbox\}.*ended by.*\\end\{python\}", "pythonbox_internal",
     "tcolorbox/lstlisting/subfiles interaction"),
    (r"\\begin\{document\}.*ended by.*\\end\{tcb@drawing\}", "tcolorbox_internal",
     "Internal tcolorbox state"),
    (r"\\begin\{document\}.*ended by.*\\end\{tcolorbox\}", "tcolorbox_cleanup",
     "Nested environment cleanup"),
    (r"Missing number, treated as zero.*footnote", "footnote_counter",
     "tcolorbox footnote counter"),
    (r"Extra \\endgroup", "subfiles_cleanup", "subfiles hook cleanup"),
]


class LogWarningDetector:
    """
    Detects typeset warnings from LaTeX log files.

    Aligned with qa-typeset-detect skill.md v1.5:
    - Step 2: Parse log file for hbox/vbox/refs/citations/floats/errors
    - Step 4: Categorize warnings with severity thresholds
    """

    def detect_log(self, log_path: Path) -> TypesetDetectResult:
        """Detect warnings in a log file."""
        if not log_path.exists():
            return TypesetDetectResult()
        content = log_path.read_text(encoding="utf-8", errors="ignore")
        return self.detect_log_content(content, str(log_path))

    def detect_log_content(self, content: str, log_file: str) -> TypesetDetectResult:
        """Detect warnings in log content."""
        result = TypesetDetectResult(log_file=log_file)
        lines = content.split("\n")

        for line in lines:
            self._check_hbox(line, result)
            self._check_vbox(line, result)
            self._check_undefined_ref(line, result)
            self._check_undefined_citation(line, result)
            self._check_float_too_large(line, result)
            self._check_latex_error(line, result)
            self._check_package_error(line, result)

        # Count underfull vbox for v1.5 itemsep detection
        result.underfull_vbox_count = len(result.underfull_vbox)
        return result

    def _check_hbox(self, line: str, result: TypesetDetectResult) -> None:
        """Check for overfull/underfull hbox warnings."""
        # Overfull hbox
        m = re.search(r"Overfull \\hbox \(([0-9.]+)pt too wide\).*lines (\d+)--(\d+)", line)
        if m:
            amount = float(m.group(1))
            severity = "CRITICAL" if amount > 10 else ("WARNING" if amount >= 1 else "INFO")
            result.overfull_hbox.append(HboxWarning(
                type="overfull", amount_pt=amount,
                lines=[int(m.group(2)), int(m.group(3))],
                context=line[:100], severity=severity
            ))
            return

        # Underfull hbox
        m = re.search(r"Underfull \\hbox \(badness (\d+)\).*lines (\d+)--(\d+)", line)
        if m:
            badness = int(m.group(1))
            severity = "WARNING" if badness >= 10000 else "INFO"
            result.underfull_hbox.append(HboxWarning(
                type="underfull", badness=badness,
                lines=[int(m.group(2)), int(m.group(3))],
                context=line[:100], severity=severity
            ))

    def _check_vbox(self, line: str, result: TypesetDetectResult) -> None:
        """Check for overfull/underfull vbox warnings."""
        # Overfull vbox - always CRITICAL
        m = re.search(r"Overfull \\vbox \(([0-9.]+)pt too high\)", line)
        if m:
            result.overfull_vbox.append(VboxWarning(
                type="overfull", amount_pt=float(m.group(1)),
                context=line[:100], severity="CRITICAL"
            ))
            return

        # Underfull vbox
        m = re.search(r"Underfull \\vbox \(badness (\d+)\)", line)
        if m:
            badness = int(m.group(1))
            severity = "WARNING" if badness >= 10000 else "INFO"
            context = "output active (page break)" if "output is active" in line else line[:100]
            result.underfull_vbox.append(VboxWarning(
                type="underfull", badness=badness, context=context, severity=severity
            ))

    def _check_undefined_ref(self, line: str, result: TypesetDetectResult) -> None:
        """Check for undefined reference warnings."""
        m = re.search(r"Reference `([^']+)'.*page.*?(\d+).*undefined.*line (\d+)", line)
        if m:
            result.undefined_references.append(UndefinedReference(
                reference=m.group(1), page=int(m.group(2)), input_line=int(m.group(3))
            ))

    def _check_undefined_citation(self, line: str, result: TypesetDetectResult) -> None:
        """Check for undefined citation warnings."""
        m = re.search(r"Citation `([^']+)'.*page.*?(\d+).*undefined.*line (\d+)", line)
        if m:
            result.undefined_citations.append(UndefinedCitation(
                citation=m.group(1), page=int(m.group(2)), input_line=int(m.group(3))
            ))

    def _check_float_too_large(self, line: str, result: TypesetDetectResult) -> None:
        """Check for float too large warnings."""
        m = re.search(r"Float too large for page by ([0-9.]+)pt on input line (\d+)", line)
        if m:
            overflow = float(m.group(1))
            severity = "CRITICAL" if overflow > 50 else "WARNING"
            result.float_too_large.append(FloatTooLarge(
                overflow_pt=overflow, input_line=int(m.group(2)), severity=severity
            ))

    def _check_latex_error(self, line: str, result: TypesetDetectResult) -> None:
        """Check for LaTeX errors, filtering known issues."""
        if not line.startswith("! LaTeX Error:"):
            return
        # Check against known issues whitelist
        for pattern, issue_type, cause in KNOWN_ISSUE_PATTERNS:
            if re.search(pattern, line):
                result.known_issues.append(KnownIssue(
                    type=issue_type, message=line, cause=cause
                ))
                return
        # Unknown error - CRITICAL
        m = re.search(r"! LaTeX Error: (.+)\.", line)
        msg = m.group(1) if m else line
        result.latex_errors.append(LatexError(message=msg))

    def _check_package_error(self, line: str, result: TypesetDetectResult) -> None:
        """Check for package errors."""
        m = re.search(r"! Package (\w+) Error: (.+)\.", line)
        if m:
            result.package_errors.append(PackageError(
                package=m.group(1), message=m.group(2)
            ))
