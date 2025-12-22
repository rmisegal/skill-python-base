---
name: qa-img-fix-missing
description: Creates missing image files for LaTeX documents (Level 2 skill)
version: 1.0.0
author: QA Team
tags: [qa, img, fix, missing, create, level-2, python-tool]
---

# qa-img-fix-missing (Level 2)

## Agent Identity
- **Name:** Missing Image Creator
- **Role:** Image file generation for missing references
- **Level:** 2 (Worker Skill)
- **Parent:** qa-img (Level 1)

## Coordination

### Reports To
- qa-img (Level 1 orchestrator)

### Input
- Issues list from qa-img-detect with `img-file-not-found` rule
- Project root path

### Output
- Creation report with files generated
- Updated LaTeX source (via ImageFixer)

## CLS Guard
**Scope:** .tex and image files only. If CLS change needed, call `qa-cls-guard`.

## Python Tool Integration

This skill is backed by Python for deterministic file creation:
- **Module:** `src/qa_engine/infrastructure/creation/image_creator.py`
- **Interface:** `CreatorInterface`
- **Dependency:** Pillow (PIL)

```python
from qa_engine.infrastructure.creation.image_creator import ImageCreator
from qa_engine.infrastructure.fixing.image_fixer import ImageFixer

# Create missing images
creator = ImageCreator(project_root=Path("."))
results = creator.create_from_issues(issues)

# Update LaTeX source to reference new images
fixer = ImageFixer()
fixed_content = fixer.fix(content, issues)
```

## Fix Process

### Phase 1: Create Missing Files (Python - ImageCreator)

| Step | Action | Python Method |
|------|--------|---------------|
| 1 | Identify missing files | `create_from_issues()` |
| 2 | Create directories | `Path.mkdir()` |
| 3 | Generate placeholder PNG | `_create_placeholder_image()` |
| 4 | Save to disk | `_save_image()` |

### Phase 2: Update LaTeX Source (Python - ImageFixer)

| Step | Action | Python Pattern |
|------|--------|----------------|
| 1 | Replace placeholder boxes | `replace-placeholder` |
| 2 | Add graphicspath | `add-graphicspath` |
| 3 | Fix path references | `fix_image_path()` |

## Image Specifications

| Property | Default | Configurable |
|----------|---------|:------------:|
| Width | 800 px | Yes |
| Height | 600 px | Yes |
| Format | PNG | Yes (.png, .jpg, .pdf) |
| Background | lightblue | Yes |
| Border | darkblue, 3px | Yes |
| Text | "Placeholder Image" | Yes |

## What Python CAN Do (100% Coverage)

- Create image directories
- Generate placeholder images (PIL)
- Save as PNG, JPG, or PDF
- Replace placeholder boxes in LaTeX
- Add graphicspath configuration
- Fix path references

## What Requires LLM (0% - None)

All operations are deterministic and handled by Python.

## Output Format

```json
{
  "skill": "qa-img-fix-missing",
  "status": "DONE",
  "files_created": [
    {"path": "images/figure1.png", "success": true},
    {"path": "images/figure2.png", "success": true}
  ],
  "source_updates": {
    "placeholders_replaced": 2,
    "graphicspath_added": true
  }
}
```

## Configuration

In `qa_setup.json`:
```json
{
  "img": {
    "fixers": ["qa-img-fix-paths", "qa-img-fix-missing"],
    "rules": {
      "img-file-not-found": {"enabled": true, "auto_fix": true}
    }
  }
}
```

## Version History
- **v1.0.0** (2025-12-15): Initial creation with Python backend

---

**Parent:** qa-img (Level 1)
**Coordination:** qa-orchestration/QA-CLAUDE.md
