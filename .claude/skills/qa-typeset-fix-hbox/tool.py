"""Python tool for qa-typeset-fix-hbox skill with LLM-assisted fixes."""
from pathlib import Path
from typing import Dict, List, Optional
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from qa_engine.typeset.fixing import HboxFixer, ManualReview


def fix_content(
    content: str, file_path: str = "", issues: Optional[List[Dict]] = None
) -> tuple:
    """
    Fix hbox issues in content string (Phase 1: auto-fix).

    Returns:
        Tuple of (fixed_content, result_dict)
        Check result_dict["manual_review"] for items needing LLM
    """
    fixer = HboxFixer()
    fixed_content, result = fixer.fix_content(content, file_path, issues)
    return fixed_content, fixer.to_dict(result)


def fix_file(file_path: str, issues: Optional[List[Dict]] = None) -> dict:
    """Fix hbox issues in a file (Phase 1: auto-fix)."""
    path = Path(file_path)
    fixer = HboxFixer()

    if not path.exists():
        return {"skill": "qa-typeset-fix-hbox", "status": "ERROR",
                "error": f"File not found: {file_path}"}

    result = fixer.fix_file(path, issues)
    return fixer.to_dict(result)


def generate_llm_prompt(review_item: Dict) -> str:
    """
    Generate prompt for LLM to fix a manual review item (Phase 2).

    Args:
        review_item: Dict from result["manual_review"]

    Returns:
        Prompt string for LLM
    """
    fixer = HboxFixer()
    review = ManualReview(
        file=review_item.get("file", ""),
        line=review_item.get("line", 0),
        issue_type=review_item.get("issue_type", "overfull"),
        content=review_item.get("content", ""),
        context=review_item.get("context", ""),
        suggestion=review_item.get("suggestion", ""),
        options=review_item.get("options", [])
    )
    return fixer.generate_llm_prompt(review)


def apply_llm_fix(
    content: str, line_num: int, fix_type: str, new_content: str, file_path: str = ""
) -> tuple:
    """
    Apply an LLM-suggested fix (Phase 2).

    Args:
        content: Full file content
        line_num: Line number to fix
        fix_type: Type of fix (reword, hyphenate, sloppy, abbreviate)
        new_content: The fixed line from LLM
        file_path: Optional file path for reporting

    Returns:
        Tuple of (fixed_content, fix_record)
    """
    fixer = HboxFixer()
    fixed, fix = fixer.apply_llm_fix(content, line_num, fix_type, new_content, file_path)
    return fixed, {"file": fix.file, "line": fix.line, "issue_type": fix.issue_type,
                   "fix_type": fix.fix_type, "before": fix.before, "after": fix.after}


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding='utf-8')

    # Demo: Phase 1 auto-fix + Phase 2 LLM items
    sample = r"""
\encell{sklearn.ensemble.RandomForestClassifier}
Text with \en{Very Long English Phrase That Causes Overfull Hbox Warning} here
"""
    issues = [
        {"line": 2, "type": "overfull", "severity": 15},
        {"line": 3, "type": "overfull", "severity": 20}
    ]

    fixed, result = fix_content(sample, "test.tex", issues)
    print("Phase 1 Result:", json.dumps(result, indent=2))

    # Phase 2: Generate LLM prompt for manual review items
    if result["manual_review"]:
        print("\n--- LLM Prompt for Manual Review ---")
        prompt = generate_llm_prompt(result["manual_review"][0])
        print(prompt)
