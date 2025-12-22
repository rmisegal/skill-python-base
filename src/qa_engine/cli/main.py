"""
Main entry point for qa-manage CLI.

Usage: qa-manage <command> <subcommand> [options]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .skill_commands import SkillCommands
from .tool_commands import ToolCommands
from .resource_commands import ResourceCommands
from .pipeline_commands import PipelineCommands


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser."""
    parser = argparse.ArgumentParser(
        prog="qa-manage",
        description="QA Engine management CLI",
    )
    parser.add_argument(
        "--skills-path",
        type=Path,
        default=Path(".claude/skills"),
        help="Path to skills directory",
    )
    parser.add_argument(
        "--config-path",
        type=Path,
        default=Path("config/qa_setup.json"),
        help="Path to pipeline config",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Register command groups
    SkillCommands.register(subparsers)
    ToolCommands.register(subparsers)
    ResourceCommands.register(subparsers)
    PipelineCommands.register(subparsers)

    return parser


def main(args: list[str] | None = None) -> int:
    """Main entry point."""
    parser = create_parser()
    parsed = parser.parse_args(args)

    if not parsed.command:
        parser.print_help()
        return 1

    if hasattr(parsed, "func"):
        try:
            return parsed.func(parsed)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
