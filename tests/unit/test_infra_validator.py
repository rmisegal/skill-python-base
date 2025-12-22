"""Unit tests for Infrastructure Validator."""
import shutil
import tempfile
from pathlib import Path
import pytest
from qa_engine.infrastructure.detection.infra_validator import (
    InfraValidator, ValidationResult, REQUIRED_DIRS
)


class TestInfraValidator:
    """Tests for InfraValidator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.validator = InfraValidator(Path(self.temp_dir))

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_validate_empty_project_fails(self):
        """Test validating empty project fails."""
        result = self.validator.validate()
        assert result.verdict == "FAIL"
        assert result.dirs_present == 0
        assert len(result.issues) > 0

    def test_validate_all_dirs_present(self):
        """Test validation with all required directories."""
        for dir_path in REQUIRED_DIRS:
            (Path(self.temp_dir) / dir_path).mkdir(parents=True, exist_ok=True)
        (Path(self.temp_dir) / "README.md").write_text("# Test")

        result = self.validator.validate()
        assert result.dirs_present == len(REQUIRED_DIRS)
        dirs_issues = [i for i in result.issues if i.check == "directories"]
        assert len(dirs_issues) == 0

    def test_validate_readme_missing(self):
        """Test validation fails when README.md is missing."""
        for dir_path in REQUIRED_DIRS:
            (Path(self.temp_dir) / dir_path).mkdir(parents=True, exist_ok=True)

        result = self.validator.validate()
        assert result.readme_in_root is False
        readme_issues = [i for i in result.issues if i.check == "readme"]
        assert len(readme_issues) == 1

    def test_validate_readme_present(self):
        """Test validation passes when README.md exists."""
        (Path(self.temp_dir) / "README.md").write_text("# Test Project")

        result = self.validator.validate()
        assert result.readme_in_root is True

    def test_validate_wrong_file_in_images(self):
        """Test detection of wrong file type in images/."""
        (Path(self.temp_dir) / "images").mkdir()
        (Path(self.temp_dir) / "images" / "script.py").write_text("print('wrong')")

        result = self.validator.validate()
        assert result.files_correct is False
        file_issues = [i for i in result.issues if i.check == "file_location"]
        assert len(file_issues) == 1
        assert "script.py" in file_issues[0].message

    def test_validate_correct_file_in_images(self):
        """Test correct file type in images/ passes."""
        (Path(self.temp_dir) / "images").mkdir()
        (Path(self.temp_dir) / "images" / "photo.png").write_bytes(b"PNG")

        result = self.validator.validate()
        file_issues = [i for i in result.issues if i.check == "file_location"]
        assert len(file_issues) == 0

    def test_validate_file_count_match(self):
        """Test file count validation passes when counts match."""
        (Path(self.temp_dir) / "file1.txt").write_text("content")
        (Path(self.temp_dir) / "file2.txt").write_text("content")

        result = self.validator.validate(expected_file_count=2)
        assert result.no_files_lost is True
        assert result.actual_count == 2

    def test_validate_file_count_mismatch(self):
        """Test file count validation fails when files lost."""
        (Path(self.temp_dir) / "file1.txt").write_text("content")

        result = self.validator.validate(expected_file_count=5)
        assert result.no_files_lost is False
        count_issues = [i for i in result.issues if i.check == "file_count"]
        assert len(count_issues) == 1

    def test_validate_pass_verdict(self):
        """Test PASS verdict when all checks succeed."""
        for dir_path in REQUIRED_DIRS:
            (Path(self.temp_dir) / dir_path).mkdir(parents=True, exist_ok=True)
        (Path(self.temp_dir) / "README.md").write_text("# Test")

        result = self.validator.validate()
        assert result.verdict == "PASS"
        assert len(result.issues) == 0

    def test_to_dict_format(self):
        """Test output dictionary format."""
        result = self.validator.validate()
        output = self.validator.to_dict(result)

        assert output["skill"] == "qa-infra-validate"
        assert output["status"] == "DONE"
        assert output["verdict"] in ["PASS", "FAIL"]
        assert "checks" in output
        assert "directories" in output["checks"]
        assert "readme_in_root" in output["checks"]
        assert "files_correct" in output["checks"]
        assert "no_files_lost" in output["checks"]
        assert "issues" in output
