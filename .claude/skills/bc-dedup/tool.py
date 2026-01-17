"""
BC Dedup Tool - Entry point for skill invocation.

Provides detect, fix, and run functions for Claude skill integration.
"""

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from bc_engine.dedup.orchestrator import DedupOrchestrator
from bc_engine.dedup.config import DedupConfig


def detect(
    project_path: str,
    config_path: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Detect duplicates across all chapters.

    Args:
        project_path: Root path of book project
        config_path: Path to bc_dedup.json

    Returns:
        List of issue dictionaries
    """
    orchestrator = DedupOrchestrator(
        project_path=project_path,
        config_path=config_path,
    )

    result = orchestrator.detect()

    return [issue.to_dict() for issue in result.issues]


def fix(
    project_path: str,
    config_path: Optional[str] = None,
    issues: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Apply fixes to detected duplicates.

    Args:
        project_path: Root path of book project
        config_path: Path to bc_dedup.json
        issues: Optional pre-detected issues

    Returns:
        Result dictionary with fix count
    """
    orchestrator = DedupOrchestrator(
        project_path=project_path,
        config_path=config_path,
    )

    if issues:
        # Convert dict issues back to DedupIssue objects
        from bc_engine.dedup.models import DedupIssue, DedupSeverity

        dedup_issues = [
            DedupIssue(
                rule=i["rule"],
                file=i["file"],
                line=i["line"],
                content=i["content"],
                severity=DedupSeverity(i["severity"]),
                source_chapter=i["source_chapter"],
                target_chapter=i["target_chapter"],
                fix=i.get("fix"),
            )
            for i in issues
        ]
        fixes_applied = orchestrator.fix(dedup_issues)
    else:
        result = orchestrator.run(apply_fixes=True)
        fixes_applied = result.fixes_applied

    return {"fixes_applied": fixes_applied}


def run(
    project_path: str,
    config_path: Optional[str] = None,
    apply_fixes: bool = False,
) -> Dict[str, Any]:
    """
    Run full deduplication pipeline.

    Args:
        project_path: Root path of book project
        config_path: Path to bc_dedup.json
        apply_fixes: Whether to apply fixes

    Returns:
        Full result dictionary
    """
    orchestrator = DedupOrchestrator(
        project_path=project_path,
        config_path=config_path,
    )

    result = orchestrator.run(apply_fixes=apply_fixes)

    return result.to_dict()


def get_config(config_path: str) -> Dict[str, Any]:
    """
    Get current configuration.

    Args:
        config_path: Path to bc_dedup.json

    Returns:
        Configuration dictionary
    """
    config = DedupConfig()
    config.load(config_path)

    return {
        "chunk_size": config.chunk_size,
        "similarity_threshold": config.similarity_threshold,
        "max_workers": config.max_workers,
        "chapter_pattern": config.chapter_pattern,
        "balance_threshold": config.balance_threshold,
    }
