---
name: qa-cls-guard
description: Central CLS protection gate - all QA skills must call this before modifying CLS files
version: 1.0.0
author: QA Team
tags: [qa, cls, protection, gate, approval, level-2]
tools: [AskUserQuestion]
---

# QA CLS Guard (Level 2)

## Agent Identity
- **Name:** CLS Guard
- **Role:** Central gate for all CLS file modifications
- **Level:** 2 (Utility Skill)
- **Parent:** All QA orchestrators

## Purpose

This is the **SINGLE POINT OF CONTROL** for all CLS file modifications in the QA system.
Any QA skill that needs to modify a CLS file MUST call this guard first.

## How It Works

### When Called By a Fixer Skill:

1. **STOP** - Block the CLS modification
2. **COLLECT** information about the requested change:
   - Which CLS file(s) need modification
   - What changes are needed
   - Why the changes are needed
   - Which QA skill requested the change
3. **INFORM** the user with a clear message:
   ```
   CLS MODIFICATION REQUEST
   ========================
   Requesting Skill: [skill-name]
   File: [cls-file-path]

   Required Changes:
   [detailed description of changes needed]

   Reason:
   [why this change is needed]

   I am going to change the CLS file(s). Please approve before I start.
   ```
4. **WAIT** for explicit user approval
5. **RETURN** approval status to the calling skill

### Input Format

```json
{
  "requesting_skill": "qa-BiDi-fix-toc-config",
  "cls_file": "hebrew-academic-template.cls",
  "changes": [
    {
      "line": 651,
      "description": "Add \\textenglish wrapper to \\thechapter",
      "before": "\\renewcommand{\\thechapter}{\\arabic{chapter}}",
      "after": "\\renewcommand{\\thechapter}{\\textenglish{\\arabic{chapter}}}"
    }
  ],
  "reason": "Fix RTL number rendering in TOC"
}
```

### Output Format

```json
{
  "approved": true,
  "user_response": "Yes, proceed with CLS changes",
  "timestamp": "2025-12-22T10:30:00Z"
}
```

OR if not approved:

```json
{
  "approved": false,
  "user_response": "No, I will handle CLS changes manually",
  "changes_documented": true
}
```

## Integration Instructions

### For Fixer Skills (Level 2):

Add this line to your skill:
```
**CLS Guard:** Before modifying any .cls file, call `qa-cls-guard` for approval.
```

### For Orchestrators (Level 1):

Add this to your coordination section:
```
**CLS Policy:** Remind all child fixers to use `qa-cls-guard` before any CLS modifications.
```

## Usage Example

```python
# In any fixer skill that might need to modify CLS:

if file_path.endswith('.cls'):
    # Call CLS guard for approval
    approval = call_skill('qa-cls-guard', {
        'requesting_skill': 'qa-BiDi-fix-toc-config',
        'cls_file': file_path,
        'changes': changes_list,
        'reason': 'Fix TOC BiDi rendering'
    })

    if not approval['approved']:
        # Document changes for user and exit
        return {'status': 'BLOCKED', 'reason': 'User did not approve CLS changes'}

    # Only proceed if approved
    apply_changes(file_path, changes_list)
```

## Version History
- **v1.0.0** (2025-12-22): Initial creation as central CLS protection gate

---

**Type:** Utility Skill
**Called By:** All QA fixer skills that need CLS modifications
**Reports To:** User (direct approval workflow)
