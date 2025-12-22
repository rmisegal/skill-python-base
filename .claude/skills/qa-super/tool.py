"""Python tool for qa-super skill (Level 0 Super Orchestrator)."""
from pathlib import Path
from typing import Dict, List, Optional
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from qa_engine.infrastructure.super_orchestrator import SuperOrchestrator


def run_pipeline(content: str = "", file_path: str = "", project_root: str = None,
                 families: List[str] = None, apply_fixes: bool = True) -> dict:
    """
    Run full QA pipeline across all families.

    Args:
        content: LaTeX content to process (for single file)
        file_path: Source file path for reporting
        project_root: Project root path
        families: List of families to run (default: all enabled)
        apply_fixes: Whether to apply fixes (default True)

    Returns:
        Orchestration result dict matching skill.md format
    """
    root = Path(project_root) if project_root else None
    orchestrator = SuperOrchestrator(project_path=root)
    result = orchestrator.run(content, file_path, families, apply_fixes)
    return orchestrator.to_dict(result)


def run_on_project(project_root: str, families: List[str] = None, apply_fixes: bool = True) -> dict:
    """
    Run QA on all .tex files in project.

    Args:
        project_root: Project root path
        families: List of families to run (default: all enabled)
        apply_fixes: Whether to apply fixes (default True)

    Returns:
        Orchestration result dict
    """
    root = Path(project_root)
    orchestrator = SuperOrchestrator(project_path=root)
    result = orchestrator.run_on_project(families, apply_fixes)
    return orchestrator.to_dict(result)


def detect_only(content: str, file_path: str = "", families: List[str] = None) -> dict:
    """
    Run detection phase only (no fixes).

    Args:
        content: LaTeX content to analyze
        file_path: Source file path for reporting
        families: List of families to run

    Returns:
        Detection result dict
    """
    orchestrator = SuperOrchestrator()
    result = orchestrator.run(content, file_path, families, apply_fixes=False)
    return orchestrator.to_dict(result)


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding='utf-8')

    # Demo: Run pipeline on sample Hebrew-English content
    sample = r"""
\documentclass{article}
\begin{document}

\section{מבוא ל-Machine Learning}

המודל נקרא CNN והוא מבוסס על 128 layers.

בשנת 2024 פותחו מודלים עם דיוק של 95%.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.8\textwidth]{images/architecture.png}
\caption{System Architecture}
\end{figure}

\begin{tikzpicture}
    \draw[->] (0,0) -- (5,0);
\end{tikzpicture}

$P(\text{אירוע}) = 0.5$

\end{document}
"""

    result = run_pipeline(sample, "demo.tex", families=["BiDi", "img"])
    print("QA Super Result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
