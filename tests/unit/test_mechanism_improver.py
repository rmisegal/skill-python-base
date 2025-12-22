"""Unit tests for QA Mechanism Improver components."""
import tempfile
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from qa_engine.meta.skill_analyzer import SkillAnalyzer, SkillAnalysis, DetectionRule
from qa_engine.meta.failure_classifier import FailureClassifier, FailureMode, BugClassification
from qa_engine.meta.improvement_tracker import ImprovementTracker, InvestigationReport


class TestSkillAnalyzer:
    """Tests for SkillAnalyzer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.analyzer = SkillAnalyzer(Path(self.temp_dir))

    def teardown_method(self):
        """Clean up."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_skill(self, skill_id: str, content: str):
        """Helper to create a skill.md file."""
        skill_dir = Path(self.temp_dir) / skill_id
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "skill.md").write_text(content, encoding="utf-8")

    def test_parse_frontmatter(self):
        """Test YAML frontmatter extraction."""
        content = """---
name: qa-test-detect
description: Test detector
version: 1.2.3
tags: [qa, detection, level-2]
tools: [Read, Grep]
---

# Test Skill
"""
        self._create_skill("qa-test-detect", content)
        analysis = self.analyzer.analyze_skill("qa-test-detect")

        assert analysis.name == "qa-test-detect"
        assert analysis.description == "Test detector"
        assert analysis.version == "1.2.3"
        assert "qa" in analysis.tags
        assert "Read" in analysis.tools

    def test_extract_detection_rules(self):
        """Test detection rule extraction."""
        content = """---
name: qa-test
---

## Detection Rules

### Rule 1: Missing Hebrew wrapper
Pattern to detect missing wrapper.

```regex
\\\\he\\{.*\\}
```

### Rule 2: Wrong direction
Another pattern.

```regex
\\\\begin\\{hebrew\\}
```
"""
        self._create_skill("qa-test", content)
        analysis = self.analyzer.analyze_skill("qa-test")

        assert len(analysis.rules) == 2
        assert analysis.rules[0].description == "Missing Hebrew wrapper"
        assert "he" in analysis.rules[0].regex

    def test_determine_level_from_tags(self):
        """Test level determination from tags."""
        content = """---
name: qa-BiDi
tags: [qa, level-1, orchestrator]
---
"""
        self._create_skill("qa-BiDi", content)
        analysis = self.analyzer.analyze_skill("qa-BiDi")
        assert analysis.level == 1

    def test_extract_family_from_id(self):
        """Test family extraction from skill ID."""
        content = """---
name: qa-BiDi-detect
---
"""
        self._create_skill("qa-BiDi-detect", content)
        analysis = self.analyzer.analyze_skill("qa-BiDi-detect")
        assert analysis.family == "BiDi"

    def test_list_skills(self):
        """Test listing available skills."""
        self._create_skill("qa-test-1", "---\nname: test1\n---")
        self._create_skill("qa-test-2", "---\nname: test2\n---")

        skills = self.analyzer.list_skills()
        assert "qa-test-1" in skills
        assert "qa-test-2" in skills


class TestFailureClassifier:
    """Tests for FailureClassifier."""

    def setup_method(self):
        """Set up classifier."""
        self.classifier = FailureClassifier()

    def test_classify_rtl_bug(self):
        """Test classification of RTL-related bug."""
        result = self.classifier.classify(
            "Hebrew text displays in wrong direction (RTL issue)"
        )

        assert result.l1_family == "qa-BiDi"
        assert "qa-BiDi-detect" in result.l2_detectors
        assert "hebrew" in result.keywords_matched or "rtl" in result.keywords_matched

    def test_classify_table_bug(self):
        """Test classification of table-related bug."""
        result = self.classifier.classify(
            "Table columns are misaligned in tabular environment"
        )

        assert result.l1_family == "qa-table"
        assert "qa-table-detect" in result.l2_detectors

    def test_classify_math_bug(self):
        """Test classification of Hebrew math bug."""
        result = self.classifier.classify(
            "Hebrew subscript in math mode renders incorrectly"
        )

        assert result.l1_family == "qa-BiDi"
        assert "qa-heb-math-detect" in result.l2_detectors

    def test_identify_missing_rule_failure(self):
        """Test failure mode identification."""
        result = self.classifier.classify(
            "Detector ran but no rule covers this pattern - not covered"
        )

        assert result.failure_mode == FailureMode.MISSING_RULE

    def test_identify_skill_not_invoked(self):
        """Test skill not invoked failure mode."""
        result = self.classifier.classify(
            "The skill never ran during QA process - not invoked"
        )

        assert result.failure_mode == FailureMode.SKILL_NOT_INVOKED

    def test_confidence_calculation(self):
        """Test confidence increases with more keyword matches."""
        low_result = self.classifier.classify("table issue")
        high_result = self.classifier.classify("table tabular caption alignment")

        assert high_result.confidence >= low_result.confidence

    def test_suggest_investigation_path(self):
        """Test investigation path suggestion."""
        result = self.classifier.classify("Hebrew text direction issue")
        steps = self.classifier.suggest_investigation_path(result)

        assert len(steps) >= 2
        assert "skill.md" in steps[0]


class TestImprovementTracker:
    """Tests for ImprovementTracker."""

    def setup_method(self):
        """Set up tracker."""
        self.tracker = ImprovementTracker()
        self.classifier = FailureClassifier()

    def test_create_investigation_report(self):
        """Test investigation report creation."""
        classification = self.classifier.classify("Hebrew RTL text bug")
        report = self.tracker.create_investigation(
            description="Hebrew text displays LTR instead of RTL",
            document="chapters/chapter-01.tex",
            classification=classification,
            root_cause="Missing \\he{} wrapper around Hebrew text"
        )

        assert report.responsible_family == "qa-BiDi"
        assert report.document == "chapters/chapter-01.tex"
        assert "wrapper" in report.root_cause

    def test_create_improvement_report(self):
        """Test improvement report creation."""
        analysis = SkillAnalysis(
            skill_id="qa-BiDi-detect",
            name="BiDi Detector",
            description="",
            version="1.0.0",
            level=2,
            skill_type="detection",
            parent="qa-BiDi",
            family="BiDi"
        )
        report = self.tracker.create_improvement(
            skill_analysis=analysis,
            new_rules=["hebrew-inline-missing"],
            new_patterns=[r"\\he\{.*\}"]
        )

        assert report.skill_name == "qa-BiDi-detect"
        assert report.old_version == "1.0.0"
        assert report.new_version == "1.1.0"
        assert "hebrew-inline-missing" in report.new_rules

    def test_format_investigation_markdown(self):
        """Test markdown formatting."""
        classification = self.classifier.classify("table caption issue")
        report = self.tracker.create_investigation(
            description="Caption not aligned",
            document="test.tex",
            classification=classification,
            root_cause="Missing RTL wrapper"
        )
        md = self.tracker.format_investigation_markdown(report)

        assert "## QA Mechanism Investigation Report" in md
        assert "Caption not aligned" in md
        assert "qa-table" in md

    def test_to_dict_output(self):
        """Test JSON-compatible output."""
        classification = self.classifier.classify("overfull hbox")
        report = self.tracker.create_investigation(
            description="Line too long",
            document="test.tex",
            classification=classification,
            root_cause="Text overflow"
        )
        output = self.tracker.to_dict(report)

        assert output["skill"] == "qa-mechanism-improver"
        assert output["status"] == "DONE"
        assert "investigation" in output
        assert "classification" in output
