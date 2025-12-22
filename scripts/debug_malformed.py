"""Debug malformed citation fix."""

import sys
import io
import re
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from qa_engine.infrastructure.detection import BibDetector

# Test file
test_file = Path(__file__).parent.parent / "test-data" / "CLS-examples" / "examples" / "advanced_example.tex"
content = test_file.read_text(encoding="utf-8", errors="replace")
lines = content.split("\n")

print("=" * 60)
print("DEBUG MALFORMED CITATION KEYS")
print("=" * 60)

# Run detection
detector = BibDetector()
issues = detector.detect(content, str(test_file))

# Filter to malformed
malformed = [i for i in issues if i.rule == "bib-malformed-cite-key"]
print(f"\nFound {len(malformed)} malformed citation issues:")

for issue in malformed[:5]:
    print(f"\n  Line {issue.line}: '{issue.content}'")
    if 1 <= issue.line <= len(lines):
        print(f"  Full line: {lines[issue.line - 1][:150]}...")

# Test the fixer regex
print("\n" + "=" * 60)
print("TESTING FIXER REGEX")
print("=" * 60)

test_lines = [
    r"\cite{hebrew_nlp_\hebyear{2023},hebrew_linguistics_2022}",
    r"\cite{hebrew_nlp_2023,\en{hebrew}_\en{linguistics}_2022}",
    r"\cite[p. 15]{bert_paper_\hebyear{2018}}",
]

def clean_cite_key(m):
    prefix = m.group(1) if m.group(1) else ""
    keys = m.group(2)
    cleaned = re.sub(r"\\hebyear\{([^}]*)\}", r"\1", keys)
    cleaned = re.sub(r"\\en\{([^}]*)\}", r"\1", cleaned)
    cleaned = re.sub(r"\\num\{([^}]*)\}", r"\1", cleaned)
    return f"\\cite{prefix}{{{cleaned}}}"

pattern = r"\\cite(\[[^\]]*\])?\{([^}]*\\(?:hebyear|en|num|percent|textenglish)\{[^}]*\}[^}]*)\}"

for line in test_lines:
    print(f"\nBefore: {line}")
    fixed = re.sub(pattern, clean_cite_key, line)
    print(f"After:  {fixed}")
