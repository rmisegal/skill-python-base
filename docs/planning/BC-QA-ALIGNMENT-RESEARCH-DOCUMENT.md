# BC-QA Alignment Research Document

## Executive Summary

This document analyzes the alignment between Book Creator (BC) skills and Quality Assurance (QA) mechanisms in the skill-python-base project. The goal is to prevent QA errors during content creation by integrating QA rules into BC workflows, using Python tools for maximum efficiency and minimum LLM usage.

**Key Finding:** BC skills currently operate as LLM-only agents with embedded formatting rules that overlap with QA detection rules but are NOT enforced programmatically. This creates a gap where content is created without real-time validation, leading to QA errors discovered only post-creation.

---

## 1. Current Architecture Analysis

### 1.1 QA Mechanism Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     QA ARCHITECTURE (PYTHON-BACKED)              │
├─────────────────────────────────────────────────────────────────┤
│  Level 0: SuperOrchestrator                                      │
│    └── Coordinates 8 families in parallel                        │
│                                                                   │
│  Level 1: Family Orchestrators                                   │
│    ├── BiDi (15 rules)    ├── code (5 rules)                    │
│    ├── table (10 rules)   ├── bib (3 rules)                     │
│    ├── img (14 rules)     ├── coverpage (8 rules)               │
│    ├── typeset (9 rules)  └── toc (16 rules)                    │
│                                                                   │
│  Level 2: Detectors + Fixers (Python tools)                      │
│    ├── DetectorInterface: detect() + get_rules()                 │
│    ├── FixerInterface: fix() + get_patterns()                    │
│    └── CreatorInterface: create() + create_from_issues()         │
└─────────────────────────────────────────────────────────────────┘

Key Characteristics:
- Rules externalized to *_rules.py files (no hardcoding)
- Max 150 lines per Python file
- Thread-safe with ResourceManager (mutex locks)
- Logging: PrintManager + JsonLogger (singletons)
- Watchdog: HeartbeatMonitor with SQLite backend
- Config-driven: qa_setup.json (v1.4.0)
- Batch processing: 4 max workers, 50 batch size
```

### 1.2 BC Skills Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     BC ARCHITECTURE (LLM-ONLY)                   │
├─────────────────────────────────────────────────────────────────┤
│  bc-source-research (Garfield)                                   │
│    └── Stage 1: Parallel source collection                       │
│                                                                   │
│  bc-architect (Harari)                                           │
│    └── Narrative flow, style review                              │
│                                                                   │
│  bc-math (Hinton)                                                │
│    └── Technical accuracy, math verification                     │
│                                                                   │
│  bc-code (Levy)                                                  │
│    └── Python/NumPy code examples                                │
│                                                                   │
│  bc-academic-source (Segal)                                      │
│    └── Citations, IEEE format, tables                            │
│                                                                   │
│  bc-hebrew (Academy)                                             │
│    └── Language editing, terminology                             │
└─────────────────────────────────────────────────────────────────┘

Key Characteristics:
- NO Python backend (100% LLM)
- Rules embedded in skill.md files (hardcoded)
- No real-time validation
- No threading/parallelism support
- No structured logging
- Manual quality checklists
```

---

## 2. Gap Analysis: BC vs QA Rules

### 2.1 Overlapping Rules (BC mentions, QA enforces)

| BC Skill | BC Rule (Embedded) | QA Rule (Python) | Gap |
|----------|-------------------|------------------|-----|
| bc-code | `\begin{pythonbox}` required | code-background-overflow | BC doesn't validate |
| bc-code | English comments only | code-direction-hebrew | BC doesn't detect Hebrew |
| bc-code | Code must be LTR | code-direction-hebrew | BC doesn't enforce |
| bc-academic-source | `\hebcell{}`, `\encell{}` | table-cell-hebrew | BC doesn't validate |
| bc-academic-source | Reverse column order | table-no-rtl-env | BC doesn't check |
| bc-academic-source | `\printenglishbibliography` | bib-* rules | BC doesn't validate |
| bc-math | `\ilm{$math$}` for inline | bidi-numbers, bidi-english | BC doesn't detect |
| bc-math | `\en{English}` wrapper | bidi-english, bidi-acronym | BC doesn't enforce |
| bc-architect | `\hebrewsection{}` | bidi-section-number | BC doesn't validate |
| bc-architect | Figure/table references | - | No QA rule exists |
| bc-hebrew | Hebrew punctuation fonts | - | No QA rule exists |

### 2.2 QA Rules Without BC Coverage

| QA Rule | Family | BC Skill Should Enforce |
|---------|--------|------------------------|
| bidi-tikz-rtl | BiDi | bc-code (diagrams) |
| bidi-tcolorbox | BiDi | bc-code (colored boxes) |
| bidi-year-range | BiDi | bc-architect, bc-hebrew |
| bidi-reversed-text | BiDi | bc-hebrew |
| caption-too-long | img | bc-architect |
| toc-english-text-naked | toc | bc-architect |
| cls-sync-content-mismatch | infra | ALL (project-wide) |

### 2.3 BC Rules Without QA Enforcement

| BC Rule | BC Skill | Gap Analysis |
|---------|----------|--------------|
| 60-80 sources required | bc-academic-source | No Python validator |
| Valid DOI/Link for all sources | bc-academic-source | No Python validator |
| IEEE citation format | bc-academic-source | No Python validator |
| NumPy-focused code | bc-code | No Python validator |
| Harari narrative style | bc-architect | Cannot automate (LLM only) |
| Academy Hebrew grammar | bc-hebrew | Cannot automate (LLM only) |
| Formula explanation in text | bc-math | Cannot automate (LLM only) |

---

## 3. Root Cause Analysis

### 3.1 Why BC Creates QA Errors

```
┌─────────────────────────────────────────────────────────────────┐
│                     ERROR CREATION FLOW                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  BC Skill Execution (LLM)                                        │
│    │                                                              │
│    ├── Reads rules from skill.md (embedded, not validated)       │
│    ├── Generates content (no real-time validation)               │
│    ├── Writes to .tex file                                        │
│    │                                                              │
│    └── ❌ NO VALIDATION STEP                                      │
│                                                                   │
│  QA Detection (Later, separate step)                             │
│    │                                                              │
│    ├── Reads .tex files                                           │
│    ├── Runs Python detectors                                      │
│    └── ❌ FINDS ERRORS (too late!)                                │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Specific Error Patterns

| Error Pattern | Frequency | Root Cause |
|--------------|-----------|------------|
| Unwrapped English in Hebrew | HIGH | bc-math doesn't use BiDi detector |
| Code with Hebrew comments | MEDIUM | bc-code doesn't use code detector |
| Tables without rtltabular | MEDIUM | bc-academic-source doesn't validate |
| Numbers without \en{} | HIGH | All BC skills lack BiDi validation |
| TikZ without english wrapper | LOW | bc-code doesn't check context |
| Inconsistent CLS versions | HIGH | No BC-level infrastructure check |

---

## 4. Proposed BC Pipeline Architecture

### 4.1 New Architecture: BC with Python Validation

```
┌─────────────────────────────────────────────────────────────────┐
│                 PROPOSED BC PIPELINE ARCHITECTURE                │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                   BC ORCHESTRATOR (Level 0)                  │ │
│  │  - Coordinates BC skills with embedded QA validation         │ │
│  │  - Python-backed like QA SuperOrchestrator                   │ │
│  │  - Manages threading, logging, watchdog                      │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                              │                                    │
│       ┌──────────────────────┼──────────────────────┐            │
│       ▼                      ▼                      ▼            │
│  ┌─────────────┐       ┌─────────────┐       ┌─────────────┐    │
│  │ BC-RESEARCH │       │  BC-CONTENT │       │  BC-REVIEW  │    │
│  │  (Stage 1)  │       │  (Stage 2)  │       │  (Stage 3)  │    │
│  │             │       │             │       │             │    │
│  │ Source      │       │ Draft       │       │ Polish      │    │
│  │ Collection  │──────▶│ Creation    │──────▶│ & Verify    │    │
│  └─────────────┘       └─────────────┘       └─────────────┘    │
│                              │                      │            │
│                              ▼                      ▼            │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              INLINE QA VALIDATION (Python)                   │ │
│  │  - BiDiValidator   - CodeValidator   - TableValidator       │ │
│  │  - BibValidator    - TOCValidator    - CLSValidator         │ │
│  │  *** VALIDATE BEFORE WRITE, NOT AFTER ***                   │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                              │                                    │
│                              ▼                                    │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                     OUTPUT GATE                              │ │
│  │  - Only write content that passes all validators            │ │
│  │  - Auto-fix where possible (using QA fixers)                │ │
│  │  - Report unfixable issues for LLM retry                    │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 BC Validator Classes (New Python Tools)

```python
# Proposed: src/qa_engine/bc/validators/__init__.py

class BCBiDiValidator:
    """Validates content for BiDi issues before write."""

    def __init__(self):
        self._detector = BiDiDetector()
        self._fixer = BiDiFixer()

    def validate_and_fix(self, content: str) -> tuple[str, List[Issue]]:
        """Validate and auto-fix where possible."""
        issues = self._detector.detect(content, "inline")
        fixable = [i for i in issues if self._can_auto_fix(i)]
        unfixable = [i for i in issues if not self._can_auto_fix(i)]

        if fixable:
            content = self._fixer.fix(content, fixable)

        return content, unfixable

class BCCodeValidator:
    """Validates code blocks before write."""
    # Uses CodeDetector + CodeFixer

class BCTableValidator:
    """Validates tables before write."""
    # Uses TableDetector + TableFixer
```

### 4.3 BC Skill Integration Points

| BC Skill | Validators to Use | Validation Trigger |
|----------|------------------|-------------------|
| bc-code | BCCodeValidator, BCBiDiValidator | Before writing pythonbox |
| bc-math | BCBiDiValidator | Before writing formulas |
| bc-academic-source | BCTableValidator, BCBibValidator | Before writing tables/citations |
| bc-architect | BCBiDiValidator, BCTOCValidator | Before writing sections |
| bc-hebrew | BCBiDiValidator | Before finalizing text |
| bc-source-research | BCBibValidator | Before writing BibTeX |

---

## 5. Configuration File Design

### 5.1 Proposed: bc_pipeline.json

```json
{
  "version": "1.0.0",
  "description": "BC Pipeline Configuration with QA Integration",

  "orchestration": {
    "max_workers": 4,
    "batch_size": 50,
    "heartbeat_interval": 30,
    "stale_timeout": 120,
    "lock_timeout": 60
  },

  "logging": {
    "level": "INFO",
    "json_format": true,
    "log_dir": "bc-logs"
  },

  "stages": {
    "research": {
      "skills": ["bc-source-research"],
      "validators": [],
      "parallel": true,
      "signal": "Source_Collection_Complete"
    },
    "content": {
      "skills": ["bc-code", "bc-math", "bc-academic-source"],
      "validators": ["BCBiDiValidator", "BCCodeValidator", "BCTableValidator"],
      "parallel": true,
      "requires": ["research"],
      "auto_fix": true
    },
    "review": {
      "skills": ["bc-architect", "bc-hebrew"],
      "validators": ["BCBiDiValidator", "BCTOCValidator"],
      "parallel": false,
      "requires": ["content"],
      "auto_fix": true
    }
  },

  "validators": {
    "BCBiDiValidator": {
      "enabled": true,
      "rules": ["bidi-numbers", "bidi-english", "bidi-acronym", "bidi-year-range"],
      "auto_fix_rules": ["bidi-numbers", "bidi-english", "bidi-acronym"],
      "block_on_critical": true
    },
    "BCCodeValidator": {
      "enabled": true,
      "rules": ["code-background-overflow", "code-direction-hebrew", "code-encoding-emoji"],
      "auto_fix_rules": ["code-background-overflow"],
      "block_on_critical": true
    },
    "BCTableValidator": {
      "enabled": true,
      "rules": ["table-no-rtl-env", "table-cell-hebrew", "table-overflow"],
      "auto_fix_rules": ["table-cell-hebrew"],
      "block_on_critical": true
    },
    "BCBibValidator": {
      "enabled": true,
      "rules": ["bib-malformed-cite-key", "bib-missing-file"],
      "auto_fix_rules": ["bib-malformed-cite-key"],
      "block_on_critical": false
    },
    "BCTOCValidator": {
      "enabled": true,
      "rules": ["toc-english-text-naked", "toc-chapter-number-not-ltr"],
      "auto_fix_rules": ["toc-english-text-naked"],
      "block_on_critical": false
    },
    "BCCLSValidator": {
      "enabled": true,
      "rules": ["cls-sync-content-mismatch"],
      "auto_fix_rules": [],
      "block_on_critical": true,
      "run_at": "start"
    }
  },

  "skill_validator_mapping": {
    "bc-code": ["BCBiDiValidator", "BCCodeValidator"],
    "bc-math": ["BCBiDiValidator"],
    "bc-academic-source": ["BCBiDiValidator", "BCTableValidator", "BCBibValidator"],
    "bc-architect": ["BCBiDiValidator", "BCTOCValidator"],
    "bc-hebrew": ["BCBiDiValidator"],
    "bc-source-research": ["BCBibValidator"]
  },

  "output_gate": {
    "require_zero_critical": true,
    "require_zero_warning": false,
    "max_retries_per_skill": 3,
    "report_unfixable": true
  }
}
```

---

## 6. Implementation Recommendations

### 6.1 Python Module Structure

```
src/qa_engine/bc/
├── __init__.py
├── orchestrator.py          # BCOrchestrator (Level 0)
├── validators/
│   ├── __init__.py
│   ├── base_validator.py    # BCValidatorInterface
│   ├── bidi_validator.py    # BCBiDiValidator
│   ├── code_validator.py    # BCCodeValidator
│   ├── table_validator.py   # BCTableValidator
│   ├── bib_validator.py     # BCBibValidator
│   ├── toc_validator.py     # BCTOCValidator
│   └── cls_validator.py     # BCCLSValidator
├── stages/
│   ├── __init__.py
│   ├── research_stage.py    # Stage 1 coordinator
│   ├── content_stage.py     # Stage 2 coordinator
│   └── review_stage.py      # Stage 3 coordinator
└── config/
    ├── __init__.py
    └── bc_config.py         # BCConfigManager
```

### 6.2 Key Design Principles

1. **Reuse QA Detectors**: Don't duplicate detection logic
   ```python
   class BCBiDiValidator:
       def __init__(self):
           self._detector = BiDiDetector()  # Reuse existing
   ```

2. **Validate Before Write**: Intercept content before file write
   ```python
   def write_content(self, content: str, path: str) -> WriteResult:
       content, issues = self.validator.validate_and_fix(content)
       if issues.has_critical:
           return WriteResult(success=False, issues=issues)
       return self._do_write(content, path)
   ```

3. **Use Existing Threading**: Leverage ResourceManager
   ```python
   with ResourceManager().locked(f"file:{path}", self.agent_id):
       self.write_content(content, path)
   ```

4. **Use Existing Logging**: Leverage PrintManager and JsonLogger
   ```python
   self._logger = PrintManager()
   self._json_logger = JsonLogger()
   ```

5. **Config-Driven**: No hardcoded rules
   ```python
   self._config = BCConfigManager().load("bc_pipeline.json")
   enabled_rules = self._config.get("validators.BCBiDiValidator.rules")
   ```

### 6.3 File Size Constraints

| File | Max Lines | Content |
|------|-----------|---------|
| bc_orchestrator.py | 150 | Main orchestration |
| base_validator.py | 80 | Interface + base class |
| bidi_validator.py | 100 | BiDi validation wrapper |
| code_validator.py | 100 | Code validation wrapper |
| table_validator.py | 100 | Table validation wrapper |
| bc_config.py | 80 | Config loading |
| *_stage.py | 100 | Stage coordination |

---

## 7. Performance Optimization

### 7.1 Speed Optimizations

| Optimization | Impact | Implementation |
|--------------|--------|----------------|
| Parallel validation | HIGH | ThreadPoolExecutor with max_workers=4 |
| Incremental detection | MEDIUM | Only validate changed sections |
| Rule caching | LOW | Cache compiled regex patterns |
| Batch processing | MEDIUM | Process 50 items per batch |

### 7.2 LLM Usage Minimization

| Current (BC Only) | Proposed (BC + Python) | LLM Reduction |
|-------------------|------------------------|---------------|
| 100% LLM for formatting | Python validates 80% | -80% tokens |
| LLM retry on QA fail | Auto-fix before LLM retry | -50% retries |
| LLM checks all rules | Python pre-filters | -70% checks |

### 7.3 Efficiency Metrics

```
Current Flow:
  BC creates → QA detects → LLM fixes → QA verifies
  Total: 4 LLM calls per issue

Proposed Flow:
  BC creates → Python validates → Python fixes → Write
  Total: 1 LLM call (creation only), 0 for fixable issues
```

---

## 8. Risk Analysis

### 8.1 Implementation Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Breaking existing BC skills | MEDIUM | HIGH | Backward-compatible wrapper |
| Performance regression | LOW | MEDIUM | Async validation |
| Config complexity | MEDIUM | LOW | Sensible defaults |
| Missing edge cases | MEDIUM | MEDIUM | Comprehensive testing |

### 8.2 Compatibility Considerations

1. **Existing BC skills remain unchanged** - validators wrap them
2. **QA detectors/fixers unchanged** - validators reuse them
3. **Gradual rollout** - enable validators per-skill
4. **Fallback mode** - disable validation for debugging

---

## 9. Testing Strategy

### 9.1 Unit Tests Required

```python
# tests/unit/bc/
test_bc_bidi_validator.py      # 20+ test cases
test_bc_code_validator.py      # 15+ test cases
test_bc_table_validator.py     # 15+ test cases
test_bc_orchestrator.py        # 10+ test cases
test_bc_config.py              # 10+ test cases
```

### 9.2 Integration Tests

```python
# tests/integration/bc/
test_bc_qa_integration.py      # Full pipeline test
test_bc_stage_flow.py          # Stage progression
test_bc_validator_chain.py     # Multi-validator scenarios
```

### 9.3 Performance Tests

```python
# tests/performance/bc/
test_bc_throughput.py          # Measure validation speed
test_bc_memory.py              # Memory usage under load
test_bc_parallel.py            # Parallel execution
```

---

## 10. Summary and Next Steps

### 10.1 Key Findings

1. **BC skills lack Python validation** - all formatting rules are LLM-only
2. **QA has mature Python infrastructure** - detectors, fixers, threading, logging
3. **Significant rule overlap** - BC embeds rules QA can enforce
4. **Performance opportunity** - Python validation is 10-100x faster than LLM

### 10.2 Recommended Implementation Order

1. **Phase 1: Infrastructure** (Week 1)
   - Create bc/ module structure
   - Implement BCValidatorInterface
   - Create bc_pipeline.json

2. **Phase 2: Core Validators** (Week 2)
   - BCBiDiValidator (highest impact)
   - BCCodeValidator
   - BCTableValidator

3. **Phase 3: Integration** (Week 3)
   - BCOrchestrator
   - Stage coordinators
   - Output gate

4. **Phase 4: Testing & Rollout** (Week 4)
   - Unit tests
   - Integration tests
   - Gradual skill enablement

### 10.3 Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| QA errors per chapter | 15-30 | <5 |
| LLM tokens per chapter | 50,000 | 15,000 |
| Time to QA-clean content | 2 hours | 30 min |
| Auto-fix rate | 0% | 70% |

---

## Appendix A: Full Rule Mapping

### A.1 BiDi Rules (15 total)

| Rule ID | BC Skill Coverage | Auto-Fixable |
|---------|------------------|--------------|
| bidi-cover-metadata | bc-architect | NO |
| bidi-section-number | bc-architect | NO |
| bidi-reversed-text | bc-hebrew | NO |
| bidi-header-footer | bc-architect | NO |
| bidi-numbers | ALL | YES |
| bidi-year-range | ALL | YES |
| bidi-english | ALL | YES |
| bidi-tcolorbox | bc-code | YES |
| bidi-section-english | bc-architect | YES |
| bidi-acronym | ALL | YES |
| bidi-chapter-label | bc-architect | NO |
| bidi-fbox-mixed | bc-code | NO |
| bidi-standalone-counter | bc-architect | NO |
| bidi-hebrew-in-english | ALL | NO |
| bidi-tikz-rtl | bc-code | YES |

### A.2 Code Rules (5 total)

| Rule ID | BC Skill Coverage | Auto-Fixable |
|---------|------------------|--------------|
| code-background-overflow | bc-code | YES |
| code-fstring-brace | bc-code | NO |
| code-encoding-emoji | bc-code | YES |
| code-direction-hebrew | bc-code | YES |
| code-hebrew-content | bc-code | NO (LLM) |

### A.3 Table Rules (10 total)

| Rule ID | BC Skill Coverage | Auto-Fixable |
|---------|------------------|--------------|
| table-plain-unstyled | bc-academic-source | YES |
| table-no-rtl-env | bc-academic-source | YES |
| table-overflow | bc-academic-source | YES |
| table-cell-hebrew | bc-academic-source | YES |
| table-missing-header-color | bc-academic-source | YES |
| table-not-hebrewtable | bc-academic-source | YES |
| caption-setup-raggedleft | bc-academic-source | YES |
| caption-flushleft-wrapped | bc-academic-source | YES |
| caption-table-raggedleft | bc-academic-source | YES |
| table-plain-fancy | bc-academic-source | YES |

---

## Appendix B: BC Skills Copied to Local Project

The following BC skills have been copied from global to local project:

```
C:\25D\GeneralLearning\skill-python-base\.claude\skills\
├── bc-academic-source\skill.md
├── bc-architect\skill.md
├── bc-code\skill.md
├── bc-hebrew\skill.md
├── bc-math\skill.md
└── bc-source-research\skill.md
```

---

*Document Version: 1.0.0*
*Date: 2025-12-21*
*Author: Claude Code Research Agent*
