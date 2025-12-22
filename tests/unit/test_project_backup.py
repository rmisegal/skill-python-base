"""Unit tests for Project Backup Utility."""
import os
import shutil
import tempfile
from pathlib import Path
import pytest
from qa_engine.infrastructure.backup import ProjectBackupUtility, BackupResult


class TestProjectBackupUtility:
    """Tests for ProjectBackupUtility."""

    def setup_method(self):
        """Set up test fixtures."""
        self.utility = ProjectBackupUtility()
        self.temp_dir = tempfile.mkdtemp()
        self.project_dir = Path(self.temp_dir) / "test_project"
        self.project_dir.mkdir()
        # Create test files
        (self.project_dir / "file1.txt").write_text("content1")
        (self.project_dir / "file2.txt").write_text("content2")
        # Create subdirectory with files
        subdir = self.project_dir / "subdir"
        subdir.mkdir()
        (subdir / "file3.txt").write_text("content3")
        # Create hidden directory
        hidden = self.project_dir / ".hidden"
        hidden.mkdir()
        (hidden / "secret.txt").write_text("secret")

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_create_backup_success(self):
        """Test successful backup creation."""
        result = self.utility.create_backup(self.project_dir)
        assert result.success is True
        assert result.verified is True
        assert result.file_count == 4  # 4 files total
        assert "backup_" in result.name
        assert Path(result.path).exists()
        # Clean up backup
        shutil.rmtree(result.path, ignore_errors=True)

    def test_backup_name_format(self):
        """Test backup name follows YYYYMMDD_HHMMSS format."""
        result = self.utility.create_backup(self.project_dir)
        assert result.name.startswith("backup_")
        # Format: backup_YYYYMMDD_HHMMSS
        parts = result.name.split("_")
        assert len(parts) == 3
        assert len(parts[1]) == 8  # YYYYMMDD
        assert len(parts[2]) == 6  # HHMMSS
        shutil.rmtree(result.path, ignore_errors=True)

    def test_backup_includes_hidden_files(self):
        """Test that hidden files are included in backup."""
        result = self.utility.create_backup(self.project_dir)
        backup_path = Path(result.path)
        assert (backup_path / ".hidden" / "secret.txt").exists()
        shutil.rmtree(result.path, ignore_errors=True)

    def test_backup_preserves_structure(self):
        """Test that directory structure is preserved."""
        result = self.utility.create_backup(self.project_dir)
        backup_path = Path(result.path)
        assert (backup_path / "file1.txt").exists()
        assert (backup_path / "subdir" / "file3.txt").exists()
        shutil.rmtree(result.path, ignore_errors=True)

    def test_backup_preserves_content(self):
        """Test that file contents are preserved."""
        result = self.utility.create_backup(self.project_dir)
        backup_path = Path(result.path)
        assert (backup_path / "file1.txt").read_text() == "content1"
        shutil.rmtree(result.path, ignore_errors=True)

    def test_backup_file_count_matches(self):
        """Test that file count verification works."""
        result = self.utility.create_backup(self.project_dir)
        assert result.file_count == result.original_file_count
        assert result.verified is True
        shutil.rmtree(result.path, ignore_errors=True)

    def test_custom_backup_location(self):
        """Test backup to custom location."""
        custom_backup_dir = Path(self.temp_dir) / "custom_backups"
        custom_backup_dir.mkdir()
        utility = ProjectBackupUtility(backup_parent_dir=custom_backup_dir)
        result = utility.create_backup(self.project_dir)
        assert str(custom_backup_dir) in result.path
        shutil.rmtree(result.path, ignore_errors=True)

    def test_nonexistent_project_path(self):
        """Test error handling for non-existent project."""
        result = self.utility.create_backup(Path("/nonexistent/path"))
        assert result.success is False
        assert result.error is not None
        assert "not found" in result.error.lower()

    def test_file_path_instead_of_directory(self):
        """Test error handling when path is file not directory."""
        file_path = self.project_dir / "file1.txt"
        result = self.utility.create_backup(file_path)
        assert result.success is False
        assert result.error is not None
        assert "not a directory" in result.error.lower()

    def test_to_dict_output_format(self):
        """Test that to_dict returns correct format."""
        result = self.utility.create_backup(self.project_dir)
        output = result.to_dict()
        assert output["skill"] == "qa-infra-backup"
        assert output["status"] == "DONE"
        assert "backup" in output
        assert "name" in output["backup"]
        assert "path" in output["backup"]
        assert "size" in output["backup"]
        assert "files" in output["backup"]
        assert "verified" in output["backup"]
        shutil.rmtree(result.path, ignore_errors=True)

    def test_size_calculation(self):
        """Test that size is calculated correctly."""
        result = self.utility.create_backup(self.project_dir)
        assert result.size_bytes > 0
        assert "MB" in result.size_mb
        shutil.rmtree(result.path, ignore_errors=True)
