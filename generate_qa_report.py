"""Generate comprehensive QA report for Chapter 08."""
from pathlib import Path
from src.qa_engine.infrastructure.super_orchestrator import SuperOrchestrator
from src.qa_engine.infrastructure.detection.bidi_detector import BiDiDetector
from src.qa_engine.infrastructure.detection.code_detector import CodeDetector
from src.qa_engine.infrastructure.detection.table_detector import TableDetector
from src.qa_engine.bibliography.detection.bib_detector import BibDetector
from datetime import datetime
import re

# Project paths
project_path = Path(r'C:\25D\GeneralLearning\skill-python-base\test-data\runi-25-26-final-project-description')
chapter_path = project_path / 'chapters' / 'chapter08.tex'
content = chapter_path.read_text(encoding='utf-8')
file_path = str(chapter_path)

# Run all detectors
bidi = BiDiDetector()
code = CodeDetector()
table = TableDetector()
bib = BibDetector()

bidi_issues = bidi.detect(content, file_path)
code_issues = code.detect(content, file_path)
table_issues = table.detect(content, file_path)
bib_result = bib.detect_in_project(project_path)

# Get structure info
labels = re.findall(r'\\label\{([^}]+)\}', content)
refs = re.findall(r'\\ref\{([^}]+)\}', content)
tikz_count = len(re.findall(r'\\begin\{tikzpicture\}', content))
table_count = len(re.findall(r'\\begin\{hebrewtable\}', content))
code_count = len(re.findall(r'\\begin\{pythonbox\*?\}', content))
lines = content.count('\n') + 1
chars = len(content)

# Print comprehensive summary
print('CHAPTER 08 QA SUMMARY')
print('=' * 50)
print(f'File: {chapter_path}')
print(f'Lines: {lines}')
print(f'Characters: {chars}')
print()
print('STRUCTURE:')
print(f'  Labels defined: {len(labels)}')
print(f'  References used: {len(refs)}')
print(f'  TikZ diagrams: {tikz_count}')
print(f'  Tables: {table_count}')
print(f'  Code blocks: {code_count}')
print()
print('ISSUES DETECTED:')
print(f'  BiDi issues: {len(bidi_issues)}')
print(f'  Code issues: {len(code_issues)}')
print(f'  Table issues: {len(table_issues)}')
print(f'  Bibliography issues (project-wide): {len(bib_result.issues)}')
print()
print('BIBLIOGRAPHY:')
print(f'  Total citations (project): {bib_result.citations_total}')
print(f'  Unique keys: {len(bib_result.citations_unique)}')
print(f'  Missing entries: {len(bib_result.missing_entries)}')
print(f'  Has printbibliography: {bib_result.has_printbib}')
print()
print('DETAILED ISSUES:')
print()
print('BiDi Issues:')
for issue in bidi_issues[:5]:
    print(f'  Line {issue.line}: {issue.rule} - {issue.content[:40]}')
if len(bidi_issues) > 5:
    print(f'  ... and {len(bidi_issues) - 5} more')
print()
print('Code Issues:')
for issue in code_issues[:5]:
    print(f'  Line {issue.line}: {issue.rule}')
if len(code_issues) > 5:
    print(f'  ... and {len(code_issues) - 5} more')
print()
print('Table Issues:')
for issue in table_issues[:5]:
    print(f'  Line {issue.line}: {issue.rule}')
if len(table_issues) > 5:
    print(f'  ... and {len(table_issues) - 5} more')
