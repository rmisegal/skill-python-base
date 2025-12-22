"""
Skill management CLI commands.

Commands: list, create, delete, enable, disable, duplicate, info, set-prompt
"""

from __future__ import annotations

import argparse
from pathlib import Path

from ..domain.models import SkillLevel, SkillType, DetectorSkill, FixerSkill
from ..management.skill_manager import SkillManager


class SkillCommands:
    """Skill management commands."""

    @staticmethod
    def register(subparsers: argparse._SubParsersAction) -> None:
        """Register skill subcommands."""
        skill_parser = subparsers.add_parser("skill", help="Skill management")
        skill_sub = skill_parser.add_subparsers(dest="subcommand")

        # list
        list_p = skill_sub.add_parser("list", help="List skills")
        list_p.add_argument("--family", help="Filter by family")
        list_p.add_argument("--level", type=int, choices=[0, 1, 2])
        list_p.add_argument("--type", dest="skill_type")
        list_p.set_defaults(func=SkillCommands.list_skills)

        # create
        create_p = skill_sub.add_parser("create", help="Create skill")
        create_p.add_argument("name", help="Skill name (e.g., qa-toc-detect)")
        create_p.add_argument("--family", required=True, help="Family name")
        create_p.add_argument(
            "--type", dest="skill_type", required=True,
            choices=["detection", "fix", "orchestrator", "validation"]
        )
        create_p.add_argument("--python", action="store_true", help="Has Python tool")
        create_p.set_defaults(func=SkillCommands.create_skill)

        # delete
        delete_p = skill_sub.add_parser("delete", help="Delete skill")
        delete_p.add_argument("name", help="Skill name")
        delete_p.set_defaults(func=SkillCommands.delete_skill)

        # enable/disable
        enable_p = skill_sub.add_parser("enable", help="Enable skill")
        enable_p.add_argument("name", help="Skill name")
        enable_p.set_defaults(func=SkillCommands.enable_skill)

        disable_p = skill_sub.add_parser("disable", help="Disable skill")
        disable_p.add_argument("name", help="Skill name")
        disable_p.set_defaults(func=SkillCommands.disable_skill)

        # duplicate
        dup_p = skill_sub.add_parser("duplicate", help="Duplicate skill")
        dup_p.add_argument("name", help="Source skill name")
        dup_p.add_argument("new_name", help="New skill name")
        dup_p.set_defaults(func=SkillCommands.duplicate_skill)

        # info
        info_p = skill_sub.add_parser("info", help="Show skill info")
        info_p.add_argument("name", help="Skill name")
        info_p.set_defaults(func=SkillCommands.show_info)

        # set-prompt
        prompt_p = skill_sub.add_parser("set-prompt", help="Set system prompt")
        prompt_p.add_argument("name", help="Skill name")
        prompt_p.add_argument("--file", type=Path, required=True)
        prompt_p.set_defaults(func=SkillCommands.set_prompt)

    @staticmethod
    def list_skills(args: argparse.Namespace) -> int:
        """List skills with optional filters."""
        manager = SkillManager(args.skills_path)
        skills = manager.list_all()

        if args.family:
            skills = [s for s in skills if s.family == args.family]
        if args.level is not None:
            skills = [s for s in skills if s.level.value == args.level]
        if args.skill_type:
            skills = [s for s in skills if s.skill_type.value == args.skill_type]

        for skill in skills:
            status = "enabled" if skill.enabled else "disabled"
            print(f"{skill.id} [{skill.level.name}] [{skill.skill_type.value}] ({status})")
        return 0

    @staticmethod
    def create_skill(args: argparse.Namespace) -> int:
        """Create a new skill."""
        manager = SkillManager(args.skills_path)
        skill_type = SkillType(args.skill_type)

        if skill_type == SkillType.DETECTION:
            skill = DetectorSkill(
                id=args.name, name=args.name, description=f"Detection skill: {args.name}",
                family=args.family, has_python_tool=args.python,
            )
        elif skill_type == SkillType.FIX:
            skill = FixerSkill(
                id=args.name, name=args.name, description=f"Fixer skill: {args.name}",
                family=args.family, has_python_tool=args.python,
            )
        else:
            from ..domain.models import Skill
            skill = Skill(
                id=args.name, name=args.name, description=f"Skill: {args.name}",
                family=args.family, skill_type=skill_type,
            )

        manager.create(skill)
        print(f"Created skill: {args.name}")
        return 0

    @staticmethod
    def delete_skill(args: argparse.Namespace) -> int:
        """Delete a skill."""
        manager = SkillManager(args.skills_path)
        if manager.delete(args.name):
            print(f"Deleted skill: {args.name}")
            return 0
        print(f"Skill not found: {args.name}")
        return 1

    @staticmethod
    def enable_skill(args: argparse.Namespace) -> int:
        """Enable a skill."""
        manager = SkillManager(args.skills_path)
        manager.enable(args.name)
        print(f"Enabled: {args.name}")
        return 0

    @staticmethod
    def disable_skill(args: argparse.Namespace) -> int:
        """Disable a skill."""
        manager = SkillManager(args.skills_path)
        manager.disable(args.name)
        print(f"Disabled: {args.name}")
        return 0

    @staticmethod
    def duplicate_skill(args: argparse.Namespace) -> int:
        """Duplicate a skill."""
        manager = SkillManager(args.skills_path)
        manager.duplicate(args.name, args.new_name)
        print(f"Duplicated {args.name} -> {args.new_name}")
        return 0

    @staticmethod
    def show_info(args: argparse.Namespace) -> int:
        """Show skill information."""
        manager = SkillManager(args.skills_path)
        skill = manager.read(args.name)
        if not skill:
            print(f"Skill not found: {args.name}")
            return 1

        print(f"ID: {skill.id}")
        print(f"Name: {skill.name}")
        print(f"Description: {skill.description}")
        print(f"Level: {skill.level.name}")
        print(f"Type: {skill.skill_type.value}")
        print(f"Family: {skill.family}")
        print(f"Enabled: {skill.enabled}")
        print(f"Tools: {', '.join(skill.tools) or 'none'}")
        print(f"Resources: {', '.join(skill.resources) or 'none'}")
        return 0

    @staticmethod
    def set_prompt(args: argparse.Namespace) -> int:
        """Set skill system prompt from file."""
        manager = SkillManager(args.skills_path)
        prompt = args.file.read_text(encoding="utf-8")
        manager.set_system_prompt(args.name, prompt)
        print(f"Updated prompt for: {args.name}")
        return 0
