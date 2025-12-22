# When to Use This Project

## Overview

This project provides Python-powered QA and BC skills for Hebrew-English LaTeX documents. Understanding when you need this project vs. using skills globally is important.

## When You NEED This Project

### 1. Developing or Modifying Skills

If you're creating new skills or modifying existing ones:
```
skill-python-base/
├── .claude/skills/qa-my-new-skill/  # Create new skill here
└── src/qa_engine/                    # Implement Python tools here
```

### 2. Running Python-Based Detection/Fixing

The Python tools provide deterministic, fast processing:
- BiDi detection (numbers, English, acronyms)
- Code block formatting
- Image path validation
- Bibliography checking
- Typeset warning analysis

### 3. Using the Full QA Pipeline

For comprehensive document QA:
```bash
cd /path/to/skill-python-base
.\.venv\Scripts\activate
claude
/qa-super "Run full QA on my book project"
```

### 4. Book Content Generation with QA Validation

BC skills validate against QA rules before writing:
```bash
/bc-super "Generate chapter on machine learning"
```

### 5. Development and Testing

The project includes comprehensive tests:
```bash
pytest tests/ -v
pytest tests/unit/ -v  # Unit tests only
pytest tests/comparison/ -v  # LLM vs Python comparison
```

## When You DON'T Need This Project

### 1. Using Individual Skills Globally

If skills are already migrated to `~/.claude/skills/` and qa_engine is installed globally:
```bash
# From any directory
claude
/qa-BiDi-detect "Check my document for BiDi issues"
```

### 2. Simple LLM-Only Skills

Skills without Python tools don't need this project:
```
~/.claude/skills/my-simple-skill/
└── skill.md  # LLM-only skill
```

### 3. Using Pre-Built Reports

If someone else ran QA and shared reports, you just need the output files.

## Migration Guide

### From Local to Global Skills

1. **Copy skill directories:**
```powershell
Copy-Item ".\.claude\skills\qa-*" "$env:USERPROFILE\.claude\skills\" -Recurse
Copy-Item ".\.claude\skills\bc-*" "$env:USERPROFILE\.claude\skills\" -Recurse
```

2. **Install qa_engine globally:**
```powershell
pip install -e C:\path\to\skill-python-base
```

3. **Update tool.py paths (if needed):**
```python
# From relative:
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

# To absolute or package import:
from qa_engine.infrastructure.detection import BiDiDetector
```

### Keeping Skills Synced

If you modify skills locally, sync to global:
```powershell
# Sync specific skill
Copy-Item ".\.claude\skills\qa-BiDi-detect\*" "$env:USERPROFILE\.claude\skills\qa-BiDi-detect\" -Force
```

## Decision Flowchart

```
┌─────────────────────────────────────┐
│ Do you need Python-based QA tools?  │
└─────────────────┬───────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
       YES                  NO
        │                   │
        ▼                   ▼
┌───────────────────┐ ┌───────────────────────────┐
│ Is qa_engine      │ │ Use LLM-only skills       │
│ installed globally?│ │ No project needed         │
└─────────┬─────────┘ └───────────────────────────┘
          │
    ┌─────┴─────┐
    │           │
   YES          NO
    │           │
    ▼           ▼
┌─────────────┐ ┌─────────────────────────────────┐
│ Use skills  │ │ Either:                         │
│ from any    │ │ 1. Install: pip install -e ...  │
│ directory   │ │ 2. Work within project directory│
└─────────────┘ └─────────────────────────────────┘
```

## Summary

| Scenario | Need Project? | Setup Required |
|----------|---------------|----------------|
| Develop new skills | Yes | Clone project |
| Modify Python tools | Yes | Clone project |
| Run full QA pipeline | Yes* | Activate venv |
| Use individual QA skills | No* | Install package globally |
| Generate BC content | Yes* | Activate venv |
| Use LLM-only skills | No | Just copy skill.md |

*Can work without project if qa_engine is installed globally
