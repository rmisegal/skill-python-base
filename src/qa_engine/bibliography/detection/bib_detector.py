"""
Bibliography detector for LaTeX documents.

Implements qa-bib-detect skill.md v1.1 - detects citation and bibliography issues.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from .bib_models import (
    BibDetectResult, BibIssue, BibIssueType, BibSeverity, CitationLocation
)


class BibDetector:
    """
    Detects bibliography issues in LaTeX documents.

    Aligned with qa-bib-detect skill.md v1.1:
    - Step 1: Extract citations from .tex files
    - Step 2: Parse .bib file
    - Step 3: Cross-reference check
    - Step 4: Check for bibliography command
    - Step 5: Verify TOC entry
    - Step 6: Verify bibliography rendered
    """

    # Citation command patterns (Step 1)
    # Handle optional arguments: \cite[p.~42]{key} -> captures {key}
    CITE_PATTERNS = [
        r"\\cite(?:\[[^\]]*\])?\{([^}]+)\}",
        r"\\citep(?:\[[^\]]*\])?\{([^}]+)\}",
        r"\\citet(?:\[[^\]]*\])?\{([^}]+)\}",
        r"\\parencite(?:\[[^\]]*\])?\{([^}]+)\}",
        r"\\textcite(?:\[[^\]]*\])?\{([^}]+)\}",
        r"\\autocite(?:\[[^\]]*\])?\{([^}]+)\}",
        r"\\footcite(?:\[[^\]]*\])?\{([^}]+)\}",
        r"\\fullcite(?:\[[^\]]*\])?\{([^}]+)\}",
    ]

    # Bibliography entry pattern (Step 2)
    BIB_ENTRY_PATTERN = r"@\w+\{([^,]+),"

    # Print bibliography patterns (Step 4)
    PRINTBIB_PATTERNS = [
        r"\\printbibliography",
        r"\\printenglishbibliography",
        r"\\printhebrewbibliography",
        r"\\bibliography\{",
    ]

    # TOC entry pattern (Step 5)
    TOC_PATTERN = r"contentsline.*\{.*(?:References|Bibliography|מקורות).*\}"

    # English environment pattern (Pattern 6 - v1.1)
    ENGLISH_ENV_PATTERN = r"\\begin\{english\}"

    # Bibitemsep pattern (Pattern 7 - v1.1)
    BIBITEMSEP_PATTERN = r"\\setlength\{\\bibitemsep\}"

    def detect_in_project(self, project_path: Path,
                          bib_file: Optional[Path] = None) -> BibDetectResult:
        """Detect bibliography issues in a LaTeX project."""
        result = BibDetectResult()

        # Find all .tex files
        tex_files = list(project_path.rglob("*.tex"))

        # Step 1: Extract citations
        for tex_file in tex_files:
            citations = self.extract_citations(tex_file)
            for key, line in citations:
                result.citation_locations.append(CitationLocation(
                    key=key, file=str(tex_file.relative_to(project_path)), line=line
                ))
                if key not in result.citations_unique:
                    result.citations_unique.append(key)
        result.citations_total = len(result.citation_locations)

        # Step 2: Parse .bib file
        if bib_file is None:
            bib_file = self._find_bib_file(project_path, tex_files)
        if bib_file and bib_file.exists():
            result.bib_file = str(bib_file.relative_to(project_path))
            result.bib_entries = self.extract_bib_keys(bib_file)

        # Step 3: Cross-reference check
        self._check_cross_references(result)

        # Step 4-6: Check bibliography commands and TOC
        self._check_bibliography_setup(result, tex_files, project_path)

        return result

    def extract_citations(self, tex_file: Path) -> List[Tuple[str, int]]:
        """Extract all citation keys with line numbers from a .tex file."""
        if not tex_file.exists():
            return []

        content = tex_file.read_text(encoding="utf-8", errors="ignore")
        citations = []

        for line_num, line in enumerate(content.split("\n"), 1):
            for pattern in self.CITE_PATTERNS:
                for match in re.finditer(pattern, line):
                    # Handle multiple citations: \cite{key1,key2,key3}
                    keys = match.group(1).split(",")
                    for key in keys:
                        citations.append((key.strip(), line_num))

        return citations

    def extract_citations_from_content(self, content: str) -> List[Tuple[str, int]]:
        """Extract citations from content string."""
        citations = []
        for line_num, line in enumerate(content.split("\n"), 1):
            for pattern in self.CITE_PATTERNS:
                for match in re.finditer(pattern, line):
                    keys = match.group(1).split(",")
                    for key in keys:
                        citations.append((key.strip(), line_num))
        return citations

    def extract_bib_keys(self, bib_file: Path) -> List[str]:
        """Extract all entry keys from a .bib file."""
        if not bib_file.exists():
            return []

        content = bib_file.read_text(encoding="utf-8", errors="ignore")
        return self.extract_bib_keys_from_content(content)

    def extract_bib_keys_from_content(self, content: str) -> List[str]:
        """Extract bibliography keys from content string."""
        keys = []
        for match in re.finditer(self.BIB_ENTRY_PATTERN, content):
            keys.append(match.group(1).strip())
        return keys

    def _find_bib_file(self, project_path: Path, tex_files: List[Path]) -> Optional[Path]:
        """Auto-detect .bib file from \\addbibresource command."""
        for tex_file in tex_files:
            content = tex_file.read_text(encoding="utf-8", errors="ignore")
            match = re.search(r"\\addbibresource\{([^}]+)\}", content)
            if match:
                bib_path = project_path / match.group(1)
                if bib_path.exists():
                    return bib_path
        # Fallback: find any .bib file
        bib_files = list(project_path.rglob("*.bib"))
        return bib_files[0] if bib_files else None

    def _check_cross_references(self, result: BibDetectResult) -> None:
        """Cross-check citations vs bib entries (Step 3)."""
        cited_keys = set(result.citations_unique)
        bib_keys = set(result.bib_entries)

        # Missing entries
        for key in cited_keys - bib_keys:
            loc = next((l for l in result.citation_locations if l.key == key), None)
            result.issues.append(BibIssue(
                type=BibIssueType.MISSING_ENTRY,
                severity=BibSeverity.CRITICAL,
                key=key,
                cited_in=loc.file if loc else None,
                line=loc.line if loc else None,
                message=f"Citation '{key}' not found in bibliography"
            ))

        # Unused entries (WARNING per skill.md verdict logic)
        for key in bib_keys - cited_keys:
            result.issues.append(BibIssue(
                type=BibIssueType.UNUSED_ENTRY,
                severity=BibSeverity.WARNING,
                key=key,
                message=f"Entry '{key}' defined but never cited"
            ))

    def _check_bibliography_setup(self, result: BibDetectResult,
                                   tex_files: List[Path], project_path: Path) -> None:
        """Check for printbibliography, TOC, and English environment."""
        for tex_file in tex_files:
            content = tex_file.read_text(encoding="utf-8", errors="ignore")

            # Step 4: Check for printbibliography
            for pattern in self.PRINTBIB_PATTERNS:
                if re.search(pattern, content):
                    result.has_printbib = True
                    # Pattern 6: Check if in English environment (v1.1)
                    self._check_english_wrapper(content, result)
                    # Pattern 7: Check bibitemsep (v1.1)
                    result.has_bibitemsep = bool(re.search(self.BIBITEMSEP_PATTERN, content))
                    break

            # Step 5: Check TOC
            if "bibintoc" in content or re.search(r"\\addcontentsline\{toc\}.*bib", content):
                result.bib_in_toc = True

        # Check .toc file if exists
        toc_files = list(project_path.rglob("*.toc"))
        for toc_file in toc_files:
            toc_content = toc_file.read_text(encoding="utf-8", errors="ignore")
            if re.search(self.TOC_PATTERN, toc_content, re.IGNORECASE):
                result.bib_in_toc = True

        # Add issues for missing setup
        if not result.has_printbib and result.citations_total > 0:
            result.issues.append(BibIssue(
                type=BibIssueType.MISSING_PRINTBIB,
                severity=BibSeverity.CRITICAL,
                message="No \\printbibliography command found"
            ))

        if result.has_printbib and not result.bib_in_toc:
            result.issues.append(BibIssue(
                type=BibIssueType.NOT_IN_TOC,
                severity=BibSeverity.WARNING,
                message="Bibliography not in table of contents"
            ))

        if not result.bib_in_english and result.has_printbib:
            result.issues.append(BibIssue(
                type=BibIssueType.NOT_IN_ENGLISH,
                severity=BibSeverity.CRITICAL,
                message="Bibliography not wrapped in \\begin{english} environment"
            ))

        if not result.has_bibitemsep and result.has_printbib:
            result.issues.append(BibIssue(
                type=BibIssueType.SPACING_TOO_LARGE,
                severity=BibSeverity.WARNING,
                message="No \\bibitemsep setting - spacing may be too large"
            ))

    def _check_english_wrapper(self, content: str, result: BibDetectResult) -> None:
        """Check if printbibliography is wrapped in English environment."""
        # Find printbibliography position
        printbib_match = re.search(r"\\printbibliography", content)
        if not printbib_match:
            return

        # Check for preceding \begin{english}
        before = content[:printbib_match.start()]
        english_count = len(re.findall(r"\\begin\{english\}", before))
        end_english_count = len(re.findall(r"\\end\{english\}", before))
        result.bib_in_english = english_count > end_english_count

    def detect_content(self, tex_content: str, bib_content: str = "") -> BibDetectResult:
        """Detect issues in content strings (for testing)."""
        result = BibDetectResult()

        # Extract citations
        citations = self.extract_citations_from_content(tex_content)
        for key, line in citations:
            result.citation_locations.append(CitationLocation(key=key, file="test.tex", line=line))
            if key not in result.citations_unique:
                result.citations_unique.append(key)
        result.citations_total = len(result.citation_locations)

        # Extract bib keys
        if bib_content:
            result.bib_entries = self.extract_bib_keys_from_content(bib_content)

        # Cross-reference
        self._check_cross_references(result)

        # Check setup
        for pattern in self.PRINTBIB_PATTERNS:
            if re.search(pattern, tex_content):
                result.has_printbib = True
                self._check_english_wrapper(tex_content, result)
                result.has_bibitemsep = bool(re.search(self.BIBITEMSEP_PATTERN, tex_content))
                break

        if "bibintoc" in tex_content:
            result.bib_in_toc = True

        # Add issues
        if not result.has_printbib and result.citations_total > 0:
            result.issues.append(BibIssue(
                type=BibIssueType.MISSING_PRINTBIB, severity=BibSeverity.CRITICAL,
                message="No \\printbibliography command found"
            ))
        if result.has_printbib and not result.bib_in_toc:
            result.issues.append(BibIssue(
                type=BibIssueType.NOT_IN_TOC, severity=BibSeverity.WARNING,
                message="Bibliography not in table of contents"
            ))
        if not result.bib_in_english and result.has_printbib:
            result.issues.append(BibIssue(
                type=BibIssueType.NOT_IN_ENGLISH, severity=BibSeverity.CRITICAL,
                message="Bibliography not wrapped in \\begin{english}"
            ))

        return result

    def to_dict(self, result: BibDetectResult) -> Dict:
        """Convert result to dictionary matching skill.md output format."""
        return {
            "skill": "qa-bib-detect", "status": "DONE", "verdict": result.verdict,
            "citations": {
                "total": result.citations_total,
                "unique_keys": result.citations_unique,
                "locations": [{"key": l.key, "file": l.file, "line": l.line}
                              for l in result.citation_locations]
            },
            "bib_file": {"path": result.bib_file, "total_entries": len(result.bib_entries),
                         "keys": result.bib_entries},
            "issues": [{"type": i.type.value, "key": i.key, "cited_in": i.cited_in,
                        "line": i.line, "severity": i.severity.value, "message": i.message}
                       for i in result.issues],
            "summary": {
                "missing_entries": len(result.missing_entries),
                "unused_entries": len(result.unused_entries),
                "has_printbib": result.has_printbib,
                "bib_in_toc": result.bib_in_toc, "bib_rendered": result.bib_rendered
            },
            "triggers": result.triggers
        }
