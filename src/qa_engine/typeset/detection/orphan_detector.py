"""Section orphan detector for LaTeX documents."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
from .orphan_rules import SECTION_PATTERNS, NEEDSPACE_PATTERN, ORPHAN_THRESHOLDS, ORPHAN_RULES


@dataclass
class OrphanIssue:
    """Represents a section orphan issue."""
    rule: str
    file: str
    line: int
    section_type: str
    section_title: str
    severity: str
    message: str
    fix: str


@dataclass
class OrphanDetectResult:
    """Result of orphan detection scan."""
    issues: List[OrphanIssue] = field(default_factory=list)
    sections_checked: int = 0
    sections_protected: int = 0
    sections_unprotected: int = 0

    @property
    def verdict(self) -> str:
        high = sum(1 for i in self.issues if i.severity == "HIGH")
        return "FAIL" if high > 0 else ("WARNING" if self.issues else "PASS")


class SectionOrphanDetector:
    """Detects section orphans in LaTeX source files."""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()

    def detect_in_file(self, file_path: Path) -> OrphanDetectResult:
        """Detect orphan issues in a LaTeX file."""
        result = OrphanDetectResult()
        if not file_path.exists():
            return result
        content = file_path.read_text(encoding="utf-8")
        rel_path = str(file_path.relative_to(self.project_root)) if self.project_root in file_path.parents else str(file_path)
        result.issues.extend(self._detect_missing_needspace(content, rel_path))
        result.issues.extend(self._detect_short_content(content, rel_path))
        result.sections_checked = self._count_sections(content)
        result.sections_protected = self._count_protected_sections(content)
        result.sections_unprotected = result.sections_checked - result.sections_protected
        return result

    def detect_in_content(self, content: str, file_path: str = "input.tex") -> OrphanDetectResult:
        """Detect orphan issues in content string."""
        result = OrphanDetectResult()
        result.issues.extend(self._detect_missing_needspace(content, file_path))
        result.issues.extend(self._detect_short_content(content, file_path))
        result.sections_checked = self._count_sections(content)
        result.sections_protected = self._count_protected_sections(content)
        result.sections_unprotected = result.sections_checked - result.sections_protected
        return result

    def _detect_missing_needspace(self, content: str, file_path: str) -> List[OrphanIssue]:
        """Detect sections without needspace protection."""
        issues = []
        lines = content.split("\n")
        for sec_type, pattern in SECTION_PATTERNS.items():
            for match in re.finditer(pattern, content):
                line_num = content[:match.start()].count("\n") + 1
                title = match.group(1)
                # Check if needspace precedes this section (within 3 lines)
                start_line = max(0, line_num - 4)
                preceding = "\n".join(lines[start_line:line_num - 1])
                has_needspace = bool(re.search(NEEDSPACE_PATTERN, preceding))
                if not has_needspace:
                    severity = "HIGH" if "section" in sec_type and "sub" not in sec_type else "MEDIUM"
                    rule = "missing-needspace-subsection" if "sub" in sec_type else "missing-needspace-section"
                    threshold = ORPHAN_THRESHOLDS.get(sec_type, 5)
                    issues.append(OrphanIssue(
                        rule=rule, file=file_path, line=line_num, section_type=sec_type,
                        section_title=title[:50], severity=severity,
                        message=f"{sec_type} without orphan protection",
                        fix=f"Add \\par\\needspace{{{threshold}\\baselineskip}} before line {line_num}"
                    ))
        return issues

    def _detect_short_content(self, content: str, file_path: str) -> List[OrphanIssue]:
        """Detect sections with very short content before next section."""
        issues = []
        # Find all section positions
        all_sections = []
        for sec_type, pattern in SECTION_PATTERNS.items():
            for match in re.finditer(pattern, content):
                all_sections.append((match.start(), match.end(), sec_type, match.group(1)))
        all_sections.sort(key=lambda x: x[0])
        # Check content between consecutive sections
        for i, (start, end, sec_type, title) in enumerate(all_sections[:-1]):
            next_start = all_sections[i + 1][0]
            between = content[end:next_start]
            # Count non-empty, non-comment lines
            lines = [l for l in between.split("\n") if l.strip() and not l.strip().startswith("%")]
            threshold = ORPHAN_THRESHOLDS.get(sec_type, 5)
            if len(lines) < threshold and len(lines) > 0:
                line_num = content[:start].count("\n") + 1
                issues.append(OrphanIssue(
                    rule="short-content-after-section", file=file_path, line=line_num,
                    section_type=sec_type, section_title=title[:50], severity="LOW",
                    message=f"Only {len(lines)} content lines before next section (need {threshold})",
                    fix=f"Consider adding more content or merging with next section"
                ))
        return issues

    def _count_sections(self, content: str) -> int:
        """Count total sections in content."""
        count = 0
        for pattern in SECTION_PATTERNS.values():
            count += len(re.findall(pattern, content))
        return count

    def _count_protected_sections(self, content: str) -> int:
        """Count sections with needspace protection."""
        count = 0
        lines = content.split("\n")
        for sec_type, pattern in SECTION_PATTERNS.items():
            for match in re.finditer(pattern, content):
                line_num = content[:match.start()].count("\n") + 1
                start_line = max(0, line_num - 4)
                preceding = "\n".join(lines[start_line:line_num - 1])
                if re.search(NEEDSPACE_PATTERN, preceding):
                    count += 1
        return count

    def to_dict(self, result: OrphanDetectResult) -> Dict:
        """Convert result to dictionary."""
        return {
            "skill": "qa-section-orphan-detect", "status": "DONE", "verdict": result.verdict,
            "issues": [{"rule": i.rule, "file": i.file, "line": i.line,
                        "section_type": i.section_type, "section_title": i.section_title,
                        "severity": i.severity, "message": i.message, "fix": i.fix}
                       for i in result.issues],
            "summary": {"sections_checked": result.sections_checked,
                        "sections_protected": result.sections_protected,
                        "sections_unprotected": result.sections_unprotected,
                        "issues_found": len(result.issues)},
            "triggers": ["qa-section-orphan-fix"] if result.issues else []
        }

    def get_rules(self) -> Dict[str, str]:
        return ORPHAN_RULES.copy()
