---
name: qa-toc-config-detect
description: Detects TOC counter format configuration issues in CLS files for BiDi rendering (Level 2 skill)
version: 1.0.0
author: QA Team
tags: [qa, toc, detection, level-2, python-tool]
---

# qa-toc-config-detect (Level 2)

## Agent Identity
- **Name:** Toc Config Detect
- **Role:** Detects TOC counter format configuration issues in CLS files for BiDi rendering
- **Level:** 2 (Worker Skill)
- **Parent:** qa-toc

## Coordination

### Reports To
- qa-toc (Level 1 orchestrator)

### Input
- LaTeX source files from parent

### Output
- Detection report with issue locations

## Python Tool Integration

This skill is backed by Python for deterministic detection:
- **Module:** tool.py
- **Rules:** 6 rules

## Detection Rules

| Rule ID | Description |
|---------|-------------|
| `toc-missing-thechapter` | Toc Missing Thechapter |
| `toc-numberline-double-wrap` | Toc Numberline Double Wrap |
| `toc-thechapter-no-wrapper` | Toc Thechapter No Wrapper |
| `toc-thesection-no-wrapper` | Toc Thesection No Wrapper |
| `toc-thesubsection-no-wrapper` | Toc Thesubsection No Wrapper |
| `toc-inconsistent-wrappers` | Toc Inconsistent Wrappers |

## Mission Statement

Detects TOC counter format configuration issues in CLS files for BiDi rendering

## Version History
- **v1.0.0** (2025-12-15): Initial creation
