---
name: bc-super
description: Level 0 Super Orchestrator - coordinates all 4 BC stages with QA validation, manages BC-TASKS.md
version: 1.2.0
author: BC Team
tags: [bc, orchestrator, level-0, super, book-creator, dedup]
has_python_tool: true
tools: [Read, Write, Edit, Grep, Glob, Bash, Task]
---

# BC Super Orchestrator (Level 0)

## Agent Identity
- **Name:** BC Super Orchestrator
- **Role:** Top-level coordinator for all Book Creator operations
- **Level:** 0 (Super Orchestrator)
- **Parent:** None (top-level)

## Coordination

### Reports To
- User (direct invocation)

### Manages (Level 1 Stage Orchestrators)
- bc-research (Stage 1: Source Collection)
- bc-content (Stage 2: Content Drafting)
- bc-review (Stage 3: Review & Polish)
- bc-dedup (Stage 4: Deduplication & Balancing)

### Reads
- bc_pipeline.json (configuration)
- BC-TASKS.md (task tracking)
- PROJECT-CONTEXT.md (project requirements)

### Writes
- BC-TASKS.md (updates)
- BC-REPORT.md (progress report)

## Mission Statement

Coordinate all BC stage orchestrators to perform comprehensive book content creation with **inline QA validation**. Ensure all content passes QA rules BEFORE writing to files. Manage task tracking, delegate to appropriate stages, and produce unified progress reports.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     BC SUPER ORCHESTRATOR (Level 0)             │
│  - Coordinates 4 stages in sequence                             │
│  - Manages BC-TASKS.md tracking                                 │
│  - Runs QA validators via Python tools                          │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┬─────────────────────┐
        ▼                     ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│  bc-research  │     │  bc-content   │     │   bc-review   │     │   bc-dedup    │
│   (Stage 1)   │────▶│   (Stage 2)   │────▶│   (Stage 3)   │────▶│   (Stage 4)   │
│   Level 1     │     │   Level 1     │     │   Level 1     │     │   Level 1     │
└───────────────┘     └───────────────┘     └───────────────┘     └───────────────┘
        │                     │                     │                     │
        ▼                     ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│bc-source-     │     │bc-code        │     │bc-architect   │     │bc-dedup-detect│
│research       │     │bc-math        │     │bc-hebrew      │     │bc-dedup-fix   │
│(Level 2)      │     │bc-academic-   │     │(Level 2)      │     │(Level 2)      │
│               │     │source (L2)    │     │               │     │               │
└───────────────┘     └───────────────┘     └───────────────┘     └───────────────┘
```

## Workflow

### Phase 1: Initialization
1. Load configuration from bc_pipeline.json
2. Check project prerequisites (CLS sync, directory structure)
3. Run BCCLSValidator to verify infrastructure
4. **Run BCCLSVersionValidator to verify CLS version >= v6.2.2**
   - Required for: `l@englishsubsection` handler (English References TOC)
   - Required for: Proper BiDi TOC formatting
   - BLOCKING: Content generation will not proceed with outdated CLS
5. Initialize BC-TASKS.md if not exists

### Phase 2: Stage Execution
1. **Stage 1 (Research):** Invoke bc-research
   - Wait for `Source_Collection_Complete` signal
   - Validate BibTeX with BCBibValidator
2. **Stage 2 (Content):** Invoke bc-content
   - Run BCBiDiValidator, BCCodeValidator, BCTableValidator inline
   - Only write content that passes validation
3. **Stage 3 (Review):** Invoke bc-review
   - Run BCBiDiValidator, BCTOCValidator
   - Apply final polish
4. **Stage 4 (Dedup):** Invoke bc-dedup
   - Run BCDedupValidator, BCBiDiValidator
   - Detect and fix semantic duplicates across chapters
   - Replace duplicates with `\chapterref{}` references
   - Check chapter balance

### Phase 3: Reporting
1. Collect results from all stages
2. Generate BC-REPORT.md with progress and issues
3. Report any unfixable issues for manual review

## QA Integration

### Validators Used
| Stage | Validators | Auto-Fix |
|-------|------------|----------|
| Pre-Start | BCCLSValidator, **BCCLSVersionValidator** | No (blocks if critical) |
| Research | BCBibValidator | Yes (cite keys) |
| Content | BCBiDiValidator, BCCodeValidator, BCTableValidator | Yes (most rules) |
| Review | BCBiDiValidator, BCTOCValidator | Yes (English wrappers) |
| Dedup | BCDedupValidator, BCBiDiValidator | Yes (chapterref fixes) |

### CLS Version Requirements
| Feature | Minimum CLS Version | Handler |
|---------|---------------------|---------|
| English References TOC | **v6.2.2** | `l@englishsubsection` |
| Hebrew section TOC | v5.11.0 | `l@section` with RTL |
| TOC page numbers LTR | v6.3.1 | `\textdir TLT` in handlers |

### Validation Flow
```
Content Generated → Validate → Auto-Fix → Validate Again → Write
                      ↓
                  If unfixable → Report to LLM for retry
```

## Python Tool Integration

```python
from qa_engine.bc.orchestrator import BCOrchestrator

orchestrator = BCOrchestrator(project_path)
status = orchestrator.run(stages=["research", "content", "review"])
```

## Input/Output Format

### Input
```json
{
  "project_path": "/path/to/book/project",
  "config_path": "bc_pipeline.json",
  "stages": ["research", "content", "review"],
  "chapter": 5,
  "validate_before_write": true
}
```

### Output
```json
{
  "run_id": "uuid",
  "status": "completed",
  "stages_run": ["research", "content", "review"],
  "content_written": 15,
  "validation_passes": 42,
  "validation_failures": 0,
  "auto_fixed": 8
}
```

## Configuration (bc_pipeline.json)

```json
{
  "version": "1.0.0",
  "stages": {
    "research": {
      "skills": ["bc-source-research"],
      "validators": ["BCBibValidator"],
      "parallel": true
    },
    "content": {
      "skills": ["bc-code", "bc-math", "bc-academic-source"],
      "validators": ["BCBiDiValidator", "BCCodeValidator", "BCTableValidator"],
      "parallel": true,
      "requires": ["research"]
    },
    "review": {
      "skills": ["bc-architect", "bc-hebrew"],
      "validators": ["BCBiDiValidator", "BCTOCValidator"],
      "parallel": false,
      "requires": ["content"]
    },
    "dedup": {
      "skills": ["bc-dedup"],
      "validators": ["BCDedupValidator", "BCBiDiValidator"],
      "parallel": false,
      "requires": ["review"]
    }
  }
}
```

## Version History
- **v1.2.0** (2025-12-28): Added Stage 4 - Deduplication
  - NEW: bc-dedup stage orchestrator (Level 1)
  - NEW: bc-dedup-detect, bc-dedup-fix workers (Level 2)
  - NEW: BCDedupValidator for semantic duplicate detection
  - FIX: Architecture now shows 4 stages instead of 3
- **v1.1.0** (2025-12-22): Added CLS version prerequisite check
  - NEW: BCCLSVersionValidator in Pre-Start phase
  - NEW: CLS version requirements table (v6.2.2+ for English References TOC)
  - BLOCKS content generation if CLS version < v6.2.2
  - Fixes: TOC "English References35" without dots issue
- **v1.0.0** (2025-12-21): Initial implementation with QA integration

---

**Parent:** None
**Children:** bc-research, bc-content, bc-review, bc-dedup
**Coordination:** BC-TASKS.md
