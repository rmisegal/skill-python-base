"""
Pipeline management CLI commands.

Commands: show, insert, remove, move, enable, disable, run
"""

from __future__ import annotations

import argparse
from pathlib import Path

from ..management.pipeline_manager import PipelineManager
from ..management.skill_manager import SkillManager


class PipelineCommands:
    """Pipeline management commands."""

    @staticmethod
    def register(subparsers: argparse._SubParsersAction) -> None:
        """Register pipeline subcommands."""
        pipe_parser = subparsers.add_parser("pipeline", help="Pipeline management")
        pipe_sub = pipe_parser.add_subparsers(dest="subcommand")

        # show
        show_p = pipe_sub.add_parser("show", help="Show pipeline")
        show_p.set_defaults(func=PipelineCommands.show_pipeline)

        # insert
        insert_p = pipe_sub.add_parser("insert", help="Insert skill into pipeline")
        insert_p.add_argument("skill_name", help="Skill name")
        insert_p.add_argument("--position", type=int, help="Insert position")
        insert_p.set_defaults(func=PipelineCommands.insert_skill)

        # remove
        remove_p = pipe_sub.add_parser("remove", help="Remove skill from pipeline")
        remove_p.add_argument("skill_name", help="Skill name")
        remove_p.set_defaults(func=PipelineCommands.remove_skill)

        # move
        move_p = pipe_sub.add_parser("move", help="Move skill in pipeline")
        move_p.add_argument("skill_name", help="Skill name")
        move_p.add_argument("--position", type=int, required=True)
        move_p.set_defaults(func=PipelineCommands.move_skill)

        # enable
        enable_p = pipe_sub.add_parser("enable", help="Enable pipeline stage")
        enable_p.add_argument("skill_name", help="Skill name")
        enable_p.set_defaults(func=PipelineCommands.enable_stage)

        # disable
        disable_p = pipe_sub.add_parser("disable", help="Disable pipeline stage")
        disable_p.add_argument("skill_name", help="Skill name")
        disable_p.set_defaults(func=PipelineCommands.disable_stage)

        # parallel
        parallel_p = pipe_sub.add_parser("parallel", help="Set parallel execution")
        parallel_p.add_argument("skill_names", nargs="+", help="Skills to run in parallel")
        parallel_p.set_defaults(func=PipelineCommands.set_parallel)

        # save
        save_p = pipe_sub.add_parser("save", help="Save pipeline config")
        save_p.set_defaults(func=PipelineCommands.save_pipeline)

    @staticmethod
    def _get_manager(args: argparse.Namespace) -> PipelineManager:
        """Get pipeline manager instance."""
        skill_manager = SkillManager(args.skills_path)
        manager = PipelineManager(args.config_path, skill_manager)
        manager.load_pipeline()
        return manager

    @staticmethod
    def show_pipeline(args: argparse.Namespace) -> int:
        """Show current pipeline configuration."""
        manager = PipelineCommands._get_manager(args)
        stages = manager.get_ordered_stages()

        if not stages:
            print("Pipeline is empty")
            return 0

        print("Pipeline stages:")
        for stage in stages:
            status = "enabled" if stage.enabled else "disabled"
            parallel = f" (parallel: {', '.join(stage.parallel_with)})" if stage.parallel_with else ""
            print(f"  {stage.order}. {stage.skill_id} [{status}]{parallel}")
        return 0

    @staticmethod
    def insert_skill(args: argparse.Namespace) -> int:
        """Insert skill into pipeline."""
        manager = PipelineCommands._get_manager(args)
        manager.insert_skill(args.skill_name, args.position)
        manager.save_pipeline()
        print(f"Inserted {args.skill_name} into pipeline")
        return 0

    @staticmethod
    def remove_skill(args: argparse.Namespace) -> int:
        """Remove skill from pipeline."""
        manager = PipelineCommands._get_manager(args)
        if manager.remove_skill(args.skill_name):
            manager.save_pipeline()
            print(f"Removed {args.skill_name} from pipeline")
            return 0
        print(f"Skill not in pipeline: {args.skill_name}")
        return 1

    @staticmethod
    def move_skill(args: argparse.Namespace) -> int:
        """Move skill to new position."""
        manager = PipelineCommands._get_manager(args)
        manager.move_skill(args.skill_name, args.position)
        manager.save_pipeline()
        print(f"Moved {args.skill_name} to position {args.position}")
        return 0

    @staticmethod
    def enable_stage(args: argparse.Namespace) -> int:
        """Enable pipeline stage."""
        manager = PipelineCommands._get_manager(args)
        if manager.enable_stage(args.skill_name):
            manager.save_pipeline()
            print(f"Enabled stage: {args.skill_name}")
            return 0
        print(f"Stage not found: {args.skill_name}")
        return 1

    @staticmethod
    def disable_stage(args: argparse.Namespace) -> int:
        """Disable pipeline stage."""
        manager = PipelineCommands._get_manager(args)
        if manager.disable_stage(args.skill_name):
            manager.save_pipeline()
            print(f"Disabled stage: {args.skill_name}")
            return 0
        print(f"Stage not found: {args.skill_name}")
        return 1

    @staticmethod
    def set_parallel(args: argparse.Namespace) -> int:
        """Set skills to run in parallel."""
        manager = PipelineCommands._get_manager(args)
        manager.set_parallel(args.skill_names)
        manager.save_pipeline()
        print(f"Set parallel: {', '.join(args.skill_names)}")
        return 0

    @staticmethod
    def save_pipeline(args: argparse.Namespace) -> int:
        """Save pipeline configuration."""
        manager = PipelineCommands._get_manager(args)
        manager.save_pipeline()
        print(f"Pipeline saved to: {args.config_path}")
        return 0
