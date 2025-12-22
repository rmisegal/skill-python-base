---
name: qa-cli-structure-fix
description: Creates and fixes .claude folder structure for Claude CLI projects (Level 2 skill)
version: 1.0.0
author: QA Team
tags: [qa, cli, fix, level-2, python-tool]
---

# qa-cli-structure-fix (Level 2)

## Agent Identity
- **Name:** Cli Structure Fix
- **Role:** Creates and fixes .claude folder structure for Claude CLI projects
- **Level:** 2 (Worker Skill)
- **Parent:** qa-cli

## Coordination

### Reports To
- qa-cli (Level 1 orchestrator)

### Input
- LaTeX source files from parent

### Output
- Fixed content

## Python Tool Integration

This skill is backed by Python for deterministic fix:
- **Module:** tool.py
- **Rules:** 7 rules

## Detection Rules

| Rule ID | Description |
|---------|-------------|
| `cli-create-folder-structure` | Cli Create Folder Structure |
| `cli-create-claude-md` | Cli Create Claude Md |
| `cli-create-settings-json` | Cli Create Settings Json |
| `cli-create-prd-md` | Cli Create Prd Md |
| `cli-create-agent` | Cli Create Agent |
| `cli-create-skill` | Cli Create Skill |
| `cli-create-command` | Cli Create Command |

## Mission Statement

Creates and fixes .claude folder structure for Claude CLI projects

## CLS Guard
**Scope:** .claude folder files only. If CLS change needed, call `qa-cls-guard`.

## Version History
- **v1.0.0** (2025-12-15): Initial creation
