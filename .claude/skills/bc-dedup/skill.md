---
name: bc-dedup
description: Level 1 Stage Orchestrator - Chapter Deduplication & Balancing for zero redundancy
version: 1.0.0
author: BC Team
tags: [bc, orchestrator, level-1, dedup, deduplication, balancing]
parent: bc-super
has_python_tool: true
tools: [Read, Write, Edit, Grep, Glob, Bash, Task]
---

# BC Dedup - Chapter Deduplication & Balancing (Level 1)

## Agent Identity
- **Name:** BC Dedup Orchestrator
- **Role:** Stage orchestrator for chapter deduplication
- **Level:** 1 (Stage Orchestrator)
- **Parent:** bc-super

## Coordination

### Reports To
- bc-super (Level 0)

### Manages (Level 2 Workers)
- bc-dedup-detect (Duplicate detection)
- bc-dedup-fix (ChapterRef rewriting)

### Reads
- bc_dedup.json (configuration)
- chapters/*.tex (chapter files)

### Writes
- DEDUP-REPORT.md (deduplication report)
- chapters/*.tex (fixed files)

## Mission Statement

Ensure **Zero Redundancy** and **Balanced Information Distribution** across all book chapters by:
1. Detecting semantic duplicates using backward scan algorithm
2. Replacing duplicates with `\chapterref{}` references
3. Balancing chapter sizes for optimal distribution

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    BC DEDUP ORCHESTRATOR (Level 1)               │
│  - Backward scan algorithm: Chapter N → Chapter 2                │
│  - Parallel chunk comparison                                     │
│  - LLM for semantic analysis (token-efficient)                   │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
┌──────────────────────────┐     ┌──────────────────────────┐
│     bc-dedup-detect      │     │      bc-dedup-fix        │
│       (Level 2)          │────▶│       (Level 2)          │
│  - Chunk comparison      │     │  - ChapterRef rewriting  │
│  - Semantic similarity   │     │  - Natural language flow │
└──────────────────────────┘     └──────────────────────────┘
```

## Algorithm: Backward Scan

```
For chapter N down to 2:
    For each chunk in chapter N:
        Compare with all chunks in chapters 1..N-1 (parallel)
        If semantic_similarity > threshold:
            Mark as duplicate
            Generate \chapterref{} fix

After scan:
    Check chapter balance (size ratios)
    Report imbalanced chapters
```

## Workflow

### Phase 1: Discovery
1. Load configuration from bc_dedup.json
2. Discover chapter files using configured pattern
3. Validate project structure

### Phase 2: Detection (Parallel)
1. Invoke bc-dedup-detect for each chapter pair
2. Collect all duplicates found
3. Generate DedupIssue objects

### Phase 3: Fixing
1. Group issues by file
2. Invoke bc-dedup-fix for rewriting
3. Apply fixes with natural language flow

### Phase 4: Reporting
1. Generate DEDUP-REPORT.md
2. Report balance warnings
3. Emit `Dedup_Complete` signal

## Python Tool Integration

```python
from bc_engine.dedup import DedupOrchestrator

# Run full deduplication
orchestrator = DedupOrchestrator(
    project_path="/path/to/book",
    config_path="config/bc_dedup.json",
    llm_callback=my_llm_function,  # Optional
)

result = orchestrator.run(apply_fixes=True)
print(f"Found {result.duplicates_found} duplicates")
print(f"Applied {result.fixes_applied} fixes")
```

## Input/Output Format

### Input
```json
{
  "project_path": "/path/to/book/project",
  "config_path": "config/bc_dedup.json",
  "apply_fixes": true,
  "llm_enabled": true
}
```

### Output
```json
{
  "chapters_scanned": 12,
  "duplicates_found": 8,
  "fixes_applied": 8,
  "balance_warnings": ["Chapter 5 is 2.3x larger than average"],
  "issues": [...]
}
```

## QA Integration

### Validators Used
| Phase | Validators | Purpose |
|-------|------------|---------|
| Pre-fix | BCBiDiValidator | Ensure references maintain RTL |
| Post-fix | BCBiDiValidator | Verify fixed content |

### CLS Requirements
- Requires CLS with `\chapterref{}` macro defined
- Reference format: `\chapterref{chapterN}`

## Configuration (bc_dedup.json)

```json
{
  "chunk_size": 50,
  "similarity_threshold": 0.75,
  "max_workers": 4,
  "chapter_pattern": "chapters/chapter*.tex",
  "balance_threshold": 2.0
}
```

## Signals

| Signal | Trigger | Description |
|--------|---------|-------------|
| `Dedup_Detection_Start` | Phase 2 start | Detection phase begins |
| `Dedup_Detection_Complete` | Phase 2 end | All duplicates found |
| `Dedup_Fix_Complete` | Phase 3 end | All fixes applied |
| `Dedup_Complete` | End | Full run completed |

## Version History
- **v1.0.0** (2025-12-24): Initial implementation
  - Backward scan algorithm
  - Parallel chunk comparison
  - ChapterRef rewriting
  - Balance checking

---

**Parent:** bc-super
**Children:** bc-dedup-detect, bc-dedup-fix
**Configuration:** bc_dedup.json
