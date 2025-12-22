"""Bibliography fixer for LaTeX documents."""
from __future__ import annotations
import re
from pathlib import Path
from typing import Dict, List, Set
from ...domain.interfaces import FixerInterface
from ...domain.models.issue import Issue


class BibFixer(FixerInterface):
    """Fixes bibliography issues: missing .bib files, undefined citations."""

    def fix(self, content: str, issues: List[Issue]) -> str:
        """Apply fixes - clean up malformed citation keys."""
        result = content
        for issue in [i for i in issues if i.rule == "bib-malformed-cite-key"]:
            result = self._fix_malformed_cite(result, issue)
        return result

    def _fix_malformed_cite(self, content: str, issue: Issue) -> str:
        """Fix a malformed citation key by removing LaTeX commands."""
        lines = content.split("\n")
        if issue.line < 1 or issue.line > len(lines):
            return content
        lines[issue.line - 1] = self._clean_all_cite_commands(lines[issue.line - 1])
        return "\n".join(lines)

    def _clean_all_cite_commands(self, line: str) -> str:
        """Clean all citation commands on a line by removing embedded LaTeX."""
        result, cite_pattern, pos = line, re.compile(r"\\cite(\[[^\]]*\])?\{"), 0
        while pos < len(result):
            match = cite_pattern.search(result, pos)
            if not match:
                break
            start, depth, i = match.end(), 1, match.end()
            while i < len(result) and depth > 0:
                if result[i] == "{": depth += 1
                elif result[i] == "}": depth -= 1
                i += 1
            if depth == 0:
                cite_content = result[start:i - 1]
                cleaned = self._clean_latex_from_key(cite_content)
                if cleaned != cite_content:
                    result = result[:start] + cleaned + result[i - 1:]
                    pos = start + len(cleaned) + 1
                else:
                    pos = i
            else:
                pos = match.end()
        return result

    def _clean_latex_from_key(self, keys: str) -> str:
        """Remove LaTeX wrapper commands from citation keys."""
        result, patterns = keys, [r"\\hebyear", r"\\en", r"\\num", r"\\percent", r"\\textenglish"]
        for _ in range(10):  # Max iterations to prevent infinite loop
            prev = result
            for p in patterns:
                result = re.sub(p + r"\{([^}]*)\}", r"\1", result)
            if result == prev:
                break
        return result

    def fix_with_context(self, content: str, issues: List[Issue], file_path: str) -> str:
        """Fix with file path context to create .bib files."""
        base_dir, undefined_cites, bib_files = Path(file_path).parent, set(), set()
        for issue in issues:
            if issue.rule == "bib-undefined-cite":
                undefined_cites.update(self._parse_cite_keys(issue.content))
            elif issue.rule == "bib-missing-file":
                bib_files.add(issue.content)
        for bib_file in bib_files:
            bib_path = base_dir / bib_file
            self._create_bib_file(bib_path.with_suffix(".bib") if not bib_path.suffix else bib_path, undefined_cites)
        if undefined_cites and not bib_files:
            self._create_bib_file(base_dir / "references.bib", undefined_cites)
        return content

    def _parse_cite_keys(self, content: str) -> Set[str]:
        """Extract citation keys from issue content."""
        match = re.search(r"\\cite\{([^}]+)\}", content)
        if match:
            return {k.strip() for k in match.group(1).split(",")}
        if "'" in content and (match := re.search(r"'([^']+)'", content)):
            return {k.strip() for k in match.group(1).split(",")}
        raw_key = self._clean_latex_from_key(content.strip())
        return {k.strip() for k in raw_key.split(",")} if raw_key else set()

    def _create_bib_file(self, bib_path: Path, citations: Set[str]) -> None:
        """Create or update .bib file with placeholder entries."""
        existing_content = bib_path.read_text(encoding="utf-8") if bib_path.exists() else ""
        existing_entries = set(re.findall(r"@\w+\{(\w+),", existing_content))
        new_entries = [self._generate_bib_entry(k) for k in sorted(citations) if k not in existing_entries]
        if new_entries:
            full_content = existing_content + ("" if existing_content.endswith("\n") else "\n" if existing_content else "")
            bib_path.write_text(full_content + "\n".join(new_entries) + "\n", encoding="utf-8")

    def _generate_bib_entry(self, cite_key: str) -> str:
        """Generate placeholder BibTeX entry."""
        author, year = "Author", "2024"
        title = cite_key.replace("_", " ").replace("-", " ").title()
        if (year_match := re.search(r"(\d{4})", cite_key)):
            year, title = year_match.group(1), re.sub(r"\d{4}", "", title).strip()
        if (name_match := re.match(r"([a-zA-Z]+)", cite_key)):
            author = name_match.group(1).title()
        return (f"@article{{{cite_key},\n  author = {{{author}}},\n  title = {{{title}}},\n"
                f"  journal = {{Journal Name}},\n  year = {{{year}}},\n"
                f"  note = {{Placeholder entry - update with actual reference}}\n}}")

    def get_patterns(self) -> Dict[str, Dict[str, str]]:
        """Return fix patterns."""
        return {"create-bib": {"find": r"\\addbibresource\{([^}]+)\}",
                              "replace": "Create .bib file", "description": "Create missing .bib file"}}
