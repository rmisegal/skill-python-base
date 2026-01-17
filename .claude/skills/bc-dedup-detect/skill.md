---
name: bc-dedup-detect
description: Level 2 Worker - Detects semantic duplicates across chapters
version: 1.0.0
author: BC Team
tags: [bc, worker, level-2, dedup, detection, python-tool]
parent: bc-dedup
has_python_tool: true
tools: [Read, Glob, Grep]
---

# BC Dedup Detect - Duplicate Detection (Level 2)

## Agent Identity
- **Name:** Dedup Detector
- **Role:** Detect semantic duplicates across chapters
- **Level:** 2 (Worker)
- **Parent:** bc-dedup

## Coordination

### Reports To
- bc-dedup (Level 1)

### Manages
- None (leaf worker)

## Mission Statement

Detect semantic duplicates using efficient chunking and parallel comparison. Minimize LLM token usage by using Python for structural analysis and only invoking LLM for semantic verification of candidate duplicates.

## Detection Rules

| Rule | Severity | Description |
|------|----------|-------------|
| `dedup-semantic-duplicate` | WARNING | Same information repeated in later chapter |
| `dedup-imbalanced-chapter` | INFO | Chapter significantly larger than average |
| `dedup-missing-reference` | WARNING | Should use chapterref to earlier content |

## Algorithm

```
1. Load and chunk all chapters (Python)
2. For each target chapter (N → 2):
   a. Create comparison tasks with earlier chapters
   b. Execute tasks in parallel (ThreadPoolExecutor)
   c. For each task:
      - Quick word-overlap check (Python)
      - If overlap > threshold: Send to LLM for semantic check
3. Collect all duplicates as DedupIssue objects
```

## Python Tool Integration

```python
from bc_engine.dedup.detector import DedupDetector

detector = DedupDetector(
    project_path="/path/to/book",
    config_path="config/bc_dedup.json",
)

# Detect across entire project
issues = detector.detect_project()

# Get supported rules
rules = detector.get_rules()
```

## Input/Output Format

### Input
```json
{
  "project_path": "/path/to/book",
  "config_path": "config/bc_dedup.json"
}
```

### Output
```json
{
  "issues": [
    {
      "rule": "dedup-semantic-duplicate",
      "file": "chapters/chapter5.tex",
      "line": 42,
      "content": "Neural networks process...",
      "severity": "WARNING",
      "source_chapter": 2,
      "target_chapter": 5,
      "fix": "\\chapterref{chapter2}"
    }
  ]
}
```

## Token Efficiency

This detector minimizes LLM usage by:
1. **Chunking**: Only comparing 50-line segments
2. **Pre-filtering**: Python word-overlap check first
3. **Batching**: Sending only candidate pairs to LLM
4. **Caching**: Reusing comparison results

## Version History
- **v1.0.0** (2025-12-24): Initial implementation

---

**Parent:** bc-dedup
**Interface:** DetectorInterface
