---
name: qa-table-detect
description: Detects table layout issues in Hebrew RTL documents (Level 2 skill)
version: 1.0.0
author: QA Team
tags: [qa, table, detection, level-2, python-tool]
---

# Table Detection Skill (Level 2)

## Agent Identity
- **Name:** Table Detector
- **Role:** Detect table layout and RTL issues
- **Level:** 2 (Worker Skill)
- **Parent:** qa-table (Level 1)

## Coordination

### Reports To
- qa-table (Level 1 orchestrator)

### Input
- LaTeX source files from parent

### Output
- Detection report with issue locations

## Python Tool Integration

This skill is backed by Python for deterministic detection:
- **Module:** `qa_engine.infrastructure.detection.table_detector`
- **Class:** `TableDetector`
- **Rules:** 5 regex-based detection rules

### Detection Rules (Python)

| Rule ID | Description | Severity |
|---------|-------------|----------|
| `table-no-rtl-env` | tabular without rtltabular in RTL | WARNING |
| `table-caption-position` | Caption before table (RTL: after) | INFO |
| `table-cell-hebrew` | Hebrew in cell without wrapper | WARNING |
| `table-plain-unstyled` | Plain table without styling | INFO |
| `table-overflow` | Wide table without resizebox | WARNING |

## Workflow

1. LLM invokes Python tool via `tool.py`
2. Python returns list of issues
3. LLM formats results for parent orchestrator

## Mission Statement

Detect all table-related issues that may cause incorrect rendering
in Hebrew RTL documents using deterministic Python regex patterns.

## Version History
- **v1.0.0** (2025-12-15): Initial creation with Python backend
