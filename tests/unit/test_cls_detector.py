"""
Tests for CLS version detector.
"""

import tempfile
from pathlib import Path

import pytest

from qa_engine.infrastructure.detection.cls_detector import (
    CLSDetector,
    CLSVersionInfo,
    REFERENCE_CLS_FILE,
)


class TestCLSDetector:
    """Tests for CLSDetector."""

    def setup_method(self):
        """Create detector instance."""
        self.detector = CLSDetector()

    def test_get_rules(self):
        """Test get_rules returns expected rules."""
        rules = self.detector.get_rules()
        assert "cls-version-mismatch" in rules
        assert "cls-version-parse-error" in rules
        assert "cls-reference-missing" in rules

    def test_parse_valid_version(self):
        """Test parsing valid CLS version header."""
        content = """% hebrew-academic-template.cls
% Version 5.11.2 - TOC BiDi Fixes
% Date: 2025-12-14
"""
        info = self.detector._parse_version(content, "test.cls")

        assert info is not None
        assert info.version == "5.11.2"
        assert info.date == "2025-12-14"
        assert info.description == "TOC BiDi Fixes"

    def test_parse_version_no_date(self):
        """Test parsing version without date line."""
        content = """% Version 5.10.0 - Some Feature
"""
        info = self.detector._parse_version(content, "test.cls")

        assert info is not None
        assert info.version == "5.10.0"
        assert info.date == "unknown"

    def test_parse_invalid_version(self):
        """Test parsing content without version header."""
        content = """% Some other comment
\\NeedsTeXFormat{LaTeX2e}
"""
        info = self.detector._parse_version(content, "test.cls")
        assert info is None

    def test_detect_version_mismatch(self):
        """Test detection of version mismatch."""
        # Create content with old version
        content = """% hebrew-academic-template.cls
% Version 1.0.0 - Old Version
% Date: 2020-01-01
"""
        issues = self.detector.detect(content, "test.cls")

        # Should detect mismatch if reference exists
        if REFERENCE_CLS_FILE.exists():
            mismatch_issues = [i for i in issues if i.rule == "cls-version-mismatch"]
            assert len(mismatch_issues) > 0
            assert "1.0.0" in mismatch_issues[0].content

    def test_detect_parse_error(self):
        """Test detection of parse error."""
        content = """% No version line here
\\documentclass{article}
"""
        issues = self.detector.detect(content, "test.cls")

        parse_errors = [i for i in issues if i.rule == "cls-version-parse-error"]
        assert len(parse_errors) > 0

    def test_reference_info(self):
        """Test getting reference CLS info."""
        info = self.detector.get_reference_info()

        if REFERENCE_CLS_FILE.exists():
            assert info is not None
            assert info.version is not None
            assert len(info.version) > 0

    def test_reference_content(self):
        """Test getting reference CLS content."""
        content = self.detector.get_reference_content()

        if REFERENCE_CLS_FILE.exists():
            assert content is not None
            assert "% Version" in content

    def test_custom_reference_path(self):
        """Test using custom reference path."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".cls", delete=False) as f:
            f.write("% Version 9.9.9 - Test Version\n% Date: 2025-01-01\n")
            temp_path = Path(f.name)

        try:
            detector = CLSDetector(reference_cls=temp_path)
            info = detector.get_reference_info()

            assert info is not None
            assert info.version == "9.9.9"
        finally:
            temp_path.unlink()
