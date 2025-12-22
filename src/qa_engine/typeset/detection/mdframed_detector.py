"""Mdframed page break detector for LaTeX documents."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
from .mdframed_rules import LOG_PATTERNS, SOURCE_PATTERNS, MDFRAMED_RULES


@dataclass
class MdframedIssue:
    """Represents an mdframed-related issue."""
    issue_type: str
    file: str
    line: int
    environment: str
    section: str
    context: str
    severity: str
    fix: str


@dataclass
class MdframedDetectResult:
    """Result of mdframed detection scan."""
    issues: List[MdframedIssue] = field(default_factory=list)
    log_file: str = ""
    mdframed_warnings: int = 0
    tcolorbox_warnings: int = 0

    @property
    def verdict(self) -> str:
        if any(i.severity == "CRITICAL" for i in self.issues):
            return "FAIL"
        return "WARNING" if self.issues else "PASS"

    @property
    def total(self) -> int:
        return len(self.issues)


class MdframedDetector:
    """Detects mdframed/tcolorbox page break issues in logs and sources."""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()

    def detect_in_log(self, log_path: Path) -> MdframedDetectResult:
        """Scan log file for mdframed/tcolorbox warnings."""
        result = MdframedDetectResult(log_file=str(log_path.name))
        if not log_path.exists():
            return result
        content = log_path.read_text(encoding="utf-8", errors="ignore")
        result.issues.extend(self._detect_warnings(content, "mdframed_warning", "mdframed-bad-break"))
        result.issues.extend(self._detect_warnings(content, "tcolorbox_warning", "tcolorbox-split"))
        result.mdframed_warnings = sum(1 for i in result.issues if i.issue_type == "mdframed-bad-break")
        result.tcolorbox_warnings = sum(1 for i in result.issues if i.issue_type == "tcolorbox-split")
        return result

    def _detect_warnings(self, content: str, pattern_key: str, issue_type: str) -> List[MdframedIssue]:
        """Detect warnings of a specific type."""
        issues = []
        for match in re.finditer(LOG_PATTERNS[pattern_key], content, re.IGNORECASE):
            ctx = content[max(0, match.start() - 200):match.end() + 200]
            line_match = re.search(LOG_PATTERNS["line_number"], ctx)
            line = int(line_match.group(1)) if line_match else 0
            env = line_match.group(2) if line_match else "unknown"
            fix_cmd = r"\clearpage" if "mdframed" in issue_type else r"\nopagebreak"
            issues.append(MdframedIssue(
                issue_type=issue_type, file=self._extract_file(ctx), line=line,
                environment=env, section="", context=f"{issue_type} warning",
                severity="WARNING", fix=f"Add {fix_cmd} before line {line}" if line else f"Add {fix_cmd}"
            ))
        return issues

    def _extract_file(self, context: str) -> str:
        """Extract file path from log context."""
        matches = re.findall(r"\(\.?/?([^()\n]+\.tex)\)", context)
        return matches[-1] if matches else "unknown.tex"

    def detect_in_source(self, tex_path: Path) -> List[MdframedIssue]:
        """Analyze source file for potential box issues."""
        if not tex_path.exists():
            return []
        content = tex_path.read_text(encoding="utf-8")
        rel_path = str(tex_path.relative_to(self.project_root))
        issues = []
        for match in re.finditer(SOURCE_PATTERNS["section_near_box"], content):
            line = content[:match.start()].count("\n") + 1
            issues.append(MdframedIssue(
                issue_type="box-near-section", file=rel_path, line=line,
                environment=match.group(3), section=match.group(2),
                context=f"{match.group(3)} after section '{match.group(2)}'",
                severity="WARNING", fix=f"Consider adding \\vspace{{1em}} before line {line}"
            ))
        return issues

    def to_dict(self, result: MdframedDetectResult) -> Dict:
        """Convert result to dictionary."""
        return {
            "skill": "qa-mdframed-detect", "status": "DONE", "verdict": result.verdict,
            "log_file": result.log_file,
            "issues": [{"type": i.issue_type, "file": i.file, "line": i.line,
                        "environment": i.environment, "section": i.section,
                        "context": i.context, "severity": i.severity, "fix": i.fix}
                       for i in result.issues],
            "summary": {"mdframed_warnings": result.mdframed_warnings,
                        "tcolorbox_warnings": result.tcolorbox_warnings, "total": result.total},
            "triggers": ["qa-mdframed-fix"] if result.issues else []
        }

    def get_rules(self) -> Dict[str, str]:
        return MDFRAMED_RULES.copy()
