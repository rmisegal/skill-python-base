"""Run comprehensive QA analysis on Chapter 08."""
from pathlib import Path
import re

# Project paths
project_path = Path(r'C:\25D\GeneralLearning\skill-python-base\test-data\runi-25-26-final-project-description')
chapter_path = project_path / 'chapters' / 'chapter08.tex'
content = chapter_path.read_text(encoding='utf-8')

# Cross-reference check for chapter 08
print('=== CHAPTER 08 CROSS-REFERENCES ===')
labels = re.findall(r'\\label\{([^}]+)\}', content)
refs = re.findall(r'\\ref\{([^}]+)\}', content)
print(f'Labels defined ({len(labels)}):')
for label in labels:
    print(f'  - {label}')
print(f'References used ({len(refs)}):')
for ref in refs:
    print(f'  - {ref}')

# Check section structure
print('\n=== SECTION STRUCTURE ===')
sections = re.findall(r'\\(hebrew)?(section|subsection|subsubsection)\{([^}]+)\}', content)
print(f'Total sections: {len(sections)}')
for prefix, level, title in sections[:15]:
    cmd = f'\\{prefix}{level}' if prefix else f'\\{level}'
    print(f'  {cmd}: {title[:50]}')

# Check TikZ environments (need english wrapper)
print('\n=== TikZ ENVIRONMENTS ===')
tikz_matches = list(re.finditer(r'\\begin\{tikzpicture\}', content))
print(f'TikZ environments: {len(tikz_matches)}')

# Check hebrewtable environments
print('\n=== TABLE ENVIRONMENTS ===')
tables = re.findall(r'\\begin\{(hebrewtable|table)\}', content)
print(f'Table environments: {len(tables)}')

# Check pythonbox environments
print('\n=== CODE ENVIRONMENTS ===')
codeboxes = re.findall(r'\\begin\{pythonbox\*?\}', content)
print(f'pythonbox environments: {len(codeboxes)}')
