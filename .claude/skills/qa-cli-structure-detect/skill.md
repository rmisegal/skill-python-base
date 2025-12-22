---
name: qa-cli-structure-detect
description: Detects missing or improper .claude folder structure (Level 2 skill)
version: 1.0.0
author: QA Team
tags: [qa, cli, detection, level-2, python-tool]
---

# qa-cli-structure-detect (Level 2)

## Agent Identity
- **Name:** Cli Structure Detect
- **Role:** Detects missing or improper .claude folder structure
- **Level:** 2 (Worker Skill)
- **Parent:** qa-cli

## Coordination

### Reports To
- qa-cli (Level 1 orchestrator)

### Input
- LaTeX source files from parent

### Output
- Detection report with issue locations

## Python Tool Integration

This skill is backed by Python for deterministic detection:
- **Module:** tool.py
- **Rules:** 8 rules

## Detection Rules

| Rule ID | Description |
|---------|-------------|
| `cli-missing-claude-folder` | Cli Missing Claude Folder |
| `cli-missing-agents-folder` | Cli Missing Agents Folder |
| `cli-missing-skills-folder` | Cli Missing Skills Folder |
| `cli-missing-commands-folder` | Cli Missing Commands Folder |
| `cli-missing-tasks-folder` | Cli Missing Tasks Folder |
| `cli-missing-claude-md` | Cli Missing Claude Md |
| `cli-missing-settings-json` | Cli Missing Settings Json |
| `cli-missing-prd-md` | Cli Missing Prd Md |

## Mission Statement

Detects missing or improper .claude folder structure

## Version History
- **v1.0.0** (2025-12-15): Initial creation
