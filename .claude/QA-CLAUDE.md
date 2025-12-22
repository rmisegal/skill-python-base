# QA Claude System

## Overview

The QA Claude system provides automated quality assurance for Hebrew-English LaTeX documents. It uses a hybrid architecture combining Claude CLI skills (LLM capabilities) with deterministic Python tools for consistent, efficient detection and fixing.

## Two-Phase Workflow

The QA system uses a two-phase workflow for optimal efficiency:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PHASE 1: PRE-COMPILATION                         │
│                    (Python Tools - Fast, Deterministic)             │
├─────────────────────────────────────────────────────────────────────┤
│  BiDiDetector │ CodeDetector │ TableDetector │ ImageDetector │ ... │
│                    Source-level detection                           │
│                    No LLM cost, consistent results                  │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                      [LaTeX Compilation]
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   PHASE 2: POST-COMPILATION                         │
│                   (LLM Skills - Visual Verification)                │
├─────────────────────────────────────────────────────────────────────┤
│           qa-img-validate │ qa-coverpage (PDF validation)          │
│                    PDF-level validation                             │
│                    Requires LLM for visual inspection               │
└─────────────────────────────────────────────────────────────────────┘
```

### Phase Characteristics

| Phase | Tools | Cost | Speed | Purpose |
|-------|-------|------|-------|---------|
| Pre-compilation | Python | Free | Fast | Source-level detection |
| Post-compilation | LLM | Tokens | Slower | Visual PDF verification |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Level 0: Entry Points                       │
├─────────────────────────────────────────────────────────────────┤
│  qa-super           │  insert_qa_skill    │  /full-pdf-qa       │
│  Super Orchestrator │  Meta-Skill         │  Command            │
└─────────────────────┴─────────────────────┴─────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Level 1: Family Orchestrators                  │
├────────────┬────────────┬────────────┬────────────┬─────────────┤
│  qa-BiDi   │  qa-code   │ qa-typeset │  qa-table  │  qa-infra   │
│  qa-bib    │qa-cls-ver  │qa-coverpage│   qa-img   │             │
└────────────┴────────────┴────────────┴────────────┴─────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Level 2: Worker Skills                        │
├─────────────────────────────┬───────────────────────────────────┤
│         Detection           │              Fixing               │
├─────────────────────────────┼───────────────────────────────────┤
│  qa-BiDi-detect            │  qa-BiDi-fix-text                 │
│  qa-code-detect            │  qa-code-fix-background           │
│  qa-typeset-detect         │  qa-cls-version-fix               │
│  qa-table-detect           │  qa-img-fix-paths                 │
│  qa-infra-subfiles-detect  │  qa-cls-sync-fix                  │
│  qa-bib-detect             │                                   │
│  qa-cls-version-detect     │                                   │
│  qa-cls-sync-detect        │                                   │
│  qa-coverpage-detect       │                                   │
│  qa-img-detect             │                                   │
└─────────────────────────────┴───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Python Tool Layer                            │
├─────────────────────────────────────────────────────────────────┤
│  qa_engine/                                                      │
│  ├── shared/         # Interfaces, config, exceptions           │
│  ├── domain/         # Document analyzer, rules                 │
│  ├── infrastructure/ # Detectors, fixers, reporting            │
│  └── sdk/            # QAController, SkillCreator              │
└─────────────────────────────────────────────────────────────────┘
```

## Detection Rules

### BiDi Detection (15 rules)
- Cover page metadata direction
- Section numbering Hebrew
- Reversed text (final letters)
- Header/footer Hebrew
- Numbers without LTR wrapper
- English without LTR wrapper
- tcolorbox BiDi-safe wrapper
- Section titles with English
- Uppercase acronyms
- Chapter labels
- fbox/parbox mixed content
- Standalone counter
- Hebrew in English wrapper
- TikZ in RTL context
- mdframed environments

### Table Detection (5 rules)
- tabular without rtltabular
- Caption position (before table)
- Hebrew in cells
- Plain unstyled tables
- Wide table overflow

### Subfiles Detection (3 rules)
- Missing subfiles class
- No main document reference
- Missing standalone preamble

### Bibliography Detection (5 rules)
- Missing bibliography file
- Undefined citations
- Empty citations
- Standalone biblatex config
- Style mismatch

### CLS Version Detection (3 rules)
- Outdated class file version
- Missing required CLS
- Modified CLS checksum

### CLS Sync Detection (3 rules)
- cls-sync-content-mismatch: CLS file content differs from master
- cls-sync-size-mismatch: CLS file size differs from master
- cls-sync-no-master: No master CLS file found for reference

### Image Detection (11 rules)

**Pre-compilation (Python - 8 rules):**
- img-file-not-found (CRITICAL)
- img-no-graphicspath (WARNING)
- img-wrong-extension (WARNING)
- img-case-mismatch (WARNING)
- img-placeholder-box (WARNING)
- img-empty-figure (WARNING)
- img-hebrew-figure-empty (WARNING)
- img-no-size-spec (INFO)

**Post-compilation (LLM - 3 rules):**
- img-not-rendered (requires PDF)
- img-empty-box-visual (requires PDF)
- img-lof-mismatch (requires PDF)

### Coverpage Detection (8 rules)

**Pre-compilation (Python):**
- cover-hebrew-title
- cover-hebrew-subtitle
- cover-hebrew-author
- cover-english-in-hebrew
- cover-numbers-unwrapped
- cover-acronym-unwrapped
- cover-date-format
- cover-copyright-bidi

**Post-compilation (LLM):**
- Visual layout validation
- BiDi rendering verification

## Usage

### Run Full QA

```bash
# Using the command
/full-pdf-qa path/to/document.tex

# Using the skill directly
invoke qa-super --target path/to/document.tex
```

### Create New Skill

```bash
# Using insert_qa_skill
invoke insert_qa_skill --mode=create \
  --name=qa-new-detect \
  --family=new \
  --level=2 \
  --type=detection \
  --description="Detect new issues" \
  --python=true
```

### Run Specific Family

```bash
invoke qa-BiDi --target path/to/document.tex
invoke qa-table --target path/to/document.tex
```

## Python API

```python
from qa_engine.sdk import QAController

# Initialize controller
controller = QAController()

# Run full QA
results = controller.run_full_qa("path/to/document.tex")

# Generate report
controller.generate_report(results, format="markdown")
```

## Configuration

Configuration is stored in `config/qa_setup.json`:

```json
{
  "version": "1.1.0",
  "enabled_families": ["BiDi", "code", "table", "bib", "coverpage", "img"],
  "global_workflow": {
    "phases": {
      "pre_compilation": {
        "description": "Source-level detection (Python)",
        "tools": ["ImageDetector", "BiDiDetector", "..."],
        "skills": ["qa-img-detect", "qa-BiDi-detect", "..."]
      },
      "compilation": {
        "description": "Compile LaTeX to PDF",
        "command": "lualatex"
      },
      "post_compilation": {
        "description": "PDF-level validation (LLM)",
        "skills": ["qa-img-validate", "qa-coverpage"],
        "note": "Requires LLM for visual inspection"
      }
    },
    "order": ["pre_compilation", "compilation", "post_compilation"]
  },
  "families": {
    "img": {
      "rules": {
        "img-file-not-found": {"phase": "pre_compilation"},
        "img-not-rendered": {"phase": "post_compilation", "requires_llm": true}
      }
    }
  }
}
```

## Key Principles

1. **Two-Phase Workflow**: Pre-compilation (Python) then post-compilation (LLM)
2. **Determinism First**: All source-level detection uses Python regex
3. **Separation of Concerns**: Detectors MUST NOT modify; Fixers MUST NOT detect
4. **Token Efficiency**: Python for pattern matching, LLM for visual judgment
5. **Composability**: Each skill works independently or as part of orchestration
6. **Fail Safe**: Errors in one family don't block others

## Test Coverage

- 574 tests passing
- All architecture constraints enforced
- File size limit: 150 lines per Python file
- Layer dependency validation
