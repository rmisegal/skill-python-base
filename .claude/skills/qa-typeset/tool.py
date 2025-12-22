"""Python tool for qa-typeset skill (Level 1 Typeset Orchestrator)."""
from pathlib import Path
from typing import Dict, List, Optional
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from qa_engine.infrastructure.typeset_orchestrator import TypesetOrchestrator


def run_pipeline(log_content: str = "", tex_content: str = "", file_path: str = "",
                 project_root: str = None, apply_fixes: bool = True) -> dict:
    """
    Run full typeset QA pipeline.

    Args:
        log_content: LaTeX log file content
        tex_content: LaTeX source content
        file_path: Source file path
        project_root: Project root path
        apply_fixes: Whether to apply fixes (default True)

    Returns:
        Orchestration result dict matching skill.md format
    """
    root = Path(project_root) if project_root else None
    orchestrator = TypesetOrchestrator(project_root=root)
    result = orchestrator.run(log_content, tex_content, file_path, apply_fixes)
    return orchestrator.to_dict(result)


def run_from_files(log_path: str, tex_path: str, project_root: str = None,
                   apply_fixes: bool = True, preamble_path: str = None) -> dict:
    """
    Run QA from file paths.

    Args:
        log_path: Path to .log file
        tex_path: Path to .tex file
        project_root: Project root path
        apply_fixes: Whether to apply fixes
        preamble_path: Path to preamble.tex

    Returns:
        Orchestration result dict
    """
    root = Path(project_root) if project_root else None
    orchestrator = TypesetOrchestrator(project_root=root)
    result = orchestrator.run_from_files(
        Path(log_path), Path(tex_path), apply_fixes,
        Path(preamble_path) if preamble_path else None
    )
    return orchestrator.to_dict(result)


def detect_only(log_content: str, file_path: str = "") -> dict:
    """
    Run detection phase only (no fixes).

    Args:
        log_content: LaTeX log content
        file_path: Source file path

    Returns:
        Detection result dict
    """
    orchestrator = TypesetOrchestrator()
    result = orchestrator.run(log_content, "", file_path, apply_fixes=False)
    return orchestrator.to_dict(result)


def get_llm_prompts(log_content: str, tex_content: str, file_path: str = "") -> List[str]:
    """
    Get LLM prompts for manual review cases.

    Args:
        log_content: LaTeX log content
        tex_content: LaTeX source content
        file_path: Source file path

    Returns:
        List of LLM prompts for manual review
    """
    orchestrator = TypesetOrchestrator()
    result = orchestrator.run(log_content, tex_content, file_path, apply_fixes=True)
    return result.llm_prompts


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding='utf-8')

    # Demo: Run pipeline on sample log content
    sample_log = r"""
This is LuaTeX, Version 1.15.0 (TeX Live 2022)
(./chapters/ch01.tex
Overfull \hbox (15.5pt too wide) in paragraph at lines 42--45
 []|\T1/cmr/m/n/10 Long text that over-flows the mar-gin
Underfull \hbox (badness 10000) in paragraph at lines 50--52
Float too large for page by 25pt
Reference `fig:missing' on page 5 undefined
)
    """

    sample_tex = r"""
\documentclass{book}
\begin{document}
\chapter{Introduction}
This is a very long line that might cause an overfull hbox warning in the output.
\begin{figure}[htbp]
\includegraphics{large-image.png}
\end{figure}
\end{document}
    """

    result = run_pipeline(sample_log, sample_tex, "demo.tex")
    print("QA Typeset Result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
