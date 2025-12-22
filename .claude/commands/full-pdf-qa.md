---
name: full-pdf-qa
description: Run comprehensive QA on a LaTeX document
arguments:
  - name: target
    description: Path to the LaTeX document or project directory
    required: true
---

# Full PDF QA

Run comprehensive quality assurance on the specified LaTeX document.

## Target
$ARGUMENTS

## Execution Phases

### Phase 0: CLS Version Check (BLOCKING)
- Invoke qa-cls-version-detect on target
- If outdated CLS found, STOP and report
- User must approve CLS update before proceeding

### Phase 1: Pre-Compilation (Python Tools - Fast, Deterministic)

Run all source-level detectors in parallel using Python tools:

| Detector | Python Tool | Purpose |
|----------|-------------|---------|
| qa-BiDi-detect | BiDiDetector | Bidirectional text issues |
| qa-code-detect | CodeDetector | Code block issues |
| qa-table-detect | TableDetector | Table formatting issues |
| qa-bib-detect | BibDetector | Bibliography/citation issues |
| qa-coverpage-detect | CoverpageDetector | Cover page metadata (source) |
| qa-img-detect | ImageDetector | Image/figure issues (source) |
| qa-infra-subfiles-detect | SubfilesDetector | Subfiles structure issues |
| qa-typeset-detect | TypesetDetector | LaTeX compilation warnings |

```python
import sys
sys.path.insert(0, "src")

from qa_engine.sdk import QAController

controller = QAController()
pre_results = controller.run_pre_compilation("$ARGUMENTS")
print(controller.generate_report(pre_results, format="markdown"))
```

### Phase 2: Apply Fixes (if auto_fix enabled)

For issues with `auto_fix: true`, apply fixes:
- qa-BiDi-fix-text
- qa-code-fix-background
- qa-table-fix
- qa-bib-fix
- qa-img-fix-paths

### Phase 3: Compilation

Compile the LaTeX document:
```bash
lualatex -interaction=nonstopmode "$ARGUMENTS"
```

### Phase 4: Post-Compilation (LLM Skills - Visual Verification)

Run PDF-level validators using LLM skills:

| Skill | Purpose | Requires |
|-------|---------|----------|
| qa-img-validate | Verify images render in PDF | LLM + PDF |
| qa-coverpage | Validate cover page visually | LLM + PDF |

These skills require LLM because they need:
- Visual inspection of rendered PDF
- List of Figures cross-reference
- Detection of empty boxes/placeholders in output

### Phase 5: Aggregate Results

1. Merge pre-compilation and post-compilation results
2. Group by severity (CRITICAL, WARNING, INFO)
3. Group by phase (pre_compilation, post_compilation)
4. Generate comprehensive report

## Report Output

```markdown
# QA Report for $ARGUMENTS

## Summary
- Pre-compilation issues: [N]
- Post-compilation issues: [N]
- Total: [N]

## Pre-Compilation (Source-Level)
| Rule | Count | Severity | Auto-Fix |
|------|-------|----------|----------|
| ... | ... | ... | ... |

## Post-Compilation (PDF-Level)
| Rule | Count | Severity | Requires |
|------|-------|----------|----------|
| ... | ... | ... | LLM |

## Detailed Issues
[file:line references with suggested fixes]
```

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Phase 0: CLS Version Check                       │
│                         (BLOCKING)                                  │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│               Phase 1: PRE-COMPILATION (Python)                     │
│                                                                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │BiDiDetect│ │CodeDetect│ │TableDet. │ │ BibDet.  │ │ ImgDet.  │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
│                    (All run in PARALLEL)                            │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                 Phase 2: APPLY FIXES (if enabled)                   │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Phase 3: COMPILATION                             │
│                      lualatex → PDF                                 │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│              Phase 4: POST-COMPILATION (LLM)                        │
│                                                                     │
│  ┌─────────────────────┐    ┌─────────────────────┐                │
│  │   qa-img-validate   │    │    qa-coverpage     │                │
│  │  (Visual PDF check) │    │  (Visual PDF check) │                │
│  └─────────────────────┘    └─────────────────────┘                │
│                    (Requires LLM + PDF)                             │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                Phase 5: AGGREGATE & REPORT                          │
└─────────────────────────────────────────────────────────────────────┘
```

## Important Notes

- **Pre-compilation**: All detection by Python tools (deterministic, no LLM cost)
- **Post-compilation**: LLM skills for visual PDF verification (requires compilation)
- If document exceeds 500 lines, automatic chunking is applied
- Results are deduplicated at chunk boundaries
- Configuration in `config/qa_setup.json`
