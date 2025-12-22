"""Unit tests for Infrastructure Scanner."""
import os
import tempfile
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from qa_engine.infrastructure.detection.infra_scanner import (
    InfraScanner, ScanResult, FILE_RULES, REQUIRED_DIRS
)


class TestInfraScanner:
    """Tests for InfraScanner."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.scanner = InfraScanner(Path(self.temp_dir))

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_scan_empty_project(self):
        """Test scanning empty project."""
        result = self.scanner.scan()
        assert result.required_dirs == len(REQUIRED_DIRS)
        assert result.present_dirs == 0
        assert len(result.missing_dirs) == len(REQUIRED_DIRS)

    def test_scan_with_all_required_dirs(self):
        """Test scanning project with all required directories."""
        for dir_path in REQUIRED_DIRS:
            (Path(self.temp_dir) / dir_path).mkdir(parents=True, exist_ok=True)

        result = self.scanner.scan()
        assert result.present_dirs == len(REQUIRED_DIRS)
        assert len(result.missing_dirs) == 0

    def test_detect_misplaced_image(self):
        """Test detecting misplaced image file in root."""
        # Create image file in root
        (Path(self.temp_dir) / "diagram.png").touch()

        result = self.scanner.scan()
        assert result.misplaced == 1
        assert result.misplaced_files[0].file == "diagram.png"
        assert result.misplaced_files[0].target == "images/"

    def test_detect_misplaced_python(self):
        """Test detecting misplaced Python file in root."""
        (Path(self.temp_dir) / "script.py").touch()

        result = self.scanner.scan()
        assert result.misplaced == 1
        assert result.misplaced_files[0].target == "src/"

    def test_readme_stays_in_root(self):
        """Test that README.md is correctly placed in root."""
        (Path(self.temp_dir) / "README.md").touch()

        result = self.scanner.scan()
        assert result.correctly_placed == 1
        assert result.misplaced == 0

    def test_detect_misplaced_markdown(self):
        """Test detecting misplaced markdown (not README)."""
        (Path(self.temp_dir) / "notes.md").touch()

        result = self.scanner.scan()
        assert result.misplaced == 1
        assert result.misplaced_files[0].target == "doc/"

    def test_detect_misplaced_chapter(self):
        """Test detecting misplaced chapter file."""
        (Path(self.temp_dir) / "chapter01.tex").touch()

        result = self.scanner.scan()
        assert result.misplaced == 1
        assert result.misplaced_files[0].target == "chapters/"

    def test_to_dict_format(self):
        """Test output dictionary format."""
        (Path(self.temp_dir) / "test.png").touch()
        result = self.scanner.scan()
        output = self.scanner.to_dict(result)

        assert output["skill"] == "qa-infra-scan"
        assert output["status"] == "DONE"
        assert "directories" in output
        assert "files" in output
        assert "misplaced_files" in output
        assert "qa-infra-reorganize" in output["triggers"]

    def test_multiple_misplaced_files(self):
        """Test detecting multiple misplaced files."""
        (Path(self.temp_dir) / "image.png").touch()
        (Path(self.temp_dir) / "script.py").touch()
        (Path(self.temp_dir) / "notes.md").touch()
        (Path(self.temp_dir) / "README.md").touch()

        result = self.scanner.scan()
        assert result.total_files == 4
        assert result.correctly_placed == 1  # README.md
        assert result.misplaced == 3
