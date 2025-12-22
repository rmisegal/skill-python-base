"""Hbox fixer for LaTeX documents. Fixes overfull/underfull hbox warnings."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

@dataclass
class HboxFix:
    """Represents an hbox fix that was applied."""
    file: str
    line: int
    issue_type: str
    fix_type: str
    before: str
    after: str

@dataclass
class ManualReview:
    """Case requiring LLM intervention."""
    file: str
    line: int
    issue_type: str
    content: str
    context: str
    suggestion: str
    options: List[str]

@dataclass
class HboxFixResult:
    """Result of hbox fix operation."""
    fixes_applied: List[HboxFix] = field(default_factory=list)
    manual_review: List[ManualReview] = field(default_factory=list)

    @property
    def status(self) -> str:
        if self.fixes_applied: return "DONE"
        return "MANUAL_REVIEW" if self.manual_review else "NO_CHANGES"

class HboxFixer:
    """Fixes hbox issues in LaTeX documents."""
    ENCELL_PATTERN = re.compile(r'(\\encell\{)([^}]+)(\})')
    CODE_IDENTIFIER = re.compile(r'[a-zA-Z_][a-zA-Z0-9_.]+\.[a-zA-Z_][a-zA-Z0-9_.]+')
    LONG_EN_PATTERN = re.compile(r'\\en\{([^}]{30,})\}')
    LONG_WORD = re.compile(r'\b[a-zA-Z]{15,}\b')

    def fix_file(self, file_path: Path, issues: Optional[List[Dict]] = None) -> HboxFixResult:
        """Fix hbox issues in a file."""
        if not file_path.exists(): return HboxFixResult()
        content = file_path.read_text(encoding="utf-8")
        fixed, result = self.fix_content(content, str(file_path), issues)
        if result.fixes_applied: file_path.write_text(fixed, encoding="utf-8")
        return result

    def fix_content(self, content: str, file_path: str = "", issues: Optional[List[Dict]] = None) -> Tuple[str, HboxFixResult]:
        """Fix hbox issues in content."""
        result, lines = HboxFixResult(), content.split("\n")
        if issues:
            for issue in issues:
                ln = issue.get("line", 0)
                if 0 < ln <= len(lines): self._process_issue(lines, ln, file_path, issue, result)
        else:
            for i, line in enumerate(lines):
                fixed_line, fix = self._auto_fix_line(line, i + 1, file_path)
                if fix: lines[i], _ = fixed_line, result.fixes_applied.append(fix)
        return "\n".join(lines), result

    def _process_issue(self, lines: List[str], ln: int, fp: str, issue: Dict, result: HboxFixResult) -> None:
        """Process a detected issue - auto-fix or queue for LLM."""
        line, itype = lines[ln - 1], issue.get("type", "overfull")
        if self.ENCELL_PATTERN.search(line):
            fixed, fix = self._fix_table_cell(line, ln, fp, itype)
            if fix: lines[ln - 1], _ = fixed, result.fixes_applied.append(fix); return
        ctx = "\n".join(f"{i+1}: {lines[i]}" for i in range(max(0, ln-3), min(len(lines), ln+2)))
        result.manual_review.append(self._create_review(fp, ln, itype, line, ctx))

    def _create_review(self, fp: str, ln: int, itype: str, line: str, ctx: str) -> ManualReview:
        """Create a manual review item with LLM guidance."""
        if self.LONG_EN_PATTERN.search(line):
            sug, opts = "Long English phrase - reword or abbreviate", ["Reword", "Add hyphenation", "Abbreviate"]
        elif self.LONG_WORD.search(line):
            sug, opts = "Long word - add hyphenation", ["Add \\- hints", "Use shorter synonym"]
        elif itype == "underfull":
            sug, opts = "Line too loose - add content", ["Add content", "Combine paragraphs", "Use \\hfill"]
        else:
            sug, opts = "Overfull line - reduce width", ["Reword", "Add line break", "Use \\sloppy"]
        return ManualReview(file=fp, line=ln, issue_type=itype, content=line[:80], context=ctx, suggestion=sug, options=opts)

    def _auto_fix_line(self, line: str, ln: int, fp: str) -> Tuple[str, Optional[HboxFix]]:
        """Auto-fix patterns that are safe to change."""
        m = self.ENCELL_PATTERN.search(line)
        if m and self.CODE_IDENTIFIER.search(m.group(2)) and len(m.group(2)) > 20:
            return self._fix_table_cell(line, ln, fp, "overfull")
        return line, None

    def _fix_table_cell(self, line: str, ln: int, fp: str, itype: str) -> Tuple[str, Optional[HboxFix]]:
        """Add \\small to table cell."""
        before = line
        fixed = self.ENCELL_PATTERN.sub(lambda m: m.group(0) if m.group(2).startswith("\\small") else f"{m.group(1)}\\small {m.group(2)}{m.group(3)}", line)
        if fixed != before:
            return fixed, HboxFix(file=fp, line=ln, issue_type=itype, fix_type="small", before=before[:60], after=fixed[:60])
        return line, None

    def _wrap_with_sloppy(self, line: str, ln: int, fp: str) -> Tuple[str, Optional[HboxFix]]:
        """Wrap line with {\\sloppy ...}."""
        s = line.strip()
        if "\\sloppy" in line or s.startswith("\\begin") or s.startswith("\\end"): return line, None
        indent, fixed = line[:len(line) - len(line.lstrip())], f"{line[:len(line) - len(line.lstrip())]}{{\\sloppy {s}}}"
        return fixed, HboxFix(file=fp, line=ln, issue_type="overfull", fix_type="sloppy", before=line[:60], after=fixed[:60])

    def add_allowbreak(self, content: str) -> str:
        """Add \\allowbreak after dots in code identifiers."""
        return re.sub(r'\.(?=[a-zA-Z])', r'.\\allowbreak ', content)

    def apply_llm_fix(self, content: str, ln: int, fix_type: str, new_content: str, fp: str = "") -> Tuple[str, HboxFix]:
        """Apply an LLM-suggested fix."""
        lines = content.split("\n")
        before = lines[ln - 1]
        lines[ln - 1] = new_content
        return "\n".join(lines), HboxFix(file=fp, line=ln, issue_type="overfull", fix_type=fix_type, before=before[:60], after=new_content[:60])

    def generate_llm_prompt(self, r: ManualReview) -> str:
        """Generate prompt for LLM to fix the issue."""
        return f"Fix this LaTeX hbox issue:\n\nIssue: {r.issue_type} at {r.file}:{r.line}\nSuggestion: {r.suggestion}\n\nContext:\n{r.context}\n\nProblematic line:\n{r.content}\n\nOptions: {', '.join(r.options)}\n\nReturn ONLY the fixed line, no explanation."

    def to_dict(self, result: HboxFixResult) -> Dict:
        """Convert result to dictionary matching skill output format."""
        return {
            "skill": "qa-typeset-fix-hbox", "status": result.status,
            "fixes_applied": [{"file": f.file, "line": f.line, "issue_type": f.issue_type,
                               "fix_type": f.fix_type, "before": f.before, "after": f.after} for f in result.fixes_applied],
            "manual_review": [{"file": r.file, "line": r.line, "issue_type": r.issue_type,
                               "content": r.content, "suggestion": r.suggestion, "options": r.options} for r in result.manual_review],
            "summary": {"auto_fixed": len(result.fixes_applied), "needs_review": len(result.manual_review)}}
