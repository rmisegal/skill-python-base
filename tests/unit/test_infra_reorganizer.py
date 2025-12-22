"""Unit tests for Infrastructure Reorganizer."""
import os
import tempfile
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from qa_engine.infrastructure.fixing.infra_reorganizer import (
    InfraReorganizer, ReorganizeResult, MoveRecord
)


class TestInfraReorganizer:
    """Tests for InfraReorganizer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.reorganizer = InfraReorganizer(Path(self.temp_dir))

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_create_missing_directory(self):
        """Test creating missing target directory."""
        # Create file in root
        (Path(self.temp_dir) / "test.png").touch()

        misplaced = [{"file": "test.png", "current": "./", "target": "images/"}]
        result = self.reorganizer.reorganize(misplaced)

        assert "images/" in result.directories_created
        assert (Path(self.temp_dir) / "images").exists()

    def test_move_single_file(self):
        """Test moving a single file."""
        (Path(self.temp_dir) / "diagram.png").touch()

        misplaced = [
            {"file": "diagram.png", "current": "./", "target": "images/",
             "reason": "Image file"}
        ]
        result = self.reorganizer.reorganize(misplaced)

        assert result.files_moved == 1
        assert not (Path(self.temp_dir) / "diagram.png").exists()
        assert (Path(self.temp_dir) / "images" / "diagram.png").exists()

    def test_move_multiple_files(self):
        """Test moving multiple files to different directories."""
        (Path(self.temp_dir) / "image.png").touch()
        (Path(self.temp_dir) / "script.py").touch()
        (Path(self.temp_dir) / "notes.md").touch()

        misplaced = [
            {"file": "image.png", "current": "./", "target": "images/"},
            {"file": "script.py", "current": "./", "target": "src/"},
            {"file": "notes.md", "current": "./", "target": "doc/"},
        ]
        result = self.reorganizer.reorganize(misplaced)

        assert result.files_moved == 3
        assert (Path(self.temp_dir) / "images" / "image.png").exists()
        assert (Path(self.temp_dir) / "src" / "script.py").exists()
        assert (Path(self.temp_dir) / "doc" / "notes.md").exists()

    def test_handle_naming_conflict(self):
        """Test handling naming conflict with timestamp."""
        # Create target directory with existing file
        (Path(self.temp_dir) / "images").mkdir()
        (Path(self.temp_dir) / "images" / "test.png").touch()
        # Create source file
        (Path(self.temp_dir) / "test.png").write_text("new content")

        misplaced = [{"file": "test.png", "current": "./", "target": "images/"}]
        result = self.reorganizer.reorganize(misplaced)

        assert result.files_moved == 1
        # Original file should still exist
        assert (Path(self.temp_dir) / "images" / "test.png").exists()
        # New file should be renamed with timestamp
        images_dir = Path(self.temp_dir) / "images"
        png_files = list(images_dir.glob("test*.png"))
        assert len(png_files) == 2

    def test_skip_nonexistent_source(self):
        """Test handling nonexistent source file."""
        misplaced = [{"file": "ghost.png", "current": "./", "target": "images/"}]
        result = self.reorganizer.reorganize(misplaced)

        assert result.files_moved == 0
        assert len(result.errors) == 1
        assert "Source not found" in result.errors[0]

    def test_skip_root_target(self):
        """Test skipping files that should stay in root."""
        misplaced = [{"file": "README.md", "current": "./", "target": "."}]
        result = self.reorganizer.reorganize(misplaced)

        assert result.files_moved == 0

    def test_to_dict_format(self):
        """Test output dictionary format."""
        (Path(self.temp_dir) / "test.py").touch()
        misplaced = [{"file": "test.py", "current": "./", "target": "src/"}]
        result = self.reorganizer.reorganize(misplaced)
        output = self.reorganizer.to_dict(result)

        assert output["skill"] == "qa-infra-reorganize"
        assert output["status"] == "DONE"
        assert output["files_moved"] == 1
        assert "moves" in output

    def test_generate_log(self):
        """Test log generation format."""
        (Path(self.temp_dir) / "test.png").touch()
        misplaced = [
            {"file": "test.png", "current": "./", "target": "images/",
             "reason": "Image file"}
        ]
        result = self.reorganizer.reorganize(misplaced)
        log = self.reorganizer.generate_log(result)

        assert "test.png" in log
        assert "FROM:" in log
        assert "TO:" in log
        assert "REASON: Image file" in log

    def test_preserve_file_content(self):
        """Test that file content is preserved after move."""
        content = "This is test content with Hebrew: שלום"
        (Path(self.temp_dir) / "test.md").write_text(content, encoding="utf-8")

        misplaced = [{"file": "test.md", "current": "./", "target": "doc/"}]
        self.reorganizer.reorganize(misplaced)

        moved_content = (Path(self.temp_dir) / "doc" / "test.md").read_text(
            encoding="utf-8"
        )
        assert moved_content == content
