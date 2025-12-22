"""
Vbox fixer for LaTeX documents.

Fixes overfull/underfull vbox warnings matching qa-typeset-fix-vbox skill.md v1.0.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class VboxFixType(Enum):
    """Fix types for vbox issues."""
    RAGGEDBOTTOM = "raggedbottom"
    VFILL = "vfill"
    VSPACE = "vspace"
    ENLARGETHISPAGE = "enlargethispage"
    FLOAT_PLACEMENT = "float_placement"
    NEWPAGE = "newpage"
    PAGEBREAK = "pagebreak"
    FLOAT_FRACTIONS = "float_fractions"


@dataclass
class VboxFix:
    """Represents a vbox fix that was applied."""
    file: str
    line: int
    issue_type: str  # overfull, underfull
    fix_type: str  # raggedbottom, vfill, enlargethispage, etc.
    before: str
    after: str
    location: str = "content"  # preamble or content


@dataclass
class VboxManualReview:
    """Case requiring LLM intervention."""
    file: str
    line: int
    issue_type: str
    badness: Optional[int]
    amount_pt: Optional[float]
    context: str
    suggestion: str
    options: List[str]


@dataclass
class VboxFixResult:
    """Result of vbox fix operation."""
    fixes_applied: List[VboxFix] = field(default_factory=list)
    manual_review: List[VboxManualReview] = field(default_factory=list)
    preamble_suggestions: List[str] = field(default_factory=list)

    @property
    def status(self) -> str:
        if self.fixes_applied:
            return "DONE"
        return "MANUAL_REVIEW" if self.manual_review else "NO_CHANGES"


class VboxFixer:
    """
    Fixes vbox issues in LaTeX documents.

    Aligned with qa-typeset-fix-vbox skill.md v1.0:
    - Problem 1: Underfull vbox (Page Too Empty)
    - Problem 2: Overfull vbox (Page Too Full)
    """

    # Patterns
    FLOAT_ENV = re.compile(r"\\begin\{(figure|table)\}(\[[^\]]*\])?")
    NEWPAGE_CMD = re.compile(r"\\(newpage|clearpage|cleardoublepage)")
    RAGGEDBOTTOM_CMD = re.compile(r"\\raggedbottom")

    # Severity thresholds from skill.md
    SEVERITY_THRESHOLDS = {
        "ignore": 1000,      # < 1000: INFO (usually ignore)
        "consider": 5000,    # 1000-5000: INFO (consider fixing)
        "should_fix": 9999,  # 5000-9999: WARNING (should fix)
        "must_review": 10000 # 10000: WARNING (definitely review)
    }

    def classify_severity(self, badness: Optional[int] = None,
                          is_overfull: bool = False) -> str:
        """Classify severity based on skill.md guide."""
        if is_overfull:
            return "CRITICAL"  # Overfull vbox must fix
        if badness is None:
            return "INFO"
        if badness < self.SEVERITY_THRESHOLDS["ignore"]:
            return "INFO"
        if badness < self.SEVERITY_THRESHOLDS["consider"]:
            return "INFO"
        if badness < self.SEVERITY_THRESHOLDS["should_fix"]:
            return "WARNING"
        return "WARNING"  # badness 10000

    def fix_preamble(self, content: str, file_path: str = "") -> Tuple[str, VboxFixResult]:
        """Add global fixes to preamble."""
        result = VboxFixResult()

        # Check if raggedbottom already present
        if self.RAGGEDBOTTOM_CMD.search(content):
            return content, result

        # Find preamble location (after \documentclass, before \begin{document})
        doc_class_match = re.search(r"\\documentclass.*?\n", content)
        begin_doc_match = re.search(r"\\begin\{document\}", content)

        if doc_class_match and begin_doc_match:
            insert_pos = begin_doc_match.start()
            raggedbottom_line = "\n\\raggedbottom  % QA: Allow uneven page bottoms\n"

            before = content[insert_pos-20:insert_pos]
            content = content[:insert_pos] + raggedbottom_line + content[insert_pos:]
            after = content[insert_pos:insert_pos+len(raggedbottom_line)+20]

            result.fixes_applied.append(VboxFix(
                file=file_path, line=0, issue_type="underfull",
                fix_type="raggedbottom", before=before.strip(),
                after=after.strip(), location="preamble"
            ))

        return content, result

    def add_vfill(self, content: str, line_num: int, file_path: str = "") -> Tuple[str, VboxFix]:
        """Add \\vfill for stretchable space."""
        lines = content.split("\n")
        before = lines[line_num - 1]
        indent = before[:len(before) - len(before.lstrip())]
        lines.insert(line_num - 1, f"{indent}\\vfill")
        after = "\\vfill inserted before line"

        fix = VboxFix(file=file_path, line=line_num, issue_type="underfull",
                      fix_type="vfill", before=before[:60], after=after)
        return "\n".join(lines), fix

    def add_vspace(self, content: str, line_num: int, space: str = "2cm",
                   file_path: str = "") -> Tuple[str, VboxFix]:
        """Add \\vspace for specific vertical space."""
        lines = content.split("\n")
        before = lines[line_num - 1]
        indent = before[:len(before) - len(before.lstrip())]
        lines.insert(line_num - 1, f"{indent}\\vspace{{{space}}}")
        after = f"\\vspace{{{space}}} inserted"

        fix = VboxFix(file=file_path, line=line_num, issue_type="underfull",
                      fix_type="vspace", before=before[:60], after=after)
        return "\n".join(lines), fix

    def add_enlargethispage(self, content: str, line_num: int,
                            amount: str = "2\\baselineskip",
                            file_path: str = "") -> Tuple[str, VboxFix]:
        """Add \\enlargethispage to adjust page height."""
        lines = content.split("\n")
        before = lines[line_num - 1]
        indent = before[:len(before) - len(before.lstrip())]
        lines.insert(line_num - 1, f"{indent}\\enlargethispage{{{amount}}}")
        after = f"\\enlargethispage{{{amount}}} inserted"

        fix = VboxFix(file=file_path, line=line_num, issue_type="underfull",
                      fix_type="enlargethispage", before=before[:60], after=after)
        return "\n".join(lines), fix

    def fix_float_placement(self, content: str, line_num: int,
                            placement: str = "htbp",
                            file_path: str = "") -> Tuple[str, Optional[VboxFix]]:
        """Change float placement options."""
        lines = content.split("\n")
        line = lines[line_num - 1]
        match = self.FLOAT_ENV.search(line)
        if not match:
            return content, None

        before = line
        env_type = match.group(1)
        # Replace or add placement option
        if match.group(2):
            new_line = re.sub(r"\[[^\]]*\]", f"[{placement}]", line, count=1)
        else:
            new_line = line.replace(f"\\begin{{{env_type}}}", f"\\begin{{{env_type}}}[{placement}]")

        lines[line_num - 1] = new_line
        fix = VboxFix(file=file_path, line=line_num, issue_type="underfull",
                      fix_type="float_placement", before=before[:60], after=new_line[:60])
        return "\n".join(lines), fix

    def add_newpage(self, content: str, line_num: int,
                    file_path: str = "") -> Tuple[str, VboxFix]:
        """Add \\newpage to move content."""
        lines = content.split("\n")
        before = lines[line_num - 1]
        indent = before[:len(before) - len(before.lstrip())]
        lines.insert(line_num - 1, f"{indent}\\newpage")
        after = "\\newpage inserted before line"

        fix = VboxFix(file=file_path, line=line_num, issue_type="overfull",
                      fix_type="newpage", before=before[:60], after=after)
        return "\n".join(lines), fix

    def create_review(self, file_path: str, line_num: int, issue_type: str,
                      badness: Optional[int] = None,
                      amount_pt: Optional[float] = None,
                      context: str = "") -> VboxManualReview:
        """Create a manual review item with LLM guidance."""
        if issue_type == "underfull":
            suggestion = "Page too empty - add content or use raggedbottom"
            options = [
                "Option A: Let LaTeX handle it (often best)",
                "Option B: Add \\raggedbottom to preamble",
                "Option C: Add \\vfill for stretchable space",
                "Option D: Adjust float placement [htbp]",
                "Option E: Use \\enlargethispage{2\\baselineskip}"
            ]
        else:  # overfull
            suggestion = "Page too full - move content or reduce"
            options = [
                "Option A: Add \\newpage before content",
                "Option B: Reduce content on page",
                "Option C: Use \\enlargethispage{-1\\baselineskip}",
                "Option D: Force float to page [p]"
            ]

        return VboxManualReview(
            file=file_path, line=line_num, issue_type=issue_type,
            badness=badness, amount_pt=amount_pt, context=context,
            suggestion=suggestion, options=options
        )

    def get_global_settings(self) -> Dict[str, str]:
        """Return global settings recommendations from skill.md."""
        return {
            "raggedbottom": "\\raggedbottom  % Allow uneven page bottoms",
            "topfraction": "\\renewcommand{\\topfraction}{0.9}",
            "bottomfraction": "\\renewcommand{\\bottomfraction}{0.9}",
            "textfraction": "\\renewcommand{\\textfraction}{0.1}",
            "floatpagefraction": "\\renewcommand{\\floatpagefraction}{0.7}",
            "topnumber": "\\setcounter{topnumber}{3}",
            "bottomnumber": "\\setcounter{bottomnumber}{3}",
            "totalnumber": "\\setcounter{totalnumber}{5}",
        }

    def should_ignore(self, issue_type: str, badness: Optional[int] = None,
                      context: str = "") -> bool:
        """Check if warning is safe to ignore per skill.md."""
        if issue_type == "overfull":
            return False  # Never ignore overfull
        # Safe to ignore underfull at chapter/section starts
        if "chapter" in context.lower() or "section" in context.lower():
            return True
        if "newpage" in context.lower():
            return True
        return badness is not None and badness < 5000

    def to_dict(self, result: VboxFixResult) -> Dict:
        """Convert result to dictionary matching skill output format."""
        return {
            "skill": "qa-typeset-fix-vbox",
            "status": result.status,
            "fixes_applied": [
                {"file": f.file, "line": f.line, "issue_type": f.issue_type,
                 "fix_type": f.fix_type, "before": f.before, "after": f.after,
                 "location": f.location}
                for f in result.fixes_applied
            ],
            "manual_review": [
                {"file": r.file, "line": r.line, "issue_type": r.issue_type,
                 "badness": r.badness, "amount_pt": r.amount_pt,
                 "suggestion": r.suggestion, "options": r.options}
                for r in result.manual_review
            ],
            "preamble_suggestions": result.preamble_suggestions,
            "summary": {
                "auto_fixed": len(result.fixes_applied),
                "needs_review": len(result.manual_review)
            }
        }

    def generate_llm_prompt(self, review: VboxManualReview) -> str:
        """Generate prompt for LLM to fix the issue."""
        return f"""Fix this LaTeX vbox issue:

Issue: {review.issue_type} vbox at {review.file}:{review.line}
{"Badness: " + str(review.badness) if review.badness else ""}
{"Overflow: " + str(review.amount_pt) + "pt" if review.amount_pt else ""}
Suggestion: {review.suggestion}

Context:
{review.context}

Available fix options:
{chr(10).join(review.options)}

Select the best option and explain why."""
