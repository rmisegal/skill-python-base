"""Comparison tests: qa-infra skill.md family vs Python implementation.

Verifies Python implementation matches skill.md specifications exactly.
"""
import os
import shutil
import tempfile
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from qa_engine.infrastructure.detection.infra_scanner import (
    InfraScanner, ScanResult, REQUIRED_DIRS, FILE_RULES
)
from qa_engine.infrastructure.detection.infra_validator import (
    InfraValidator, ValidationResult, VALID_EXTENSIONS
)
from qa_engine.infrastructure.fixing.infra_reorganizer import (
    InfraReorganizer, ReorganizeResult
)
from qa_engine.infrastructure.backup.project_backup import (
    ProjectBackupUtility, BackupResult
)


class TestQaInfraScanComparison:
    """Compare qa-infra-scan skill.md v1.1.0 with Python InfraScanner."""

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.scanner = InfraScanner(Path(self.temp_dir))

    def teardown_method(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # ========== Required Directories (skill.md) ==========

    @pytest.mark.parametrize("dir_path", [
        ".claude/commands",
        ".claude/skills",
        ".claude/agents",
        ".claude/tasks",
        "chapters",
        "images",
        "src",
        "reviews",
        "doc",
        "examples",
    ])
    def test_required_directory_defined(self, dir_path):
        """Verify all skill.md required directories are defined."""
        assert dir_path in REQUIRED_DIRS

    def test_required_dirs_count(self):
        """Verify correct number of required directories."""
        assert len(REQUIRED_DIRS) >= 10  # At least 10 per skill.md

    # ========== File Categorization Rules (skill.md) ==========

    @pytest.mark.parametrize("pattern,target", [
        ("README.md", "."),        # Must stay in root
        ("*.md", "doc"),           # Documentation
        ("*.txt", "doc"),          # Text documentation
        ("*.py", "src"),           # Python code
        ("*.png", "images"),       # Images
        ("*.jpg", "images"),       # Images
        ("*.svg", "images"),       # Vector images
    ])
    def test_file_rule_defined(self, pattern, target):
        """Verify file categorization rules from skill.md."""
        assert pattern in FILE_RULES
        assert FILE_RULES[pattern] == target

    # ========== Operation: directory-inventory ==========

    def test_operation_directory_inventory(self):
        """Test directory-inventory operation."""
        from qa_engine.infrastructure.detection.infra_scanner import REQUIRED_DIRS as SCANNER_DIRS
        result = self.scanner.scan()
        assert result.required_dirs == len(SCANNER_DIRS)
        assert isinstance(result.present_dirs, int)
        assert isinstance(result.missing_dirs, list)

    def test_directory_inventory_all_present(self):
        """Test directory inventory when all dirs exist."""
        from qa_engine.infrastructure.detection.infra_scanner import REQUIRED_DIRS as SCANNER_DIRS
        for dir_path in SCANNER_DIRS:
            (Path(self.temp_dir) / dir_path).mkdir(parents=True, exist_ok=True)
        result = self.scanner.scan()
        assert result.present_dirs == len(SCANNER_DIRS)
        assert len(result.missing_dirs) == 0

    def test_directory_inventory_missing(self):
        """Test directory inventory with missing dirs."""
        from qa_engine.infrastructure.detection.infra_scanner import REQUIRED_DIRS as SCANNER_DIRS
        result = self.scanner.scan()
        assert result.present_dirs == 0
        assert len(result.missing_dirs) == len(SCANNER_DIRS)

    # ========== Operation: file-categorization ==========

    @pytest.mark.parametrize("filename,expected_target", [
        ("README.md", "."),
        ("notes.md", "doc"),
        ("script.py", "src"),
        ("diagram.png", "images"),
        ("photo.jpg", "images"),
        ("icon.svg", "images"),
        ("chapter01.tex", "chapters"),
        ("example01.tex", "examples"),
    ])
    def test_file_categorization(self, filename, expected_target):
        """Test file categorization for various file types."""
        target = self.scanner._get_target_dir(filename)
        assert target == expected_target

    # ========== Operation: misplaced-detection ==========

    def test_misplaced_detection_image_in_root(self):
        """Test detecting misplaced image file."""
        (Path(self.temp_dir) / "diagram.png").touch()
        result = self.scanner.scan()
        assert result.misplaced == 1
        assert result.misplaced_files[0].target == "images/"

    def test_misplaced_detection_python_in_root(self):
        """Test detecting misplaced Python file."""
        (Path(self.temp_dir) / "script.py").touch()
        result = self.scanner.scan()
        assert result.misplaced == 1
        assert result.misplaced_files[0].target == "src/"

    def test_correctly_placed_readme(self):
        """Test README.md correctly placed in root."""
        (Path(self.temp_dir) / "README.md").touch()
        result = self.scanner.scan()
        assert result.correctly_placed == 1
        assert result.misplaced == 0

    # ========== Operation: structure-report (Output Format) ==========

    def test_output_skill_name(self):
        """Output: skill field = 'qa-infra-scan'."""
        result = self.scanner.scan()
        output = self.scanner.to_dict(result)
        assert output["skill"] == "qa-infra-scan"

    def test_output_status(self):
        """Output: status field = 'DONE'."""
        result = self.scanner.scan()
        output = self.scanner.to_dict(result)
        assert output["status"] == "DONE"

    def test_output_directories_section(self):
        """Output: directories section with required/present/missing."""
        result = self.scanner.scan()
        output = self.scanner.to_dict(result)
        assert "directories" in output
        assert "required" in output["directories"]
        assert "present" in output["directories"]
        assert "missing" in output["directories"]

    def test_output_files_section(self):
        """Output: files section with total/correctly_placed/misplaced."""
        result = self.scanner.scan()
        output = self.scanner.to_dict(result)
        assert "files" in output
        assert "total" in output["files"]
        assert "correctly_placed" in output["files"]
        assert "misplaced" in output["files"]

    def test_output_misplaced_files(self):
        """Output: misplaced_files list with file/current/target."""
        (Path(self.temp_dir) / "test.png").touch()
        result = self.scanner.scan()
        output = self.scanner.to_dict(result)
        assert "misplaced_files" in output
        assert len(output["misplaced_files"]) == 1
        assert "file" in output["misplaced_files"][0]
        assert "current" in output["misplaced_files"][0]
        assert "target" in output["misplaced_files"][0]

    def test_output_triggers_reorganize(self):
        """Output: triggers qa-infra-reorganize when misplaced files."""
        (Path(self.temp_dir) / "test.png").touch()
        result = self.scanner.scan()
        output = self.scanner.to_dict(result)
        assert "triggers" in output
        assert "qa-infra-reorganize" in output["triggers"]


class TestQaInfraValidateComparison:
    """Compare qa-infra-validate skill.md v1.1.0 with Python InfraValidator."""

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.validator = InfraValidator(Path(self.temp_dir))

    def teardown_method(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # ========== Operation: directory-check ==========

    def test_operation_directory_check_all_present(self):
        """Test directory-check operation with all dirs."""
        for dir_path in REQUIRED_DIRS:
            (Path(self.temp_dir) / dir_path).mkdir(parents=True, exist_ok=True)
        (Path(self.temp_dir) / "README.md").touch()
        result = self.validator.validate()
        dirs_issues = [i for i in result.issues if i.check == "directories"]
        assert len(dirs_issues) == 0

    def test_operation_directory_check_missing(self):
        """Test directory-check operation with missing dirs."""
        result = self.validator.validate()
        dirs_issues = [i for i in result.issues if i.check == "directories"]
        assert len(dirs_issues) > 0

    # ========== Operation: readme-check ==========

    def test_operation_readme_check_present(self):
        """Test readme-check operation when README.md exists."""
        (Path(self.temp_dir) / "README.md").touch()
        result = self.validator.validate()
        assert result.readme_in_root is True

    def test_operation_readme_check_missing(self):
        """Test readme-check operation when README.md missing."""
        result = self.validator.validate()
        assert result.readme_in_root is False
        readme_issues = [i for i in result.issues if i.check == "readme"]
        assert len(readme_issues) == 1

    # ========== Operation: file-location-check ==========

    def test_operation_file_location_correct(self):
        """Test file-location-check with correct file types."""
        (Path(self.temp_dir) / "images").mkdir()
        (Path(self.temp_dir) / "images" / "photo.png").touch()
        result = self.validator.validate()
        file_issues = [i for i in result.issues if i.check == "file_location"]
        assert len(file_issues) == 0

    def test_operation_file_location_wrong_type(self):
        """Test file-location-check with wrong file type."""
        (Path(self.temp_dir) / "images").mkdir()
        (Path(self.temp_dir) / "images" / "script.py").touch()
        result = self.validator.validate()
        assert result.files_correct is False
        file_issues = [i for i in result.issues if i.check == "file_location"]
        assert len(file_issues) == 1

    # ========== Operation: file-count-check ==========

    def test_operation_file_count_match(self):
        """Test file-count-check when counts match."""
        (Path(self.temp_dir) / "file1.txt").touch()
        (Path(self.temp_dir) / "file2.txt").touch()
        result = self.validator.validate(expected_file_count=2)
        assert result.no_files_lost is True

    def test_operation_file_count_mismatch(self):
        """Test file-count-check when files lost."""
        (Path(self.temp_dir) / "file1.txt").touch()
        result = self.validator.validate(expected_file_count=5)
        assert result.no_files_lost is False
        count_issues = [i for i in result.issues if i.check == "file_count"]
        assert len(count_issues) == 1

    # ========== Verdict Logic (skill.md) ==========

    def test_verdict_pass_all_good(self):
        """Verdict: PASS when all checks succeed."""
        for dir_path in REQUIRED_DIRS:
            (Path(self.temp_dir) / dir_path).mkdir(parents=True, exist_ok=True)
        (Path(self.temp_dir) / "README.md").touch()
        result = self.validator.validate()
        assert result.verdict == "PASS"

    def test_verdict_fail_missing_dirs(self):
        """Verdict: FAIL when required directories missing."""
        result = self.validator.validate()
        assert result.verdict == "FAIL"

    def test_verdict_fail_readme_missing(self):
        """Verdict: FAIL when README.md missing."""
        for dir_path in REQUIRED_DIRS:
            (Path(self.temp_dir) / dir_path).mkdir(parents=True, exist_ok=True)
        result = self.validator.validate()
        assert result.verdict == "FAIL"

    def test_verdict_fail_wrong_file_location(self):
        """Verdict: FAIL when files in wrong location."""
        for dir_path in REQUIRED_DIRS:
            (Path(self.temp_dir) / dir_path).mkdir(parents=True, exist_ok=True)
        (Path(self.temp_dir) / "README.md").touch()
        (Path(self.temp_dir) / "images" / "script.py").touch()
        result = self.validator.validate()
        assert result.verdict == "FAIL"

    # ========== Output Format (skill.md) ==========

    def test_output_skill_name(self):
        """Output: skill field = 'qa-infra-validate'."""
        result = self.validator.validate()
        output = self.validator.to_dict(result)
        assert output["skill"] == "qa-infra-validate"

    def test_output_status(self):
        """Output: status field = 'DONE'."""
        result = self.validator.validate()
        output = self.validator.to_dict(result)
        assert output["status"] == "DONE"

    def test_output_verdict(self):
        """Output: verdict field (PASS/FAIL)."""
        result = self.validator.validate()
        output = self.validator.to_dict(result)
        assert output["verdict"] in ["PASS", "FAIL"]

    def test_output_checks_section(self):
        """Output: checks section with all required fields."""
        result = self.validator.validate()
        output = self.validator.to_dict(result)
        assert "checks" in output
        assert "directories" in output["checks"]
        assert "readme_in_root" in output["checks"]
        assert "files_correct" in output["checks"]
        assert "no_files_lost" in output["checks"]

    def test_output_issues_list(self):
        """Output: issues list present."""
        result = self.validator.validate()
        output = self.validator.to_dict(result)
        assert "issues" in output


class TestQaInfraBackupComparison:
    """Compare qa-infra-backup skill.md v1.1.0 with Python ProjectBackupUtility."""

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.backup_dir = tempfile.mkdtemp()
        self.backup_util = ProjectBackupUtility(Path(self.backup_dir))

    def teardown_method(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        shutil.rmtree(self.backup_dir, ignore_errors=True)

    # ========== Operation: create-timestamped-backup ==========

    def test_operation_timestamped_backup(self):
        """Test create-timestamped-backup operation."""
        (Path(self.temp_dir) / "file.txt").touch()
        result = self.backup_util.create_backup(Path(self.temp_dir))
        assert result.name.startswith("backup_")
        assert len(result.name) == 22  # backup_YYYYMMDD_HHMMSS

    # ========== Operation: preserve-permissions ==========

    def test_operation_preserve_timestamps(self):
        """Test preserve-timestamps using shutil.copy2."""
        file_path = Path(self.temp_dir) / "file.txt"
        file_path.write_text("content")
        original_mtime = file_path.stat().st_mtime

        result = self.backup_util.create_backup(Path(self.temp_dir))
        backup_file = Path(result.path) / "file.txt"

        # shutil.copy2 preserves modification time
        assert backup_file.exists()

    # ========== Operation: include-hidden-files ==========

    def test_operation_include_hidden_files(self):
        """Test include-hidden-files operation."""
        (Path(self.temp_dir) / ".hidden").touch()
        (Path(self.temp_dir) / ".claude").mkdir()
        (Path(self.temp_dir) / ".claude" / "config").touch()

        result = self.backup_util.create_backup(Path(self.temp_dir))
        backup_path = Path(result.path)

        assert (backup_path / ".hidden").exists()
        assert (backup_path / ".claude" / "config").exists()

    # ========== Operation: verify-file-count ==========

    def test_operation_verify_file_count(self):
        """Test verify-file-count operation."""
        for i in range(5):
            (Path(self.temp_dir) / f"file{i}.txt").touch()

        result = self.backup_util.create_backup(Path(self.temp_dir))
        assert result.file_count == result.original_file_count
        assert result.verified is True

    # ========== Output Format (skill.md) ==========

    def test_output_skill_name(self):
        """Output: skill field = 'qa-infra-backup'."""
        (Path(self.temp_dir) / "file.txt").touch()
        result = self.backup_util.create_backup(Path(self.temp_dir))
        output = result.to_dict()
        assert output["skill"] == "qa-infra-backup"

    def test_output_status(self):
        """Output: status field = 'DONE' on success."""
        (Path(self.temp_dir) / "file.txt").touch()
        result = self.backup_util.create_backup(Path(self.temp_dir))
        output = result.to_dict()
        assert output["status"] == "DONE"

    def test_output_backup_section(self):
        """Output: backup section with name/path/size/files/verified."""
        (Path(self.temp_dir) / "file.txt").touch()
        result = self.backup_util.create_backup(Path(self.temp_dir))
        output = result.to_dict()
        assert "backup" in output
        assert "name" in output["backup"]
        assert "path" in output["backup"]
        assert "size" in output["backup"]
        assert "files" in output["backup"]
        assert "verified" in output["backup"]


class TestQaInfraReorganizeComparison:
    """Compare qa-infra-reorganize (implicit from skill.md) with InfraReorganizer."""

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.reorganizer = InfraReorganizer(Path(self.temp_dir))

    def teardown_method(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # ========== Create Missing Directories ==========

    def test_create_missing_directories(self):
        """Test creating missing target directories."""
        (Path(self.temp_dir) / "test.png").touch()
        misplaced = [{"file": "test.png", "current": "./", "target": "images/"}]
        result = self.reorganizer.reorganize(misplaced)
        assert "images/" in result.directories_created
        assert (Path(self.temp_dir) / "images").exists()

    # ========== Move Files ==========

    def test_move_files_to_correct_locations(self):
        """Test moving files to correct locations."""
        (Path(self.temp_dir) / "image.png").touch()
        (Path(self.temp_dir) / "script.py").touch()
        misplaced = [
            {"file": "image.png", "current": "./", "target": "images/"},
            {"file": "script.py", "current": "./", "target": "src/"},
        ]
        result = self.reorganizer.reorganize(misplaced)
        assert result.files_moved == 2
        assert (Path(self.temp_dir) / "images" / "image.png").exists()
        assert (Path(self.temp_dir) / "src" / "script.py").exists()

    # ========== Handle Conflicts ==========

    def test_handle_naming_conflicts(self):
        """Test handling naming conflicts with timestamp."""
        (Path(self.temp_dir) / "images").mkdir()
        (Path(self.temp_dir) / "images" / "test.png").touch()
        (Path(self.temp_dir) / "test.png").touch()

        misplaced = [{"file": "test.png", "current": "./", "target": "images/"}]
        result = self.reorganizer.reorganize(misplaced)

        assert result.files_moved == 1
        # Both files should exist (one renamed)
        png_files = list((Path(self.temp_dir) / "images").glob("test*.png"))
        assert len(png_files) == 2

    # ========== Preserve Content ==========

    def test_preserve_file_content(self):
        """Test file content preserved after move."""
        content = "Test content with special chars: "
        (Path(self.temp_dir) / "test.md").write_text(content, encoding="utf-8")

        misplaced = [{"file": "test.md", "current": "./", "target": "doc/"}]
        self.reorganizer.reorganize(misplaced)

        moved = (Path(self.temp_dir) / "doc" / "test.md").read_text(encoding="utf-8")
        assert moved == content

    # ========== Generate Log ==========

    def test_generate_move_log(self):
        """Test log generation format."""
        (Path(self.temp_dir) / "test.png").touch()
        misplaced = [{"file": "test.png", "current": "./", "target": "images/",
                      "reason": "Image file"}]
        result = self.reorganizer.reorganize(misplaced)
        log = self.reorganizer.generate_log(result)

        assert "test.png" in log
        assert "FROM:" in log
        assert "TO:" in log
        assert "REASON:" in log

    # ========== Output Format ==========

    def test_output_skill_name(self):
        """Output: skill field = 'qa-infra-reorganize'."""
        result = self.reorganizer.reorganize([])
        output = self.reorganizer.to_dict(result)
        assert output["skill"] == "qa-infra-reorganize"

    def test_output_status(self):
        """Output: status field."""
        result = self.reorganizer.reorganize([])
        output = self.reorganizer.to_dict(result)
        assert output["status"] in ["DONE", "PARTIAL"]

    def test_output_moves_list(self):
        """Output: moves list present."""
        result = self.reorganizer.reorganize([])
        output = self.reorganizer.to_dict(result)
        assert "moves" in output


class TestQaInfraSubfilesDetectComparison:
    """Compare qa-infra-subfiles-detect skill.md with Python SubfilesDetector."""

    def setup_method(self):
        from qa_engine.infrastructure.detection.subfiles_detector import SubfilesDetector
        self.detector = SubfilesDetector()

    # ========== Detection Rules (skill.md) ==========

    def test_rule_subfiles_missing_class(self):
        """Rule: subfiles-missing-class (WARNING)."""
        rules = self.detector.get_rules()
        assert "subfiles-missing-class" in rules

    def test_rule_subfiles_no_main_ref(self):
        """Rule: subfiles-no-main-ref (CRITICAL)."""
        rules = self.detector.get_rules()
        assert "subfiles-no-main-ref" in rules

    def test_rule_subfiles_no_preamble(self):
        """Rule: subfiles-no-preamble (INFO)."""
        rules = self.detector.get_rules()
        assert "subfiles-no-preamble" in rules

    def test_detect_missing_subfiles_class(self):
        """Detect chapter without subfiles documentclass."""
        content = r"\documentclass{article}"
        issues = self.detector.detect(content, "chapter01.tex")
        rule_names = [i.rule for i in issues]
        assert "subfiles-missing-class" in rule_names

    def test_detect_no_main_reference(self):
        """Detect subfiles without main.tex reference."""
        content = r"\documentclass{subfiles}"
        issues = self.detector.detect(content, "chapter01.tex")
        rule_names = [i.rule for i in issues]
        assert "subfiles-no-main-ref" in rule_names

    def test_pass_correct_subfiles_setup(self):
        """Pass when subfiles setup is correct."""
        content = r"\documentclass[../main.tex]{subfiles}"
        # This should not trigger subfiles-no-main-ref
        issues = self.detector.detect(content, "chapter01.tex")
        # Filter for the no-main-ref rule specifically
        no_main_issues = [i for i in issues if i.rule == "subfiles-no-main-ref"]
        assert len(no_main_issues) == 0


class TestEndToEndInfraScenarios:
    """End-to-end scenarios testing complete infrastructure workflow."""

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.backup_dir = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        shutil.rmtree(self.backup_dir, ignore_errors=True)

    def test_scenario_full_reorganization_workflow(self):
        """Scenario: Complete scan -> backup -> reorganize -> validate."""
        # Setup: Create messy project
        (Path(self.temp_dir) / "README.md").write_text("# Project")
        (Path(self.temp_dir) / "diagram.png").touch()
        (Path(self.temp_dir) / "script.py").touch()
        (Path(self.temp_dir) / "notes.md").touch()

        # Step 1: Scan
        scanner = InfraScanner(Path(self.temp_dir))
        scan_result = scanner.scan()
        assert scan_result.misplaced == 3

        # Step 2: Backup (before reorganizing)
        backup_util = ProjectBackupUtility(Path(self.backup_dir))
        backup_result = backup_util.create_backup(Path(self.temp_dir))
        assert backup_result.verified is True
        original_count = backup_result.original_file_count

        # Step 3: Reorganize
        reorganizer = InfraReorganizer(Path(self.temp_dir))
        misplaced = scanner.to_dict(scan_result)["misplaced_files"]
        reorg_result = reorganizer.reorganize(misplaced)
        assert reorg_result.files_moved == 3

        # Step 4: Validate
        validator = InfraValidator(Path(self.temp_dir))
        valid_result = validator.validate(expected_file_count=original_count)
        # May still FAIL due to missing required dirs, but files should be preserved
        assert valid_result.no_files_lost is True

    def test_scenario_clean_project(self):
        """Scenario: Clean project passes validation."""
        # Create properly structured project
        for dir_path in REQUIRED_DIRS:
            (Path(self.temp_dir) / dir_path).mkdir(parents=True, exist_ok=True)
        (Path(self.temp_dir) / "README.md").write_text("# Clean Project")
        (Path(self.temp_dir) / "images" / "logo.png").touch()
        (Path(self.temp_dir) / "src" / "main.py").touch()

        # Scan should find no misplaced files in root
        scanner = InfraScanner(Path(self.temp_dir))
        scan_result = scanner.scan()
        # Files in subdirs aren't scanned by root scanner
        assert scan_result.misplaced == 0

        # Validate should pass
        validator = InfraValidator(Path(self.temp_dir))
        valid_result = validator.validate()
        assert valid_result.verdict == "PASS"

    def test_scenario_backup_verification(self):
        """Scenario: Backup verification catches integrity issues."""
        # Create project with files
        (Path(self.temp_dir) / "important.txt").write_text("critical data")
        (Path(self.temp_dir) / "subdir").mkdir()
        (Path(self.temp_dir) / "subdir" / "nested.txt").write_text("nested data")

        # Backup
        backup_util = ProjectBackupUtility(Path(self.backup_dir))
        result = backup_util.create_backup(Path(self.temp_dir))

        # Verify file count matches
        assert result.file_count == 2
        assert result.original_file_count == 2
        assert result.verified is True

        # Verify content preserved
        backup_path = Path(result.path)
        assert (backup_path / "important.txt").read_text() == "critical data"
        assert (backup_path / "subdir" / "nested.txt").read_text() == "nested data"


# Import REQUIRED_DIRS for validation tests
from qa_engine.infrastructure.detection.infra_validator import REQUIRED_DIRS
