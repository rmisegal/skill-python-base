"""Unit tests for Code Fixer."""
import pytest
from qa_engine.infrastructure.fixing.code_fixer import CodeFixer
from qa_engine.domain.models.issue import Issue, Severity


class TestCodeFixer:
    """Tests for CodeFixer."""

    def setup_method(self):
        self.fixer = CodeFixer()

    def test_fix_hebrew_in_comment(self):
        """Test Hebrew comment is replaced with placeholder."""
        line = "x = 5  # תריצי prompt ילמודנר"
        result = self.fixer._fix_hebrew_in_code(line)
        assert "[TODO: translate Hebrew comment]" in result
        assert "תריצי" not in result

    def test_fix_hebrew_in_string(self):
        """Test Hebrew in string is replaced."""
        line = 'print("שלום עולם")'
        result = self.fixer._fix_hebrew_in_code(line)
        assert "[HEB]" in result
        assert "שלום" not in result

    def test_fix_preserves_english(self):
        """Test English code is preserved."""
        line = "def hello():  # English comment"
        result = self.fixer._fix_hebrew_in_code(line)
        assert result == line

    def test_fix_mixed_content(self):
        """Test line with both English and Hebrew."""
        line = "result = model.generate()  # הפעלת המודל"
        result = self.fixer._fix_hebrew_in_code(line)
        assert "result = model.generate()" in result
        assert "[TODO: translate Hebrew comment]" in result

    def test_fix_with_issues(self):
        """Test fix method with code-hebrew-content issues."""
        content = '''def test():
    # שלום עולם
    return True'''
        issue = Issue(
            rule="code-hebrew-content",
            file="test.tex",
            line=2,
            content="# שלום עולם",
            severity=Severity.WARNING,
            context={"in_code_block": True}
        )
        result = self.fixer.fix(content, [issue])
        assert "[TODO: translate Hebrew comment]" in result

    def test_fix_docstring_hebrew(self):
        """Test Hebrew in docstring pattern."""
        line = '"""הנובו תוילמודנר תולאש"""'
        result = self.fixer._fix_hebrew_in_code(line)
        assert "[HEB]" in result

    def test_get_patterns(self):
        """Test get_patterns returns dict."""
        patterns = self.fixer.get_patterns()
        assert isinstance(patterns, dict)
        assert "english-wrapper" in patterns


class TestCodeHebrewContentDetection:
    """Tests for code-hebrew-content rule detection."""

    def setup_method(self):
        from qa_engine.infrastructure.detection.code_detector import CodeDetector
        self.detector = CodeDetector()

    def test_detects_hebrew_comment(self):
        """Test detection of Hebrew in comment."""
        content = r'''
\begin{pythonbox}[Test]
def test():
    # שלום
    pass
\end{pythonbox}
'''
        issues = self.detector.detect(content, "test.tex")
        rules = [i.rule for i in issues]
        assert "code-hebrew-content" in rules or "code-direction-hebrew" in rules

    def test_detects_hebrew_string(self):
        """Test detection of Hebrew in string."""
        content = r'''
\begin{pythonbox}[Test]
msg = "שלום עולם"
\end{pythonbox}
'''
        issues = self.detector.detect(content, "test.tex")
        rules = [i.rule for i in issues]
        assert "code-hebrew-content" in rules or "code-direction-hebrew" in rules


class TestCodeOrchestrator:
    """Tests for CodeOrchestrator."""

    def setup_method(self):
        from qa_engine.infrastructure.code_orchestrator import CodeOrchestrator
        self.orch = CodeOrchestrator()

    def test_run_detects_issues(self):
        """Test orchestrator detects code issues."""
        content = r'''
\begin{pythonbox}[Test]
# שלום עולם
\end{pythonbox}
'''
        result = self.orch.run(content, "test.tex", apply_fixes=False)
        assert result.detect_result is not None
        assert result.detect_result.total > 0

    def test_run_fixes_issues(self):
        """Test orchestrator fixes code issues."""
        content = r'''
\begin{pythonbox}[Test]
# שלום עולם
\end{pythonbox}
'''
        result = self.orch.run(content, "test.tex", apply_fixes=True)
        assert result.fix_result is not None
        assert "[TODO: translate" in result.fix_result.content
