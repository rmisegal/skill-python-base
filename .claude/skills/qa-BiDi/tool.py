"""Python tool for qa-BiDi skill (Level 1 Family Orchestrator)."""
from pathlib import Path
from typing import Dict, List, Optional
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from qa_engine.infrastructure.bidi_orchestrator import BiDiOrchestrator


def run_pipeline(content: str, file_path: str = "", apply_fixes: bool = True) -> dict:
    """
    Run full BiDi QA pipeline (detect + fix).

    Args:
        content: LaTeX content to process
        file_path: Source file path for reporting
        apply_fixes: Whether to apply fixes (default True)

    Returns:
        Orchestration result dict matching skill.md format
    """
    orchestrator = BiDiOrchestrator()
    result = orchestrator.run(content, file_path, apply_fixes)
    return orchestrator.to_dict(result)


def detect_only(content: str, file_path: str = "") -> dict:
    """
    Run detection phase only (no fixes).

    Args:
        content: LaTeX content to analyze
        file_path: Source file path for reporting

    Returns:
        Detection result dict
    """
    orchestrator = BiDiOrchestrator()
    result = orchestrator.run(content, file_path, apply_fixes=False)
    return orchestrator.to_dict(result)


def get_fixed_content(content: str, file_path: str = "") -> str:
    """
    Run pipeline and return fixed content.

    Args:
        content: LaTeX content to fix
        file_path: Source file path

    Returns:
        Fixed LaTeX content
    """
    orchestrator = BiDiOrchestrator()
    result = orchestrator.run(content, file_path, apply_fixes=True)
    if result.fix_result:
        return result.fix_result.content
    return content


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding='utf-8')

    # Demo: Run pipeline on sample Hebrew-English content
    sample = r"""
\section{מבוא ל-Machine Learning}

המודל הראשון נקרא CNN והוא מבוסס על 128 layers.

בשנת 2024 פותחו מודלים חדשים עם דיוק של 95%.

\begin{tikzpicture}
    \draw[->] (0,0) -- (5,0);
\end{tikzpicture}

$P(\text{אירוע}) = 0.5$
"""

    result = run_pipeline(sample, "demo.tex")
    print("BiDi QA Result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
