"""
Integration tests for QA Controller.
"""

import tempfile
from pathlib import Path

import pytest
from qa_engine.sdk.controller import QAController


class TestQAController:
    """Integration tests for QAController."""

    def test_controller_initialization(self):
        """Test controller can be initialized."""
        with tempfile.TemporaryDirectory() as tmpdir:
            controller = QAController(tmpdir)
            assert controller is not None
            controller.cleanup()

    def test_detect_bidi_issues(self):
        """Test BiDi detection through controller."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tex_file = Path(tmpdir) / "test.tex"
            # Use encoding='utf-8' for Hebrew text
            tex_file.write_text("זה טקסט עם מספר 123 בעברית", encoding="utf-8")

            controller = QAController(tmpdir)
            content = tex_file.read_text(encoding="utf-8")
            issues = controller.detect("BiDi", content, str(tex_file))

            assert len(issues) > 0
            controller.cleanup()

    def test_detect_code_issues(self):
        """Test code detection through controller."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tex_file = Path(tmpdir) / "test.tex"
            tex_file.write_text(
                "\\begin{pythonbox}\nprint('hello')\n\\end{pythonbox}",
                encoding="utf-8",
            )

            controller = QAController(tmpdir)
            content = tex_file.read_text(encoding="utf-8")
            issues = controller.detect("code", content, str(tex_file))

            assert isinstance(issues, list)
            controller.cleanup()

    def test_run_full_pipeline(self):
        """Test running full QA pipeline."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tex_file = Path(tmpdir) / "test.tex"
            tex_file.write_text("זה טקסט עם מספר 123 בעברית", encoding="utf-8")

            controller = QAController(tmpdir)
            status = controller.run()

            assert status.run_id is not None
            assert status.started_at is not None
            assert status.completed_at is not None
            controller.cleanup()

    def test_get_status(self):
        """Test getting status from controller."""
        with tempfile.TemporaryDirectory() as tmpdir:
            controller = QAController(tmpdir)
            status = controller.get_status()

            assert "status" in status
            controller.cleanup()

    def test_with_config_file(self):
        """Test controller with custom config."""
        import json

        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                "enabled_families": ["BiDi"],
                "parallel_families": False,
            }
            config_path = Path(tmpdir) / "qa_setup.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")

            controller = QAController(tmpdir, config_path)
            status = controller.run()

            assert status is not None
            controller.cleanup()
