# BC Mechanism (Book Creator)

## Overview

The **Book Creator (BC)** mechanism is an AI-assisted content generation system for Hebrew-English academic LaTeX documents. It works alongside the QA mechanism to ensure generated content passes all quality checks.

## Three-Stage Pipeline

### Stage 1: Research
- `bc-source-research` - Parallel source collection, filtering, BibTeX preparation
- `bc-research` - Deep research on specific topics

### Stage 2: Content Generation
- `bc-code` - Python, NumPy, MCP code examples with LaTeX formatting
- `bc-math` - Technical accuracy, mathematical rigor, AI/ML theory
- `bc-academic-source` - IEEE format citations, bibliography management

### Stage 3: Review & Polish
- `bc-architect` - Narrative flow, philosophical context, final style review
- `bc-hebrew` - Academy standard Hebrew copyediting, terminology

## BC Skills Hierarchy

```
bc-super (Level 0)
├── bc-architect (Level 1) - Chief Architect & Strategic Reviewer
├── bc-research (Level 1) - Research Coordinator
│   └── bc-source-research (Level 2) - Source Research Agent
├── bc-content (Level 1) - Content Coordinator
│   ├── bc-code (Level 2) - Code Implementation Specialist
│   ├── bc-math (Level 2) - Lead Technologist & Math Reviewer
│   └── bc-academic-source (Level 2) - Academic Source Specialist
├── bc-hebrew (Level 1) - Hebrew Language Editor
└── bc-drawing (Level 1) - Drawing & Visualization Agent
```

## QA Integration

BC skills are validated against QA rules **before** writing content:

```
[BC Content Generation] → [QA Validation] → [Write to File]
                              ↓
                         [Fix Issues]
                              ↓
                         [Re-validate]
```

This ensures "Write Once, Pass Always" - content is correct when first written.

## Using BC Skills

### From Claude CLI (Local Project)
```bash
cd /path/to/skill-python-base
claude

# In Claude CLI:
/bc-super "Write a chapter on neural networks"
```

### As Global Skills
BC skills can be migrated to global location:
```powershell
# Copy to global location
Copy-Item -Path ".\.claude\skills\bc-*" -Destination "$env:USERPROFILE\.claude\skills\" -Recurse

# Ensure Python tools can import qa_engine
pip install -e C:\path\to\skill-python-base
```

## Configuration

BC pipeline is configured in `config/bc_pipeline.json`:

```json
{
  "stages": [
    {"name": "research", "skills": ["bc-source-research"], "parallel": true},
    {"name": "content", "skills": ["bc-code", "bc-math"], "parallel": true},
    {"name": "review", "skills": ["bc-architect", "bc-hebrew"], "parallel": false}
  ],
  "validators": ["qa-BiDi", "qa-code", "qa-bib"],
  "output_format": "latex"
}
```

## BC vs QA Comparison

| Aspect | QA Mechanism | BC Mechanism |
|--------|--------------|--------------|
| Purpose | Detect/Fix issues | Generate content |
| Input | Existing LaTeX | Topic/Outline |
| Output | Fixed LaTeX | New LaTeX |
| Python Tools | Detectors, Fixers | Templates, Validators |
| LLM Role | Complex decisions | Content generation |
