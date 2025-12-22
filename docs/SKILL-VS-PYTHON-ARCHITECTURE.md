# QA Skill Mechanism Architecture

## Overview: What is Done by LLM vs Python Tool

The QA system uses a **hybrid architecture** where:
- **LLM (Claude)**: Orchestration, decision-making, context understanding
- **Python Tools**: Deterministic, repeatable detection and fixing

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        LLM (Claude)                              │
│  - Invokes skills                                                │
│  - Interprets results                                            │
│  - Makes decisions                                               │
│  - Formats output                                                │
└─────────────────────────┬───────────────────────────────────────┘
                          │ Invokes
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Skill (skill.md)                              │
│  - Defines role & mission                                        │
│  - Specifies Python tool integration                            │
│  - Documents rules                                               │
└─────────────────────────┬───────────────────────────────────────┘
                          │ Calls
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Tool (tool.py)                                │
│  - Entry point for LLM                                          │
│  - Wraps Python module                                          │
│  - Returns structured data                                       │
└─────────────────────────┬───────────────────────────────────────┘
                          │ Uses
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│              Python Module (qa_engine/...)                       │
│  - Deterministic regex-based detection                          │
│  - Rule definitions                                              │
│  - Pattern matching                                              │
│  - 100% repeatable results                                       │
└─────────────────────────────────────────────────────────────────┘
```

## qa-bib-detect Skill Breakdown

### Files Structure

```
.claude/skills/qa-bib-detect/
├── skill.md          # Skill definition (for LLM)
└── tool.py           # Python entry point

src/qa_engine/infrastructure/detection/
├── bib_detector.py   # Actual detection logic
└── bib_rules.py      # Rule definitions
```

### What LLM Does (skill.md)

1. **Receives request** from parent orchestrator (qa-bib)
2. **Invokes Python tool** via tool.py
3. **Interprets results** returned by Python
4. **Formats output** for parent/user
5. **Makes decisions** based on results

### What Python Tool Does (tool.py + bib_detector.py)

1. **Reads file content** (if not provided)
2. **Applies regex patterns** to detect issues
3. **Loads .bib files** to check defined entries
4. **Returns structured list** of issues

## Complete Skill Inventory

### Level 0: Super Orchestrator
| Skill | Python Tool | Description |
|-------|-------------|-------------|
| qa-super | ✗ | Coordinates all QA families |

### Level 1: Family Orchestrators
| Skill | Python Tool | Description |
|-------|-------------|-------------|
| qa-bib | ✗ | Bibliography family orchestrator |
| qa-BiDi | ✗ | BiDi text family orchestrator |
| qa-code | ✗ | Code block family orchestrator |
| qa-table | ✗ | Table family orchestrator |
| qa-typeset | ✗ | Typesetting family orchestrator |
| qa-infra | ✗ | Infrastructure family orchestrator |
| qa-cls-version | ✗ | CLS version family orchestrator |

### Level 2: Detection Skills
| Skill | Python Tool | Module |
|-------|-------------|--------|
| qa-bib-detect | ✓ tool.py | `bib_detector.BibDetector` |
| qa-BiDi-detect | ✓ tool.py | `bidi_detector.BiDiDetector` |
| qa-code-detect | ✓ tool.py | `code_detector.CodeDetector` |
| qa-table-detect | ✓ tool.py | `table_detector.TableDetector` |
| qa-typeset-detect | ✓ tool.py | `typeset_detector.TypesetDetector` |
| qa-cls-version-detect | ✓ tool.py | CLS version check |
| qa-infra-subfiles-detect | ✓ tool.py | Subfiles check |

### Level 2: Fix Skills
| Skill | Python Tool | Module |
|-------|-------------|--------|
| qa-bib-fix | ✓ tool.py | `bib_fixer.BibFixer` |
| qa-BiDi-fix-text | ✓ tool.py | `bidi_fixer.BiDiFixer` |
| qa-code-fix-background | ✓ tool.py | `code_fixer.CodeFixer` |
| qa-code-fix-encoding | ✓ tool.py | `code_fixer.CodeFixer` |
| qa-table-fix | ✓ tool.py | `table_fixer.TableFixer` |
| qa-cls-version-fix | ✓ tool.py | CLS update |

## LLM vs Python Responsibilities

### LLM Responsibilities (Non-Deterministic)
- Understanding user intent
- Deciding which skills to run
- Interpreting complex results
- Providing explanations
- Handling edge cases not covered by rules
- Orchestrating multi-step workflows

### Python Tool Responsibilities (Deterministic)
- Regex-based pattern matching
- File I/O operations
- Rule application
- Structured data return
- Repeatable detection
- Consistent fixing

## Example: qa-bib-detect Flow

```
User Request: "Check bibliography issues"
       │
       ▼
┌──────────────────────────────────────┐
│ LLM: Understands request             │
│      Decides to invoke qa-bib-detect │
└──────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ Skill: qa-bib-detect invoked         │
│        Calls tool.py                  │
└──────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ tool.py:                             │
│   detector = BibDetector()           │
│   issues = detector.detect(content)  │
│   return [issue.to_dict() for ...]   │
└──────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ BibDetector (Python):                │
│   - Apply 6 regex rules              │
│   - Check .bib file existence        │
│   - Match citation keys              │
│   - Return Issue objects             │
└──────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ LLM: Receives structured results     │
│      Formats for user                │
│      Suggests next steps             │
└──────────────────────────────────────┘
```

## Verification Results

Running both methods on `advanced_example.tex`:

| Method | Issues Found | Identical |
|--------|--------------|-----------|
| Skill tool.py | 0 | ✓ |
| Direct Python | 0 | ✓ |

**Both methods produce identical results** because:
1. `tool.py` simply wraps `BibDetector`
2. All logic is in Python (deterministic)
3. LLM only handles orchestration

## Key Principle

> **"Python for the HOW, LLM for the WHY"**
>
> - Python tools handle *how* to detect/fix (deterministic regex)
> - LLM handles *why* and *when* to run (intelligent orchestration)
