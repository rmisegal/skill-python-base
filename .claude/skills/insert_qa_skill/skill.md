---
name: insert_qa_skill
description: Creates and integrates new QA skills with optional Python tool generation (Level 0 meta-skill)
version: 1.0.0
author: QA Team
tags: [qa, meta-skill, skill-creation, python-tool, integration, level-0]
---

# insert_qa_skill - QA Skill Creation Meta-Skill

## Agent Identity
- **Name:** Insert QA Skill
- **Role:** Automate creation and integration of new QA skills
- **Level:** 0 (Meta-Skill)
- **Parent:** None (top-level utility)

## Coordination

### Reports To
- User (direct invocation)

### Manages
- Creates new Level 1 or Level 2 skills
- Generates Python tool implementations
- Updates parent orchestrators

## Operating Modes

### Mode 1: Create New Skill
```
invoke: insert_qa_skill --mode=create
arguments:
  --name: skill name (e.g., qa-new-detector)
  --family: parent family (e.g., BiDi, code, table)
  --level: skill level (1 or 2)
  --type: detection | fix | orchestrator
  --description: brief description
  --rules: comma-separated list of detection rules
  --python: true | false (generate Python tool)
```

### Mode 2: Split Existing Skill
```
invoke: insert_qa_skill --mode=split
arguments:
  --skill: existing skill name to split
  --extract: capabilities to extract to Python
```

## Python Tool Integration

This skill is backed by Python for file generation:
- **Module:** `skill_creator`
- **Functions:** `create_skill()`, `split_skill()`

## Workflow: Create New Skill

1. Validate input parameters
2. Generate skill.md from template
3. Generate tool.py (if --python=true)
4. Update parent orchestrator
5. Run validation tests
6. Output integration report

## Mission Statement

Automate the process of creating new QA skills to ensure consistency,
proper integration, and reduce manual effort in skill development.

## Version History
- **v1.0.0** (2025-12-15): Initial creation
