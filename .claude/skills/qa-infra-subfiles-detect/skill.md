---
name: qa-infra-subfiles-detect
description: Detects chapter files missing subfiles preamble for standalone compilation (Level 2 skill)
version: 1.0.0
author: QA Team
tags: [qa, infra, subfiles, detection, level-2, python-tool]
---

# Subfiles Detection Skill (Level 2)

## Agent Identity
- **Name:** Subfiles Detector
- **Role:** Detect subfiles package issues
- **Level:** 2 (Worker Skill)
- **Parent:** qa-infra (Level 1)

## Coordination

### Reports To
- qa-infra (Level 1 orchestrator)

### Input
- LaTeX source files from parent

### Output
- Detection report with issue locations

## Python Tool Integration

This skill is backed by Python for deterministic detection:
- **Module:** `qa_engine.infrastructure.detection.subfiles_detector`
- **Class:** `SubfilesDetector`
- **Rules:** 3 regex-based detection rules

### Detection Rules (Python)

| Rule ID | Description | Severity |
|---------|-------------|----------|
| `subfiles-missing-class` | Chapter without subfiles class | WARNING |
| `subfiles-no-main-ref` | Subfiles without main reference | CRITICAL |
| `subfiles-no-preamble` | Missing standalone setup | INFO |

## Workflow

1. LLM invokes Python tool via `tool.py`
2. Python returns list of issues
3. LLM formats results for parent orchestrator

## Mission Statement

Detect all subfiles-related issues that may prevent standalone chapter
compilation using deterministic Python regex patterns.

## Version History
- **v1.0.0** (2025-12-15): Initial creation with Python backend
