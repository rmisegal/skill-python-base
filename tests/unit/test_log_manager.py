"""Tests for LogManager - FIFO rotation and versioning."""

import pytest
from pathlib import Path
from qa_engine.infrastructure.log_manager import LogManager, MAX_LOG_FILES


class TestLogManager:
    """Tests for LogManager."""

    def test_get_next_version_empty_dir(self, tmp_path):
        """Test first version is 1 in empty directory."""
        manager = LogManager(tmp_path)
        assert manager.get_next_version() == 1

    def test_get_next_version_increments(self, tmp_path):
        """Test version increments correctly."""
        manager = LogManager(tmp_path)
        (tmp_path / "qa-execution-1.log").write_text("test")
        (tmp_path / "qa-execution-2.log").write_text("test")
        assert manager.get_next_version() == 3

    def test_get_existing_logs_sorted(self, tmp_path):
        """Test logs returned sorted by version."""
        manager = LogManager(tmp_path)
        (tmp_path / "qa-execution-3.log").write_text("test")
        (tmp_path / "qa-execution-1.log").write_text("test")
        (tmp_path / "qa-execution-2.log").write_text("test")
        logs = manager.get_existing_logs()
        assert len(logs) == 3
        assert logs[0].name == "qa-execution-1.log"
        assert logs[2].name == "qa-execution-3.log"

    def test_get_log_path(self, tmp_path):
        """Test log path generation."""
        manager = LogManager(tmp_path)
        path = manager.get_log_path(5)
        assert path.name == "qa-execution-5.log"
        assert path.parent == tmp_path

    def test_rotate_logs_under_limit(self, tmp_path):
        """Test no rotation when under limit."""
        manager = LogManager(tmp_path)
        for i in range(5):
            (tmp_path / f"qa-execution-{i+1}.log").write_text("test")
        deleted = manager.rotate_logs()
        assert len(deleted) == 0
        assert len(manager.get_existing_logs()) == 5

    def test_rotate_logs_at_limit(self, tmp_path):
        """Test rotation when at limit."""
        manager = LogManager(tmp_path)
        for i in range(MAX_LOG_FILES):
            (tmp_path / f"qa-execution-{i+1}.log").write_text("test")
        deleted = manager.rotate_logs()
        assert len(deleted) == 1
        assert deleted[0].name == "qa-execution-1.log"
        assert len(manager.get_existing_logs()) == MAX_LOG_FILES - 1

    def test_rotate_logs_over_limit(self, tmp_path):
        """Test rotation when over limit."""
        manager = LogManager(tmp_path)
        for i in range(MAX_LOG_FILES + 3):
            (tmp_path / f"qa-execution-{i+1}.log").write_text("test")
        deleted = manager.rotate_logs()
        assert len(deleted) == 4  # Need to delete 4 to get to MAX-1
        remaining = manager.get_existing_logs()
        assert len(remaining) == MAX_LOG_FILES - 1

    def test_clear_logs(self, tmp_path):
        """Test clearing all logs."""
        manager = LogManager(tmp_path)
        for i in range(5):
            (tmp_path / f"qa-execution-{i+1}.log").write_text("test")
        count = manager.clear_logs()
        assert count == 5
        assert len(manager.get_existing_logs()) == 0

    def test_clear_logs_empty_dir(self, tmp_path):
        """Test clearing empty directory."""
        manager = LogManager(tmp_path)
        count = manager.clear_logs()
        assert count == 0

    def test_save_with_rotation(self, tmp_path):
        """Test saving with automatic rotation."""
        manager = LogManager(tmp_path)
        path = manager.save_with_rotation('{"test": 1}')
        assert path.exists()
        assert path.name == "qa-execution-1.log"
        path2 = manager.save_with_rotation('{"test": 2}')
        assert path2.name == "qa-execution-2.log"

    def test_save_with_rotation_fifo(self, tmp_path):
        """Test FIFO rotation on save."""
        manager = LogManager(tmp_path)
        # Create MAX_LOG_FILES logs
        for i in range(MAX_LOG_FILES):
            manager.save_with_rotation(f'{{"version": {i+1}}}')
        # Should have MAX_LOG_FILES logs
        assert len(manager.get_existing_logs()) == MAX_LOG_FILES
        # Save one more - should rotate oldest
        manager.save_with_rotation('{"version": "new"}')
        logs = manager.get_existing_logs()
        assert len(logs) == MAX_LOG_FILES
        # Oldest should be version 2 now (1 was deleted)
        assert logs[0].name == "qa-execution-2.log"

    def test_get_latest_log(self, tmp_path):
        """Test getting latest log."""
        manager = LogManager(tmp_path)
        assert manager.get_latest_log() is None
        (tmp_path / "qa-execution-1.log").write_text("test")
        (tmp_path / "qa-execution-5.log").write_text("test")
        latest = manager.get_latest_log()
        assert latest.name == "qa-execution-5.log"

    def test_get_log_count(self, tmp_path):
        """Test log count."""
        manager = LogManager(tmp_path)
        assert manager.get_log_count() == 0
        for i in range(3):
            (tmp_path / f"qa-execution-{i+1}.log").write_text("test")
        assert manager.get_log_count() == 3

    def test_ignores_non_log_files(self, tmp_path):
        """Test ignores files that don't match pattern."""
        manager = LogManager(tmp_path)
        (tmp_path / "qa-execution-1.log").write_text("test")
        (tmp_path / "other-file.log").write_text("test")
        (tmp_path / "qa-execution.log").write_text("test")  # Wrong pattern
        (tmp_path / "qa-execution-abc.log").write_text("test")  # Not numeric
        logs = manager.get_existing_logs()
        assert len(logs) == 1
        assert logs[0].name == "qa-execution-1.log"

    def test_creates_directory_if_missing(self, tmp_path):
        """Test creates log directory if it doesn't exist."""
        log_dir = tmp_path / "nested" / "logs"
        manager = LogManager(log_dir)
        assert log_dir.exists()
