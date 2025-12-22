"""Unit tests for Hbox Fixer."""
import pytest
from qa_engine.typeset.fixing import HboxFixer, HboxFixResult, ManualReview


class TestHboxFixer:
    """Tests for HboxFixer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.fixer = HboxFixer()

    def test_add_small_to_encell(self):
        """Test adding \\small to table cell with code identifier."""
        content = r"\encell{sklearn.svm.LinearSVC}"
        fixed, result = self.fixer.fix_content(content)
        assert r"\small" in fixed
        assert result.status == "DONE"

    def test_preserve_existing_small(self):
        """Test that existing \\small is not duplicated."""
        content = r"\encell{\small sklearn.svm.LinearSVC}"
        fixed, result = self.fixer.fix_content(content)
        assert fixed.count(r"\small") == 1

    def test_fix_long_identifier(self):
        """Test fixing long code identifiers."""
        content = r"\encell{sklearn.linear_model.LinearRegression}"
        fixed, result = self.fixer.fix_content(content)
        assert r"\small" in fixed
        assert len(result.fixes_applied) == 1

    def test_short_identifier_not_fixed(self):
        """Test that short identifiers are not modified."""
        content = r"\encell{np.array}"
        fixed, result = self.fixer.fix_content(content)
        # Short identifiers should not trigger fix
        assert r"\small" not in fixed or len(result.fixes_applied) == 0

    def test_wrap_with_sloppy(self):
        """Test wrapping line with sloppy."""
        line = "Very long paragraph text that causes overfull hbox warning"
        fixed, fix = self.fixer._wrap_with_sloppy(line, 1, "test.tex")
        assert r"{\sloppy" in fixed
        assert fix.fix_type == "sloppy"

    def test_no_double_sloppy(self):
        """Test that already sloppy lines are not wrapped again."""
        line = r"{\sloppy Already wrapped text}"
        fixed, fix = self.fixer._wrap_with_sloppy(line, 1, "test.tex")
        assert fix is None
        assert fixed.count(r"\sloppy") == 1

    def test_skip_environment_commands(self):
        """Test that \\begin and \\end lines are not wrapped."""
        content = r"\begin{tabular}{|c|c|}"
        fixed, fix = self.fixer._wrap_with_sloppy(content, 1, "test.tex")
        assert fix is None

    def test_add_allowbreak(self):
        """Test adding allowbreak after dots."""
        content = "sklearn.svm.LinearSVC"
        result = self.fixer.add_allowbreak(content)
        assert r".\allowbreak " in result

    def test_fix_with_issues_list(self):
        """Test fixing with pre-detected issues."""
        content = r"""\encell{sklearn.svm.LinearSVC}
Some text
\encell{another.long.identifier}"""
        issues = [{"line": 1, "type": "overfull", "severity": 15}]
        fixed, result = self.fixer.fix_content(content, "test.tex", issues)
        assert len(result.fixes_applied) == 1

    def test_to_dict_format(self):
        """Test output dictionary format."""
        content = r"\encell{sklearn.svm.LinearSVC}"
        _, result = self.fixer.fix_content(content, "test.tex")
        output = self.fixer.to_dict(result)

        assert output["skill"] == "qa-typeset-fix-hbox"
        assert output["status"] == "DONE"
        assert "fixes_applied" in output
        assert "manual_review" in output
        assert "summary" in output

    def test_fix_has_required_fields(self):
        """Test that fix records have all required fields."""
        content = r"\encell{sklearn.svm.LinearSVC}"
        _, result = self.fixer.fix_content(content, "chapter.tex")
        output = self.fixer.to_dict(result)

        if output["fixes_applied"]:
            fix = output["fixes_applied"][0]
            assert "file" in fix
            assert "line" in fix
            assert "issue_type" in fix
            assert "fix_type" in fix
            assert "before" in fix
            assert "after" in fix

    def test_no_changes_status(self):
        """Test status when no fixes needed."""
        content = "Just some regular text without issues."
        _, result = self.fixer.fix_content(content)
        assert result.status == "NO_CHANGES"

    def test_multiple_cells_in_row(self):
        """Test fixing multiple cells in a table row."""
        content = r"\encell{sklearn.svm.LinearSVC} & \encell{sklearn.tree.DecisionTreeClassifier}"
        fixed, result = self.fixer.fix_content(content)
        assert fixed.count(r"\small") == 2

    def test_preserve_indentation(self):
        """Test that indentation is preserved."""
        content = r"    \encell{sklearn.svm.LinearSVC}"
        fixed, result = self.fixer.fix_content(content)
        assert fixed.startswith("    ")

    def test_manual_review_for_long_en(self):
        """Test that long \\en{} phrases are queued for LLM review."""
        content = r"Text with \en{Very Long English Phrase That Needs Review} here"
        issues = [{"line": 1, "type": "overfull", "severity": 20}]
        _, result = self.fixer.fix_content(content, "test.tex", issues)
        assert len(result.manual_review) == 1
        assert "reword" in result.manual_review[0].suggestion.lower()

    def test_manual_review_has_context(self):
        """Test that manual review includes surrounding context."""
        content = "Line 1\nLine 2 with long text\nLine 3"
        issues = [{"line": 2, "type": "overfull", "severity": 20}]
        _, result = self.fixer.fix_content(content, "test.tex", issues)
        assert len(result.manual_review) == 1
        assert "Line 1" in result.manual_review[0].context

    def test_generate_llm_prompt(self):
        """Test LLM prompt generation."""
        review = ManualReview(
            file="test.tex", line=10, issue_type="overfull",
            content="problematic line content", context="surrounding context",
            suggestion="reword the text", options=["Option A", "Option B"]
        )
        prompt = self.fixer.generate_llm_prompt(review)
        assert "overfull" in prompt
        assert "test.tex" in prompt
        assert "problematic line" in prompt
        assert "Option A" in prompt

    def test_apply_llm_fix(self):
        """Test applying an LLM-suggested fix."""
        content = "Line 1\nOriginal line\nLine 3"
        fixed, fix = self.fixer.apply_llm_fix(content, 2, "reword", "Fixed line", "test.tex")
        assert "Fixed line" in fixed
        assert fix.fix_type == "reword"
        assert fix.line == 2

    def test_manual_review_status(self):
        """Test MANUAL_REVIEW status when items need LLM."""
        content = "Some text here"
        issues = [{"line": 1, "type": "overfull", "severity": 20}]
        _, result = self.fixer.fix_content(content, "test.tex", issues)
        assert result.status == "MANUAL_REVIEW"
