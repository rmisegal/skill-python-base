---
name: qa-bib-detect
description: Detects bibliography and citation issues in LaTeX documents (Level 2 skill)
version: 1.0.0
author: QA Team
tags: [qa, bib, bibliography, citation, detection, level-2, python-tool]
---

# Bibliography Detection Skill (Level 2)

## Agent Identity
- **Name:** Bibliography Detector
- **Role:** Detect citation and bibliography issues
- **Level:** 2 (Worker Skill)
- **Parent:** qa-bib (Level 1)

## Coordination

### Reports To
- qa-bib (Level 1 orchestrator)

### Input
- LaTeX source files from parent

### Output
- Detection report with issue locations

## Python Tool Integration

This skill is backed by Python for deterministic detection:
- **Module:** `qa_engine.infrastructure.detection.bib_detector`
- **Class:** `BibDetector`
- **Rules:** 5 regex-based detection rules

### Detection Rules (Python)

| Rule ID | Description | Severity |
|---------|-------------|----------|
| `bib-missing-file` | Bibliography file reference | CRITICAL |
| `bib-undefined-cite` | Citation may be undefined | WARNING |
| `bib-empty-cite` | Empty citation command | CRITICAL |
| `bib-standalone-missing` | Subfile missing biblatex | WARNING |
| `bib-style-mismatch` | bibtex style with biblatex | WARNING |

## Workflow

1. LLM invokes Python tool via `tool.py`
2. Python returns list of issues
3. LLM formats results for parent orchestrator

## Mission Statement

Detect all citation and bibliography issues that may cause compilation
errors or missing references using deterministic Python regex patterns.

## Version History
- **v1.0.0** (2025-12-15): Initial creation with Python backend
