# BC Claude System

## Overview

The BC (Book Creator) Claude system provides automated content creation for Hebrew-English LaTeX academic books. It uses a 3-level hierarchical architecture mirroring the QA system, with integrated QA validation to ensure content passes quality checks BEFORE writing.

## Three-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Level 0: Super Orchestrator                 │
├─────────────────────────────────────────────────────────────────┤
│  bc-super                                                       │
│  - Coordinates 3 stages                                         │
│  - Manages BC-TASKS.md                                          │
│  - Runs QA validators before output                             │
│  - Configuration: bc_pipeline.json                              │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Level 1: Stage Orchestrators                  │
├───────────────┬───────────────────────┬─────────────────────────┤
│  bc-research  │     bc-content        │      bc-review          │
│  Stage 1      │     Stage 2           │      Stage 3            │
│  Sources      │     Drafting          │      Polish             │
└───────────────┴───────────────────────┴─────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Level 2: Worker Skills                      │
├─────────────────────────────────────────────────────────────────┤
│  bc-source-research │ bc-code  │ bc-math │ bc-academic-source   │
│      (Garfield)     │  (Levy)  │(Hinton) │     (Segal)          │
│                     │          │         │                       │
│                     │ bc-architect (Harari) │ bc-hebrew (Academy)│
└─────────────────────────────────────────────────────────────────┘
```

## Stage Flow

```
Stage 1: Research          Stage 2: Content           Stage 3: Review
───────────────────────────────────────────────────────────────────────
       │                         │                         │
       ▼                         ▼                         ▼
┌─────────────┐           ┌─────────────┐           ┌─────────────┐
│ bc-source-  │           │  bc-code    │           │bc-architect │
│ research    │           │  bc-math    │           │ (Harari)    │
│             │           │  bc-acad-   │           │             │
│             │           │  source     │           │ bc-hebrew   │
└─────────────┘           └─────────────┘           │ (Polish)    │
       │                         │                  └─────────────┘
       ▼                         ▼                         │
 [BCBibValidator]      [BCBiDiValidator]                   ▼
                       [BCCodeValidator]           [BCBiDiValidator]
                       [BCTableValidator]          [BCTOCValidator]
       │                         │                         │
       ▼                         ▼                         ▼
Source_Collection     Content_Drafting              Review_Complete
    _Complete              _Complete
```

## Skill Hierarchy

### Level 0: bc-super
- **Role:** Top-level coordinator
- **Manages:** bc-research, bc-content, bc-review
- **Config:** bc_pipeline.json
- **Output:** BC-REPORT.md

### Level 1: Stage Orchestrators

| Skill | Stage | Workers | Validators |
|-------|-------|---------|------------|
| bc-research | 1 | bc-source-research | BCBibValidator |
| bc-content | 2 | bc-code, bc-math, bc-academic-source | BCBiDiValidator, BCCodeValidator, BCTableValidator |
| bc-review | 3 | bc-architect, bc-hebrew | BCBiDiValidator, BCTOCValidator |

### Level 2: Worker Skills

| Skill | Parent | Persona | Validators |
|-------|--------|---------|------------|
| bc-source-research | bc-research | Garfield | BCBibValidator |
| bc-code | bc-content | Levy | BCCodeValidator, BCBiDiValidator |
| bc-math | bc-content | Hinton | BCBiDiValidator, BCHebMathValidator |
| bc-academic-source | bc-content | Segal | BCTableValidator, BCBibValidator |
| bc-architect | bc-review | Harari | BCBiDiValidator, BCTOCValidator |
| bc-hebrew | bc-review | Academy | BCBiDiValidator |

## QA Integration

### Validation Flow
```
Content Generated → Validate → Auto-Fix → Validate Again → Write
                      ↓
                  If unfixable → Report to LLM for retry
```

### Validators Per Stage

| Stage | Validators | Auto-Fix |
|-------|------------|----------|
| 1 | BCBibValidator | Yes (cite keys) |
| 2 | BCBiDiValidator, BCCodeValidator, BCTableValidator | Yes (wrappers) |
| 3 | BCBiDiValidator, BCTOCValidator | Yes (English) |

## Usage

### Run Full BC Pipeline
```bash
# Using bc-super
invoke bc-super --project path/to/book

# Specific stage only
invoke bc-content --chapter 5
```

### Run Specific Worker
```bash
invoke bc-code --chapter 5 --section 5.2
invoke bc-math --chapter 3
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
    }
  }
}
```

## Key Principles

1. **Hierarchical Orchestration:** 3-level structure like QA system
2. **Inline Validation:** QA checks BEFORE write, not after
3. **Auto-Fix First:** Python fixes issues before LLM retry
4. **Stage Dependencies:** Each stage requires previous to complete
5. **Parallel Where Possible:** Stage 1 & 2 run workers in parallel
6. **Sequential Review:** Stage 3 is sequential (Harari → Hebrew)

## Comparison: BC vs QA

| Aspect | QA System | BC System |
|--------|-----------|-----------|
| Purpose | Detect & Fix | Create & Validate |
| Level 0 | qa-super | bc-super |
| Level 1 | Family (BiDi, code, table) | Stage (research, content, review) |
| Level 2 | Detect + Fix skills | Worker skills (personas) |
| Python Tools | Detectors + Fixers | Validators (reuse QA) |
| Config | qa_setup.json | bc_pipeline.json |
| Output | QA-REPORT.md | BC-REPORT.md |

## Version History
- **v1.0.0** (2025-12-21): Initial 3-level architecture

---

*Configuration:* bc_pipeline.json
*Tasks:* BC-TASKS.md
*Report:* BC-REPORT.md
