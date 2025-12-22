---
name: upgrade-bc-qa
description: Analyze BC-QA gaps and upgrade BC skills to comply with QA rules
arguments:
  - name: issues
    description: Issue ID(s) or comma-separated list (e.g., "BIDI-001" or "BIDI-001,CODE-002")
    required: true
---

# Upgrade BC Skills from QA Issues

Analyze gaps between BC (Book Creator) content generation and QA mechanism expectations.
Upgrade BC skills to produce QA-compliant LaTeX content from the start.

## Issues to Analyze
$ARGUMENTS

## Ground Truth
- **QA mechanisms** are ground truth (DO NOT MODIFY)
- **CLS class file** is ground truth (DO NOT MODIFY - ask user if changes needed)
- **BC skills** must be upgraded to comply with QA rules

## Execution Flow

### Phase 1: Load Issue Mapping
```python
import sys
sys.path.insert(0, "src")

from qa_engine.bc.upgrader import BCQAUpgrader

upgrader = BCQAUpgrader()
issues = upgrader.parse_issues("$ARGUMENTS")
print(f"Analyzing {len(issues)} issue(s): {issues}")
```

### Phase 2: Extract Relevant QA Rules
For each issue, identify which QA detection rules are violated:

```python
qa_rules = upgrader.get_qa_rules_for_issues(issues)
print(upgrader.format_rules_report(qa_rules))
```

### Phase 3: Map BC Skills to Issues
Identify which BC skills generate content that triggers these issues:

```python
bc_mapping = upgrader.map_bc_skills_to_issues(issues)
print(upgrader.format_bc_mapping_report(bc_mapping))
```

### Phase 4: Generate Upgrade Plan
Create upgrade plan for each affected BC skill:

```python
upgrade_plan = upgrader.create_upgrade_plan(bc_mapping, qa_rules)
print(upgrader.format_upgrade_plan(upgrade_plan))
```

### Phase 5: Apply Upgrades
Update BC skill configurations and templates:

```python
results = upgrader.apply_upgrades(upgrade_plan)
print(upgrader.format_results(results))
```

### Phase 6: Validate Changes
Run QA validation on sample content to verify fixes:

```python
validation = upgrader.validate_upgrades(results)
print(upgrader.format_validation_report(validation))
```

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                    UPGRADE-BC-QA COMMAND                            │
└─────────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│ Issue Parser  │     │ QA Rule       │     │ BC Skill      │
│ (Python)      │     │ Extractor     │     │ Analyzer      │
│               │     │ (Python)      │     │ (Python)      │
└───────────────┘     └───────────────┘     └───────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
                 ┌─────────────────────────┐
                 │   Gap Analyzer          │
                 │   (Maps issues to BC    │
                 │    skills & QA rules)   │
                 └─────────────────────────┘
                              │
                              ▼
                 ┌─────────────────────────┐
                 │   BC Skill Upgrader     │
                 │   - Update templates    │
                 │   - Update config       │
                 │   - Update validators   │
                 └─────────────────────────┘
                              │
                              ▼
                 ┌─────────────────────────┐
                 │   Validation Gate       │
                 │   (Verify QA passes)    │
                 └─────────────────────────┘
```

## Issue Categories

| Category | Prefix | QA Family | BC Skills Affected |
|----------|--------|-----------|-------------------|
| BiDi | BIDI-* | qa-BiDi | bc-content, bc-math, bc-code |
| Code | CODE-* | qa-code | bc-code |
| Table | TABLE-* | qa-table | bc-academic-source |
| Bibliography | BIB-* | qa-bib | bc-source-research, bc-academic-source |
| Image | IMG-* | qa-img | bc-content |
| Typeset | TYPE-* | qa-typeset | All BC skills |

## Output Files

- **BC-UPGRADE-REPORT.md**: Summary of changes made
- **bc_pipeline.json**: Updated configuration (if modified)
- **Skill files**: Updated skill.md files with new rules

## Important Notes

1. **Minimum LLM tokens**: All analysis done via Python tools
2. **No code duplication**: OOP architecture with shared base classes
3. **No hardcoded data**: All mappings loaded from config files
4. **CLS is read-only**: If CLS changes needed, report to user
5. **One issue may break multiple rules**: All relevant rules identified
