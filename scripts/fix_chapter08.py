"""Fix chapter08.tex corruption."""
import re
from pathlib import Path

file_path = Path("test-data/GenAI-Security-Cheat-Sheet-2025-2026/chapters/chapter08.tex")
content = file_path.read_text(encoding="utf-8")

def fix_pythonbox_line(line):
    """Fix a corrupted pythonbox line."""
    if 'exthebrew' not in line:
        return line

    # Extract all Hebrew words
    hebrew_words = re.findall(r'[\u0590-\u05FF]+', line)
    # Extract English words in \en{}
    en_pattern = r'\\en\{([^}]+)\}'
    english_words = re.findall(en_pattern, line)

    # Build clean title with Hebrew words
    title_text = ' '.join(hebrew_words)

    # Add English parts if present
    for en in english_words:
        title_text += f' \\en{{{en}}}'

    # Determine box type
    if 'pythonbox' in line:
        return f'\\begin{{pythonbox}}[title={{\\texthebrew{{{title_text}}}}}]'
    elif 'defensebox' in line:
        return f'\\begin{{defensebox}}[title={{\\texthebrew{{{title_text}}}}}]'
    elif 'casestudy' in line:
        return f'\\begin{{casestudy}}[title={{\\texthebrew{{{title_text}}}}}]'

    return line

lines = content.split('\n')
fixed_lines = []
for line in lines:
    if 'exthebrew' in line:
        fixed_lines.append(fix_pythonbox_line(line))
    else:
        fixed_lines.append(line)

content = '\n'.join(fixed_lines)

# Also remove duplicate \begin{english} lines
content = re.sub(r'(\\begin\{english\}\n)+', r'\\begin{english}\n', content)

file_path.write_text(content, encoding='utf-8')
print("Fixed chapter08.tex")

# Verify
content = file_path.read_text(encoding='utf-8')
if 'exthebrew' in content:
    print("WARNING: Still has exthebrew patterns")
    for i, line in enumerate(content.split('\n'), 1):
        if 'exthebrew' in line:
            print(f"  Line {i}: {line[:80]}...")
else:
    print("SUCCESS: No more exthebrew patterns")
