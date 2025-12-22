"""Unit tests for Subfiles Chapter Fixer."""
import tempfile
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from qa_engine.infrastructure.fixing.subfiles_chapter_fixer import (
    SubfilesChapterFixer, SubfilesFixResult, FixRecord
)


class TestSubfilesChapterFixer:
    """Tests for SubfilesChapterFixer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.fixer = SubfilesChapterFixer(Path(self.temp_dir))
        (Path(self.temp_dir) / "chapters").mkdir()

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_chapter(self, name: str, content: str) -> Path:
        """Helper to create a chapter file."""
        path = Path(self.temp_dir) / "chapters" / name
        path.write_text(content, encoding="utf-8")
        return path

    def test_fix_adds_preamble_before_chapter(self):
        """Test Fix 1: Add preamble before \\chapter{}."""
        content = r"""% Chapter comments
\chapter{Test Chapter}
Some content here.
"""
        fixed = self.fixer.fix_content(content, ["missing-subfiles-documentclass", "missing-begin-document"])

        assert r"\documentclass[../main.tex]{subfiles}" in fixed
        assert r"\begin{document}" in fixed
        # Verify order: preamble before \chapter
        doc_pos = fixed.find(r"\documentclass")
        chap_pos = fixed.find(r"\chapter{")
        assert doc_pos < chap_pos

    def test_fix_adds_end_document(self):
        """Test Fix 2: Add \\end{document} at end."""
        content = r"""
\documentclass[../main.tex]{subfiles}
\begin{document}
\chapter{Test}
Content here.
"""
        fixed = self.fixer.fix_content(content, ["missing-end-document"])

        assert r"\end{document}" in fixed
        assert fixed.strip().endswith(r"\end{document}")

    def test_fix_all_three_missing(self):
        """Test fixing file missing all three elements."""
        content = r"""% Chapter 2
\chapter{Methods}
Content here.
"""
        rules = [
            "missing-subfiles-documentclass",
            "missing-begin-document",
            "missing-end-document"
        ]
        fixed = self.fixer.fix_content(content, rules)

        assert r"\documentclass[../main.tex]{subfiles}" in fixed
        assert r"\begin{document}" in fixed
        assert r"\end{document}" in fixed

    def test_preserves_header_comments(self):
        """Test that header comments are preserved."""
        content = r"""% פרק 2: שיטות
% This is a Hebrew chapter title
% More comments

\chapter{Methods}
Content.
"""
        fixed = self.fixer.fix_content(content, ["missing-subfiles-documentclass"])

        # Comments should still be at the beginning
        assert fixed.strip().startswith("%")
        assert "פרק 2" in fixed

    def test_creates_backup_file(self):
        """Test Step 1: Backup file is created."""
        content = r"\chapter{Test}"
        path = self._create_chapter("chapter-01.tex", content)

        issues = [{"file": "chapters/chapter-01.tex", "rule": "missing-subfiles-documentclass"}]
        result = self.fixer.fix_files(issues)

        backup_path = path.with_suffix(".tex.bak")
        assert backup_path.exists()
        assert "chapter-01.tex.bak" in result.files_fixed[0].backup

    def test_fix_file_records_applied_fixes(self):
        """Test that applied fixes are recorded."""
        content = r"\chapter{Test}"
        self._create_chapter("chapter-01.tex", content)

        issues = [
            {"file": "chapters/chapter-01.tex", "rule": "missing-subfiles-documentclass"},
            {"file": "chapters/chapter-01.tex", "rule": "missing-begin-document"},
            {"file": "chapters/chapter-01.tex", "rule": "missing-end-document"},
        ]
        result = self.fixer.fix_files(issues)

        fixes = result.files_fixed[0].fixes_applied
        assert "added-documentclass-subfiles" in fixes
        assert "added-begin-document" in fixes
        assert "added-end-document" in fixes

    def test_verify_fix_passes(self):
        """Test Step 4: Verification passes for properly fixed file."""
        content = r"""
\documentclass[../main.tex]{subfiles}
\begin{document}
\chapter{Test}
\end{document}
"""
        assert self.fixer._verify_fix(content) is True

    def test_verify_fix_fails_incomplete(self):
        """Test verification fails for incomplete fix."""
        content = r"""
\documentclass[../main.tex]{subfiles}
\chapter{Test}
"""
        assert self.fixer._verify_fix(content) is False

    def test_to_dict_output_format(self):
        """Test output matches skill.md JSON format."""
        content = r"\chapter{Test}"
        self._create_chapter("chapter.tex", content)

        issues = [{"file": "chapters/chapter.tex", "rule": "missing-subfiles-documentclass"}]
        result = self.fixer.fix_files(issues)
        output = self.fixer.to_dict(result)

        assert output["skill"] == "qa-infra-subfiles-fix"
        assert output["status"] == "DONE"
        assert "files_fixed" in output
        assert "summary" in output
        assert output["files_fixed"][0]["backup"].endswith(".bak")

    def test_does_not_duplicate_existing_structure(self):
        """Test that existing structure is not duplicated."""
        content = r"""
\documentclass[../main.tex]{subfiles}
\begin{document}
\chapter{Test}
Content.
\end{document}
"""
        # Attempt to fix already-fixed content
        fixed = self.fixer.fix_content(content, [
            "missing-subfiles-documentclass",
            "missing-begin-document",
            "missing-end-document"
        ])

        # Should only have one of each
        assert fixed.count(r"\documentclass") == 1
        assert fixed.count(r"\begin{document}") == 1
        assert fixed.count(r"\end{document}") == 1

    def test_get_patterns(self):
        """Test get_patterns returns all 3 fix patterns."""
        patterns = self.fixer.get_patterns()
        assert len(patterns) == 3
        assert "added-documentclass-subfiles" in patterns
        assert "added-begin-document" in patterns
        assert "added-end-document" in patterns

    def test_custom_main_path(self):
        """Test custom main.tex path."""
        fixer = SubfilesChapterFixer(Path(self.temp_dir), main_path="../../main.tex")
        content = r"\chapter{Test}"
        fixed = fixer.fix_content(content, ["missing-subfiles-documentclass"])

        assert r"\documentclass[../../main.tex]{subfiles}" in fixed
