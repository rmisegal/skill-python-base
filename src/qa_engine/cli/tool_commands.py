"""
Tool management CLI commands.

Commands: list, add, remove, generate
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ..domain.models import RuleDefinition, PatternDefinition
from ..domain.models.definitions import Severity
from ..management.tool_manager import ToolManager
from ..management.skill_manager import SkillManager


class ToolCommands:
    """Tool management commands."""

    @staticmethod
    def register(subparsers: argparse._SubParsersAction) -> None:
        """Register tool subcommands."""
        tool_parser = subparsers.add_parser("tool", help="Tool management")
        tool_sub = tool_parser.add_subparsers(dest="subcommand")

        # list
        list_p = tool_sub.add_parser("list", help="List tools")
        list_p.add_argument("--skill", help="Filter by skill")
        list_p.set_defaults(func=ToolCommands.list_tools)

        # add
        add_p = tool_sub.add_parser("add", help="Add tool to skill")
        add_p.add_argument("skill_name", help="Skill name")
        add_p.add_argument("tool_name", help="Tool name")
        add_p.set_defaults(func=ToolCommands.add_tool)

        # remove
        remove_p = tool_sub.add_parser("remove", help="Remove tool from skill")
        remove_p.add_argument("skill_name", help="Skill name")
        remove_p.add_argument("tool_name", help="Tool name")
        remove_p.set_defaults(func=ToolCommands.remove_tool)

        # generate
        gen_p = tool_sub.add_parser("generate", help="Generate new tool")
        gen_p.add_argument("name", help="Tool name")
        gen_p.add_argument(
            "--type", dest="tool_type", required=True,
            choices=["detector", "fixer"]
        )
        gen_p.add_argument("--rules", type=Path, help="Rules JSON file")
        gen_p.add_argument("--patterns", type=Path, help="Patterns JSON file")
        gen_p.set_defaults(func=ToolCommands.generate_tool)

        # info
        info_p = tool_sub.add_parser("info", help="Show tool info")
        info_p.add_argument("name", help="Tool name")
        info_p.set_defaults(func=ToolCommands.show_info)

    @staticmethod
    def list_tools(args: argparse.Namespace) -> int:
        """List all tools."""
        tool_manager = ToolManager(args.skills_path)
        tools = tool_manager.list_all()

        if args.skill:
            skill_manager = SkillManager(args.skills_path)
            skill = skill_manager.read(args.skill)
            if skill:
                tools = [t for t in tools if t.id in skill.tools]

        for tool in tools:
            status = "enabled" if tool.enabled else "disabled"
            print(f"{tool.id} [{tool.tool_type.value}] ({status})")
        return 0

    @staticmethod
    def add_tool(args: argparse.Namespace) -> int:
        """Add a tool to a skill."""
        skill_manager = SkillManager(args.skills_path)
        skill_manager.add_tool(args.skill_name, args.tool_name)
        print(f"Added {args.tool_name} to {args.skill_name}")
        return 0

    @staticmethod
    def remove_tool(args: argparse.Namespace) -> int:
        """Remove a tool from a skill."""
        skill_manager = SkillManager(args.skills_path)
        skill_manager.remove_tool(args.skill_name, args.tool_name)
        print(f"Removed {args.tool_name} from {args.skill_name}")
        return 0

    @staticmethod
    def generate_tool(args: argparse.Namespace) -> int:
        """Generate a new tool."""
        tool_manager = ToolManager(args.skills_path)

        if args.tool_type == "detector":
            rules = {}
            if args.rules and args.rules.exists():
                rules_data = json.loads(args.rules.read_text())
                for rule_id, rule_data in rules_data.items():
                    rules[rule_id] = RuleDefinition(
                        id=rule_id,
                        description=rule_data.get("description", ""),
                        pattern=rule_data["pattern"],
                        severity=Severity(rule_data.get("severity", "warning")),
                    )
            tool = tool_manager.generate_detector(
                name=args.name,
                description=f"Detector tool: {args.name}",
                rules=rules,
            )
        else:
            patterns = {}
            if args.patterns and args.patterns.exists():
                patterns_data = json.loads(args.patterns.read_text())
                for pat_id, pat_data in patterns_data.items():
                    patterns[pat_id] = PatternDefinition(
                        id=pat_id,
                        description=pat_data.get("description", ""),
                        find=pat_data["find"],
                        replace=pat_data["replace"],
                    )
            tool = tool_manager.generate_fixer(
                name=args.name,
                description=f"Fixer tool: {args.name}",
                patterns=patterns,
            )

        print(f"Generated tool: {tool.id}")
        return 0

    @staticmethod
    def show_info(args: argparse.Namespace) -> int:
        """Show tool information."""
        tool_manager = ToolManager(args.skills_path)
        tool = tool_manager.read(args.name)
        if not tool:
            print(f"Tool not found: {args.name}")
            return 1

        print(f"ID: {tool.id}")
        print(f"Name: {tool.name}")
        print(f"Type: {tool.tool_type.value}")
        print(f"Module: {tool.module_path}")
        print(f"Entry: {tool.entry_function}")
        print(f"Enabled: {tool.enabled}")
        return 0
