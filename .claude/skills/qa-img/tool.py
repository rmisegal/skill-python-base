"""Python tool for qa-img skill (Level 1 Family Orchestrator)."""
from pathlib import Path
from typing import Dict, List, Optional
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from qa_engine.infrastructure.image_orchestrator import ImageOrchestrator


def run_pipeline(content: str, file_path: str = "", project_root: str = None,
                 apply_fixes: bool = True, create_missing: bool = True,
                 validate: bool = True) -> dict:
    """
    Run full Image QA pipeline (detect + fix + validate).

    Args:
        content: LaTeX content to process
        file_path: Source file path for reporting
        project_root: Project root for file existence checks
        apply_fixes: Whether to apply fixes (default True)
        create_missing: Whether to create missing images (default True)
        validate: Whether to run validation (default True)

    Returns:
        Orchestration result dict matching skill.md format
    """
    root = Path(project_root) if project_root else None
    orchestrator = ImageOrchestrator(project_root=root)
    result = orchestrator.run(content, file_path, apply_fixes, create_missing, validate)
    return orchestrator.to_dict(result)


def detect_only(content: str, file_path: str = "", project_root: str = None) -> dict:
    """
    Run detection phase only (no fixes).

    Args:
        content: LaTeX content to analyze
        file_path: Source file path for reporting
        project_root: Project root for file existence checks

    Returns:
        Detection result dict
    """
    root = Path(project_root) if project_root else None
    orchestrator = ImageOrchestrator(project_root=root)
    result = orchestrator.run(content, file_path, apply_fixes=False, create_missing=False, validate=False)
    return orchestrator.to_dict(result)


def get_fixed_content(content: str, file_path: str = "", project_root: str = None) -> str:
    """
    Run pipeline and return fixed content.

    Args:
        content: LaTeX content to fix
        file_path: Source file path
        project_root: Project root for file operations

    Returns:
        Fixed LaTeX content
    """
    root = Path(project_root) if project_root else None
    orchestrator = ImageOrchestrator(project_root=root)
    result = orchestrator.run(content, file_path, apply_fixes=True, create_missing=False, validate=False)
    if result.fix_result:
        return result.fix_result.content
    return content


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding='utf-8')

    # Demo: Run pipeline on sample LaTeX with image references
    sample = r"""
\documentclass{article}
\begin{document}

\begin{figure}[htbp]
\centering
\includegraphics[width=0.8\textwidth]{images/architecture.png}
\caption{System Architecture}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics{missing_image.jpg}
\caption{Missing Image}
\end{figure}

\includegraphics{another/path/diagram.pdf}

\end{document}
"""

    result = run_pipeline(sample, "demo.tex", apply_fixes=True, create_missing=False, validate=True)
    print("Image QA Result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
