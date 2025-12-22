"""
Tests for CLS version fixer.
"""

import tempfile
from pathlib import Path

import pytest

from qa_engine.infrastructure.fixing.cls_fixer import (
    CLSFixer,
    FixResult,
    REFERENCE_CLS_FILE,
)


class TestCLSFixer:
    """Tests for CLSFixer."""

    def setup_method(self):
        """Create fixer instance."""
        self.fixer = CLSFixer()

    def test_get_patterns(self):
        """Test get_patterns returns expected patterns."""
        patterns = self.fixer.get_patterns()
        assert "copy-reference-cls" in patterns
        assert "backup-existing-cls" in patterns

    def test_fix_creates_backup(self):
        """Test fix_file creates backup of existing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create mock reference CLS
            ref_cls = Path(tmpdir) / "reference.cls"
            ref_cls.write_text("% Version 5.11.2 - New\n", encoding="utf-8")

            # Create existing project CLS
            project_cls = Path(tmpdir) / "project.cls"
            project_cls.write_text("% Version 5.10.0 - Old\n", encoding="utf-8")

            fixer = CLSFixer(reference_cls=ref_cls)
            result = fixer.fix_file(project_cls, create_backup=True)

            assert result.success
            assert result.backup_path is not None
            assert Path(result.backup_path).exists()

            # Check backup content
            backup_content = Path(result.backup_path).read_text(encoding="utf-8")
            assert "5.10.0" in backup_content

            # Check new content
            new_content = project_cls.read_text(encoding="utf-8")
            assert "5.11.2" in new_content

    def test_fix_no_backup(self):
        """Test fix_file without backup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ref_cls = Path(tmpdir) / "reference.cls"
            ref_cls.write_text("% Version 5.11.2 - New\n", encoding="utf-8")

            project_cls = Path(tmpdir) / "project.cls"
            project_cls.write_text("% Version 5.10.0 - Old\n", encoding="utf-8")

            fixer = CLSFixer(reference_cls=ref_cls)
            result = fixer.fix_file(project_cls, create_backup=False)

            assert result.success
            assert result.backup_path is None

    def test_fix_missing_reference(self):
        """Test fix_file with missing reference."""
        with tempfile.TemporaryDirectory() as tmpdir:
            missing_ref = Path(tmpdir) / "nonexistent.cls"
            project_cls = Path(tmpdir) / "project.cls"
            project_cls.write_text("% Version 5.10.0\n", encoding="utf-8")

            fixer = CLSFixer(reference_cls=missing_ref)
            result = fixer.fix_file(project_cls)

            assert not result.success
            assert "not found" in result.message

    def test_fix_new_file(self):
        """Test fix_file when project file doesn't exist yet."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ref_cls = Path(tmpdir) / "reference.cls"
            ref_cls.write_text("% Version 5.11.2 - New\n", encoding="utf-8")

            project_cls = Path(tmpdir) / "project.cls"
            # Don't create project_cls - it doesn't exist

            fixer = CLSFixer(reference_cls=ref_cls)
            result = fixer.fix_file(project_cls, create_backup=True)

            assert result.success
            assert result.backup_path is None  # No backup when file didn't exist
            assert project_cls.exists()

    def test_get_new_capabilities(self):
        """Test getting new capabilities from reference."""
        capabilities = self.fixer.get_new_capabilities()

        if REFERENCE_CLS_FILE.exists():
            assert isinstance(capabilities, list)
            # Should find NEW: or FIXED: entries
            if len(capabilities) > 0:
                assert any("NEW" in cap or "FIXED" in cap for cap in capabilities)

    def test_get_version(self):
        """Test extracting version from CLS file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".cls", delete=False) as f:
            f.write("% Version 3.2.1 - Test\n")
            temp_path = Path(f.name)

        try:
            version = self.fixer._get_version(temp_path)
            assert version == "3.2.1"
        finally:
            temp_path.unlink()
