"""
Resource management CLI commands.

Commands: list, create, update, info
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ..domain.models import Resource, ResourceType, FileFormat
from ..management.resource_manager import ResourceManager


class ResourceCommands:
    """Resource management commands."""

    @staticmethod
    def register(subparsers: argparse._SubParsersAction) -> None:
        """Register resource subcommands."""
        res_parser = subparsers.add_parser("resource", help="Resource management")
        res_sub = res_parser.add_subparsers(dest="subcommand")

        # list
        list_p = res_sub.add_parser("list", help="List resources")
        list_p.add_argument(
            "--type", dest="resource_type",
            choices=["config", "template", "rules", "patterns"]
        )
        list_p.set_defaults(func=ResourceCommands.list_resources)

        # create
        create_p = res_sub.add_parser("create", help="Create resource")
        create_p.add_argument("name", help="Resource name")
        create_p.add_argument(
            "--type", dest="resource_type", required=True,
            choices=["config", "template", "rules", "patterns"]
        )
        create_p.add_argument("--file", type=Path, help="Content file")
        create_p.add_argument(
            "--format", dest="file_format", default="json",
            choices=["json", "yaml"]
        )
        create_p.set_defaults(func=ResourceCommands.create_resource)

        # update
        update_p = res_sub.add_parser("update", help="Update resource")
        update_p.add_argument("name", help="Resource name")
        update_p.add_argument("--file", type=Path, required=True)
        update_p.set_defaults(func=ResourceCommands.update_resource)

        # info
        info_p = res_sub.add_parser("info", help="Show resource info")
        info_p.add_argument("name", help="Resource name")
        info_p.set_defaults(func=ResourceCommands.show_info)

        # validate
        val_p = res_sub.add_parser("validate", help="Validate resource")
        val_p.add_argument("name", help="Resource name")
        val_p.set_defaults(func=ResourceCommands.validate_resource)

    @staticmethod
    def list_resources(args: argparse.Namespace) -> int:
        """List all resources."""
        manager = ResourceManager(args.skills_path / "resources")
        resources = manager.list_all()

        if args.resource_type:
            res_type = ResourceType(args.resource_type)
            resources = [r for r in resources if r.resource_type == res_type]

        for res in resources:
            print(f"{res.id} [{res.resource_type.value}] [{res.file_format.value}]")
        return 0

    @staticmethod
    def create_resource(args: argparse.Namespace) -> int:
        """Create a new resource."""
        manager = ResourceManager(args.skills_path / "resources")

        content = {}
        if args.file and args.file.exists():
            content = json.loads(args.file.read_text())

        resource = Resource(
            id=args.name,
            name=args.name,
            description=f"Resource: {args.name}",
            resource_type=ResourceType(args.resource_type),
            file_format=FileFormat(args.file_format),
            content=content,
        )

        manager.create(resource)
        print(f"Created resource: {args.name}")
        return 0

    @staticmethod
    def update_resource(args: argparse.Namespace) -> int:
        """Update resource content."""
        manager = ResourceManager(args.skills_path / "resources")

        content = json.loads(args.file.read_text())
        manager.set_content(args.name, content)
        print(f"Updated resource: {args.name}")
        return 0

    @staticmethod
    def show_info(args: argparse.Namespace) -> int:
        """Show resource information."""
        manager = ResourceManager(args.skills_path / "resources")
        resource = manager.read(args.name)
        if not resource:
            print(f"Resource not found: {args.name}")
            return 1

        print(f"ID: {resource.id}")
        print(f"Name: {resource.name}")
        print(f"Type: {resource.resource_type.value}")
        print(f"Format: {resource.file_format.value}")
        print(f"Enabled: {resource.enabled}")
        return 0

    @staticmethod
    def validate_resource(args: argparse.Namespace) -> int:
        """Validate resource content."""
        manager = ResourceManager(args.skills_path / "resources")
        errors = manager.validate_content(args.name)

        if errors:
            print(f"Validation errors for {args.name}:")
            for error in errors:
                print(f"  - {error}")
            return 1

        print(f"Resource {args.name} is valid")
        return 0
