"""Tests for ExecutionLogger."""

import pytest
from datetime import datetime
from pathlib import Path
from qa_engine.infrastructure.execution_logger import ExecutionLogger


class TestExecutionLogger:
    """Tests for ExecutionLogger singleton."""

    def setup_method(self):
        """Reset logger before each test."""
        ExecutionLogger.reset()
        self.logger = ExecutionLogger.get_instance()

    def teardown_method(self):
        """Reset logger after each test."""
        ExecutionLogger.reset()

    def test_singleton_pattern(self):
        """Test singleton returns same instance."""
        logger1 = ExecutionLogger.get_instance()
        logger2 = ExecutionLogger.get_instance()
        assert logger1 is logger2

    def test_start_run_creates_log(self):
        """Test start_run initializes log."""
        self.logger.start_run("test-run-123")
        log = self.logger.get_execution_log()
        assert log is not None
        assert log.run_id == "test-run-123"
        assert log.started_at is not None

    def test_end_run_sets_completion(self):
        """Test end_run sets completed_at."""
        self.logger.start_run("test-run")
        self.logger.end_run()
        log = self.logger.get_execution_log()
        assert log.completed_at is not None

    def test_log_family(self):
        """Test logging a family."""
        self.logger.start_run("test")
        self.logger.log_family("BiDi")
        log = self.logger.get_execution_log()
        assert "BiDi" in log.families_executed

    def test_log_skill(self):
        """Test logging a skill."""
        self.logger.start_run("test")
        self.logger.log_skill("qa-BiDi-detect", "BiDi", 2)
        log = self.logger.get_execution_log()
        assert "qa-BiDi-detect" in log.skills_executed
        assert log.skills_executed["qa-BiDi-detect"].family == "BiDi"
        assert log.skills_executed["qa-BiDi-detect"].level == 2

    def test_log_rule(self):
        """Test logging a rule."""
        self.logger.start_run("test")
        self.logger.log_skill("qa-BiDi-detect", "BiDi", 2)
        self.logger.log_rule("bidi-numbers", "BiDi", "qa-BiDi-detect", issues=3)
        log = self.logger.get_execution_log()
        assert "bidi-numbers" in log.rules_executed
        assert log.rules_executed["bidi-numbers"].issues_found == 3

    def test_verification_report_passes(self):
        """Test verification when all expected executed."""
        self.logger.start_run("test")
        self.logger.log_family("BiDi")
        self.logger.log_rule("bidi-numbers", "BiDi", "qa-BiDi-detect")
        report = self.logger.get_verification_report(
            expected_families=["BiDi"],
            expected_rules={"BiDi": ["bidi-numbers"]}
        )
        assert report["verification_passed"] is True
        assert len(report["families_missing"]) == 0

    def test_verification_report_fails_missing_family(self):
        """Test verification fails when family missing."""
        self.logger.start_run("test")
        self.logger.log_family("BiDi")
        report = self.logger.get_verification_report(
            expected_families=["BiDi", "img"],
            expected_rules={}
        )
        assert report["verification_passed"] is False
        assert "img" in report["families_missing"]

    def test_verification_report_fails_missing_rule(self):
        """Test verification fails when rule missing."""
        self.logger.start_run("test")
        self.logger.log_family("BiDi")
        self.logger.log_rule("bidi-numbers", "BiDi", "qa-BiDi-detect")
        report = self.logger.get_verification_report(
            expected_families=["BiDi"],
            expected_rules={"BiDi": ["bidi-numbers", "bidi-english"]}
        )
        assert report["verification_passed"] is False
        assert "bidi-english" in report["rules_missing"]["BiDi"]

    def test_save_log(self, tmp_path):
        """Test saving log to versioned file."""
        self.logger.start_run("test-save")
        self.logger.log_family("BiDi")
        self.logger.end_run()
        log_dir = tmp_path / "qa-logs"
        output = self.logger.save_log(log_dir)
        assert output is not None
        assert output.exists()
        assert output.name == "qa-execution-1.log"
        content = output.read_text()
        assert "test-save" in content
        assert "BiDi" in content
        assert '"version": 1' in content

    def test_save_log_increments_version(self, tmp_path):
        """Test version increments on successive saves."""
        log_dir = tmp_path / "qa-logs"
        self.logger.start_run("run-1")
        self.logger.end_run()
        path1 = self.logger.save_log(log_dir)
        assert path1.name == "qa-execution-1.log"
        ExecutionLogger.reset()
        self.logger = ExecutionLogger.get_instance()
        self.logger.start_run("run-2")
        self.logger.end_run()
        path2 = self.logger.save_log(log_dir)
        assert path2.name == "qa-execution-2.log"

    def test_clear_logs(self, tmp_path):
        """Test clearing all log files."""
        log_dir = tmp_path / "qa-logs"
        log_dir.mkdir()
        (log_dir / "qa-execution-1.log").write_text("{}")
        (log_dir / "qa-execution-2.log").write_text("{}")
        count = ExecutionLogger.clear_logs(log_dir)
        assert count == 2
        assert len(list(log_dir.iterdir())) == 0

    def test_reset_clears_state(self):
        """Test reset clears singleton and log."""
        self.logger.start_run("test")
        self.logger.log_family("BiDi")
        ExecutionLogger.reset()
        new_logger = ExecutionLogger.get_instance()
        assert new_logger.get_execution_log() is None
