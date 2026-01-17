---
name: qa-verify-execution
description: Final verification that ALL QA skills and rules were executed (Level 2)
version: 1.0.0
author: QA Team
tags: [qa, verification, level-2, mandatory, final]
has_python_tool: true
tools: [Read]
---

# qa-verify-execution (Level 2)

## Agent Identity
- **Name:** Execution Verifier
- **Role:** Verify complete QA coverage
- **Level:** 2 (Worker Skill - Final Phase)
- **Parent:** qa-super (Level 0)

## Coordination

### Reports To
- qa-super (Level 0 orchestrator)

### Reads
- qa_setup.json (expected families and rules)
- qa-execution.log (actual execution log)

### Output
- Verification report (pass/fail)

## Mission Statement

**CRITICAL:** This skill MUST run as the LAST skill in every qa-super execution.
It verifies that ALL enabled families and ALL enabled rules were actually executed.

If any family or rule was skipped, this skill reports a CRITICAL error.

## Python Tool Integration

```python
from qa_engine.infrastructure.execution_logger import ExecutionLogger
from qa_engine.shared.config import ConfigManager

logger = ExecutionLogger.get_instance()
config = ConfigManager()
config.load(Path("config/qa_setup.json"))

# Get expected families and rules
expected_families = config.get_list("enabled_families")
expected_rules = {}
for family in expected_families:
    family_config = config.get(f"families.{family}")
    if family_config and "rules" in family_config:
        enabled_rules = [
            rule for rule, cfg in family_config["rules"].items()
            if cfg.get("enabled", True)
        ]
        expected_rules[family] = enabled_rules

# Verify execution
report = logger.get_verification_report(expected_families, expected_rules)
```

## Verification Checks

| Check | Description | Severity |
|-------|-------------|----------|
| All families executed | Every enabled family was invoked | CRITICAL |
| All detectors run | Every enabled detector skill executed | CRITICAL |
| All rules applied | Every enabled rule was checked | CRITICAL |
| Mandatory rules | All mandatory rules (copyright, etc.) | CRITICAL |
| No shallow detection | Python detectors actually ran | CRITICAL |

## Output Format

### Success
```json
{
  "verification_passed": true,
  "run_id": "qa-run-123",
  "families_executed": ["BiDi", "code", "table", ...],
  "total_skills_executed": 45,
  "total_rules_executed": 120,
  "total_issues_found": 23
}
```

### Failure
```json
{
  "verification_passed": false,
  "run_id": "qa-run-123",
  "families_missing": ["infra"],
  "rules_missing": {
    "coverpage": ["cover-numbers-unwrapped", "cover-copyright-missing"]
  },
  "error": "CRITICAL: 3 rules were not executed"
}
```

## Enforcement

When verification fails:
1. Report is marked as INCOMPLETE
2. QA-REPORT.md includes WARNING header
3. User is notified of skipped checks
4. Exit code is non-zero

## Workflow Position

```
qa-super
├── Phase 1: Pre-compilation (all families parallel)
│   ├── qa-BiDi → qa-BiDi-detect → rules...
│   ├── qa-code → qa-code-detect → rules...
│   ├── qa-coverpage → qa-coverpage-detect → ALL 9 RULES
│   └── ...
├── Phase 2: Compilation
├── Phase 3: Post-compilation
└── Phase 4: VERIFICATION (THIS SKILL - ALWAYS LAST)
    └── qa-verify-execution
        ├── Load execution log
        ├── Compare against expected
        ├── Report any gaps
        └── FAIL if incomplete
```

## Version History
- **v1.0.0** (2025-12-28): Initial creation for complete QA coverage

---

**Parent:** qa-super
**Children:** None
**Coordination:** Final verification - runs after ALL other skills
