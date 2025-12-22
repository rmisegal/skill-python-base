"""
Bibliography detector for LaTeX documents.

Detects citation and bibliography issues in LaTeX documents.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Set

from ...domain.interfaces import DetectorInterface
from ...domain.models.issue import Issue
from .bib_rules import BIB_RULES


class BibDetector(DetectorInterface):
    """
    Detects bibliography and citation issues in LaTeX.

    Checks for missing citations, undefined keys, and biblatex issues.
    """

    def __init__(self) -> None:
        self._rules = BIB_RULES

    def detect(
        self,
        content: str,
        file_path: str,
        offset: int = 0,
    ) -> List[Issue]:
        """Detect bibliography issues in content."""
        issues: List[Issue] = []
        lines = content.split("\n")

        # Load defined bib entries from referenced .bib files
        defined_entries = self._load_bib_entries(content, file_path)

        for rule_name, rule_def in self._rules.items():
            pattern = re.compile(rule_def["pattern"])
            context_pattern = rule_def.get("context_pattern")
            document_context = rule_def.get("document_context", False)
            negative_pattern = rule_def.get("negative_pattern")
            has_cite_pattern = rule_def.get("has_cite_pattern")

            # Negative pattern check
            if negative_pattern and re.search(negative_pattern, content):
                continue

            # Has cite pattern check (for standalone rule)
            if has_cite_pattern and not re.search(has_cite_pattern, content):
                continue

            # Document context check
            if document_context and context_pattern:
                if not re.search(context_pattern, content):
                    continue

            for line_num, line in enumerate(lines, start=1):
                if line.strip().startswith("%"):
                    continue

                # Line context check
                if context_pattern and not document_context:
                    if not re.search(context_pattern, line):
                        continue

                for match in pattern.finditer(line):
                    matched = match.group(1) if match.lastindex else match.group(0)

                    # Skip undefined-cite if citation exists in .bib
                    if rule_name == "bib-undefined-cite":
                        cite_keys = [k.strip() for k in matched.split(",")]
                        if all(k in defined_entries for k in cite_keys):
                            continue

                    # Skip missing-file if .bib file exists
                    if rule_name == "bib-missing-file":
                        bib_path = Path(file_path).parent / matched
                        if not bib_path.suffix:
                            bib_path = bib_path.with_suffix(".bib")
                        if bib_path.exists():
                            continue

                    issues.append(
                        Issue(
                            rule=rule_name,
                            file=file_path,
                            line=line_num + offset,
                            content=matched,
                            severity=rule_def["severity"],
                            fix=self._format_fix(rule_def, matched),
                            context={"match_start": match.start()},
                        )
                    )

        return issues

    def _load_bib_entries(self, content: str, file_path: str) -> Set[str]:
        """Load defined entries from referenced .bib files."""
        entries: Set[str] = set()
        base_dir = Path(file_path).parent

        # Find all \addbibresource{} commands
        bib_files = re.findall(r"\\addbibresource\{([^}]+)\}", content)

        for bib_file in bib_files:
            bib_path = base_dir / bib_file
            if not bib_path.suffix:
                bib_path = bib_path.with_suffix(".bib")

            if bib_path.exists():
                try:
                    bib_content = bib_path.read_text(encoding="utf-8")
                    # Extract entry keys: @type{key,
                    keys = re.findall(r"@\w+\{(\w+),", bib_content)
                    entries.update(keys)
                except Exception:
                    pass

        return entries

    def _format_fix(self, rule_def: dict, content: str) -> str:
        """Format fix suggestion with matched content."""
        template = rule_def.get("fix_template", "")
        if "{}" in template:
            return template.format(content)
        return template

    def get_rules(self) -> Dict[str, str]:
        """Return dict of rule_name -> description."""
        return {name: rule["description"] for name, rule in self._rules.items()}
