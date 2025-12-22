"""
Bibliography fixer for LaTeX documents.

Implements qa-bib-fix-missing skill.md v1.0 - fixes missing entries and commands.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..detection.bib_models import BibDetectResult, BibFixResult, BibIssueType


class BibFixer:
    """
    Fixes bibliography issues in LaTeX documents.

    Aligned with qa-bib-fix-missing skill.md v1.0:
    - Fix 1: Missing bibliography entry
    - Fix 2: Missing print command
    - Fix 3: Missing TOC entry
    - Fix 4: Empty bibliography (filter issue)
    """

    # Entry templates
    ENTRY_TEMPLATES = {
        "misc": '''@misc{{{key},
  author    = {{TODO: Add author}},
  title     = {{TODO: Add title for {key}}},
  year      = {{YYYY}},
  note      = {{PLACEHOLDER - Auto-generated for missing citation}},
  keywords  = {{english}}
}}''',
        "article": '''@article{{{key},
  author    = {{LastName, FirstName and LastName2, FirstName2}},
  title     = {{Article Title}},
  journal   = {{Journal Name}},
  volume    = {{X}},
  number    = {{Y}},
  pages     = {{1--10}},
  year      = {{YYYY}},
  doi       = {{10.xxxx/xxxxx}},
  keywords  = {{english}}
}}''',
        "book": '''@book{{{key},
  author    = {{LastName, FirstName}},
  title     = {{Book Title}},
  publisher = {{Publisher Name}},
  year      = {{YYYY}},
  isbn      = {{XXX-X-XXX-XXXXX-X}},
  keywords  = {{english}}
}}''',
        "inproceedings": '''@inproceedings{{{key},
  author    = {{LastName, FirstName}},
  title     = {{Paper Title}},
  booktitle = {{Proceedings of Conference Name}},
  pages     = {{1--10}},
  year      = {{YYYY}},
  publisher = {{Publisher}},
  doi       = {{10.xxxx/xxxxx}},
  keywords  = {{english}}
}}'''
    }

    # Print bibliography templates
    PRINTBIB_HEBREW = '''
% ======== Bibliography ========
\\newpage
\\printenglishbibliography
'''

    PRINTBIB_STANDARD = '''
% ======== Bibliography ========
\\newpage
\\printbibliography[heading=bibintoc,title={References}]
'''

    def add_missing_entry(self, bib_content: str, key: str,
                          entry_type: str = "misc") -> Tuple[str, Dict[str, Any]]:
        """Add a placeholder entry for a missing citation key."""
        template = self.ENTRY_TEMPLATES.get(entry_type, self.ENTRY_TEMPLATES["misc"])
        new_entry = template.format(key=key)

        # Add to end of bib content
        updated = bib_content.rstrip() + "\n\n" + new_entry + "\n"

        fix_info = {
            "type": "added_entry",
            "key": key,
            "entry_type": entry_type,
            "note": "Placeholder entry - requires manual completion"
        }
        return updated, fix_info

    def add_printbibliography(self, tex_content: str,
                               is_hebrew: bool = True) -> Tuple[str, Dict[str, Any]]:
        """Add printbibliography command before \\end{document}."""
        template = self.PRINTBIB_HEBREW if is_hebrew else self.PRINTBIB_STANDARD

        # Find \end{document}
        match = re.search(r"(\\end\{document\})", tex_content)
        if not match:
            return tex_content, {}

        # Insert before \end{document}
        insert_pos = match.start()
        updated = tex_content[:insert_pos] + template + tex_content[insert_pos:]

        fix_info = {
            "type": "added_printbib",
            "template": "hebrew" if is_hebrew else "standard",
            "note": "Added bibliography section"
        }
        return updated, fix_info

    def add_toc_entry(self, tex_content: str,
                       method: str = "bibintoc") -> Tuple[str, Dict[str, Any]]:
        """Add bibliography to table of contents."""
        if method == "bibintoc":
            # Change \printbibliography to include bibintoc
            updated = re.sub(
                r"\\printbibliography(?!\[)",
                r"\\printbibliography[heading=bibintoc,title={References}]",
                tex_content
            )
            # Also handle existing options
            if updated == tex_content:
                updated = re.sub(
                    r"\\printbibliography\[([^\]]+)\]",
                    r"\\printbibliography[heading=bibintoc,\1]",
                    tex_content
                )
        else:
            # Add manual TOC entry before \printbibliography
            updated = re.sub(
                r"(\\printbibliography)",
                r"\\phantomsection\n\\addcontentsline{toc}{section}{References}\n\1",
                tex_content
            )

        fix_info = {
            "type": "added_toc_entry",
            "method": method,
            "note": "Added bibliography to table of contents"
        }
        return updated, fix_info

    def add_english_wrapper(self, tex_content: str) -> Tuple[str, Dict[str, Any]]:
        """Wrap printbibliography in English environment."""
        # Find printbibliography and wrap it
        pattern = r"(\\printbibliography(?:\[[^\]]*\])?)"
        replacement = r"\\begin{english}\n\1\n\\end{english}"
        updated = re.sub(pattern, replacement, tex_content)

        fix_info = {
            "type": "added_english_wrapper",
            "note": "Wrapped bibliography in English environment for RTL documents"
        }
        return updated, fix_info

    def add_bibitemsep(self, tex_content: str,
                        spacing: str = "0.5\\baselineskip") -> Tuple[str, Dict[str, Any]]:
        """Add bibitemsep setting before printbibliography."""
        setting = f"\\setlength{{\\bibitemsep}}{{{spacing}}}\n"
        # Use lambda to avoid regex interpretation of backslashes in setting
        updated = re.sub(
            r"(\\printbibliography)",
            lambda m: setting + m.group(1),
            tex_content
        )

        fix_info = {
            "type": "added_bibitemsep",
            "spacing": spacing,
            "note": "Set bibliography item spacing"
        }
        return updated, fix_info

    def add_keyword_to_entry(self, bib_content: str, key: str,
                              keyword: str = "english") -> Tuple[str, Dict[str, Any]]:
        """Add keyword field to a bibliography entry."""
        # Find the entry
        pattern = rf"(@\w+\{{{key},.*?)\n\}}"
        match = re.search(pattern, bib_content, re.DOTALL)
        if not match:
            return bib_content, {}

        # Check if keywords already exists
        entry = match.group(0)
        if "keywords" in entry.lower():
            return bib_content, {}

        # Add keywords before closing brace
        new_entry = entry[:-1] + f",\n  keywords  = {{{keyword}}}\n}}"
        updated = bib_content[:match.start()] + new_entry + bib_content[match.end():]

        fix_info = {
            "type": "added_keyword",
            "key": key,
            "keyword": keyword,
            "note": f"Added keywords={keyword} to entry"
        }
        return updated, fix_info

    def fix_from_detect_result(self, detect_result: BibDetectResult,
                                tex_content: str = "",
                                bib_content: str = "") -> Tuple[str, str, BibFixResult]:
        """Apply fixes based on detection result."""
        result = BibFixResult()
        updated_tex = tex_content
        updated_bib = bib_content

        for issue in detect_result.issues:
            if issue.type == BibIssueType.MISSING_ENTRY and issue.key:
                updated_bib, fix = self.add_missing_entry(updated_bib, issue.key)
                if fix:
                    fix["file"] = detect_result.bib_file
                    result.fixes_applied.append(fix)
                    result.manual_actions.append(
                        f"Complete placeholder entry for {issue.key} with correct metadata"
                    )

            elif issue.type == BibIssueType.MISSING_PRINTBIB:
                updated_tex, fix = self.add_printbibliography(updated_tex)
                if fix:
                    result.fixes_applied.append(fix)

            elif issue.type == BibIssueType.NOT_IN_TOC:
                updated_tex, fix = self.add_toc_entry(updated_tex)
                if fix:
                    result.fixes_applied.append(fix)

            elif issue.type == BibIssueType.NOT_IN_ENGLISH:
                updated_tex, fix = self.add_english_wrapper(updated_tex)
                if fix:
                    result.fixes_applied.append(fix)

        if result.fixes_applied:
            result.recompile_needed = True

        return updated_tex, updated_bib, result

    def get_entry_templates(self) -> Dict[str, str]:
        """Return all entry templates."""
        return self.ENTRY_TEMPLATES.copy()

    def to_dict(self, result: BibFixResult) -> Dict:
        """Convert result to dictionary matching skill.md output format."""
        return {
            "skill": "qa-bib-fix-missing",
            "status": result.status,
            "fixes_applied": result.fixes_applied,
            "manual_actions_required": result.manual_actions,
            "verification": {
                "recompile_needed": result.recompile_needed,
                "passes_required": result.passes_required
            }
        }
