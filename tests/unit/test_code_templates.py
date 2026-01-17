"""Unit tests for code_templates.py - code blocks and callout boxes."""
import pytest
from qa_engine.bc.templates.code_templates import CodeTemplates


class TestPythonCodeTemplates:
    """Tests for Python code block templates."""

    def test_python_code_basic(self):
        """Basic python code block has english wrapper."""
        result = CodeTemplates.python_code("Example", "print('hello')")
        assert r"\begin{english}" in result
        assert r"\end{english}" in result
        assert r"\begin{pythonbox}[Example]" in result
        assert "print('hello')" in result

    def test_python_code_uses_square_brackets(self):
        """pythonbox must use square brackets for title, not curly braces."""
        result = CodeTemplates.python_code("Title", "code")
        assert "[Title]" in result
        assert "{Title}" not in result

    def test_python_code_long_block(self):
        """Long code blocks use pythonbox* environment."""
        result = CodeTemplates.python_code("Long Example", "code", long_block=True)
        assert r"\begin{pythonbox*}[Long Example]" in result
        assert r"\end{pythonbox*}" in result

    def test_python_function(self):
        """Python function template generates valid structure."""
        result = CodeTemplates.python_function(
            title_eng="Function Example",
            func_name="my_func",
            args=[("x", "int"), ("y", "str")],
            docstring="A test function.",
            body="return x",
            returns="int",
        )
        assert "def my_func(x: int, y: str) -> int:" in result
        assert "A test function." in result
        assert r"\begin{english}" in result

    def test_python_class(self):
        """Python class template generates valid structure."""
        result = CodeTemplates.python_class(
            title_eng="Class Example",
            class_name="MyClass",
            docstring="A test class.",
            methods=["def __init__(self): pass"],
        )
        assert "class MyClass:" in result
        assert "A test class." in result
        assert r"\begin{pythonbox*}" in result  # Classes use long block

    def test_pseudocode(self):
        """Pseudocode template has english wrapper."""
        result = CodeTemplates.pseudocode("Algorithm", "for each item:\n  process")
        assert r"\begin{english}" in result
        assert "# Pseudocode" in result

    def test_numpy_example(self):
        """NumPy example includes import statement."""
        result = CodeTemplates.numpy_example(
            "NumPy Demo",
            "Create array",
            ["arr = np.array([1, 2, 3])"],
        )
        assert "import numpy as np" in result
        assert "# Create array" in result


class TestImportantboxTemplate:
    """Tests for importantbox template."""

    def test_importantbox_has_english_wrapper(self):
        """importantbox must be wrapped in english environment."""
        result = CodeTemplates.importantbox("Important content")
        assert r"\begin{english}" in result
        assert r"\end{english}" in result

    def test_importantbox_environment(self):
        """importantbox uses correct environment name."""
        result = CodeTemplates.importantbox("Content")
        assert r"\begin{importantbox}" in result
        assert r"\end{importantbox}" in result

    def test_importantbox_content_preserved(self):
        """Content is preserved in importantbox."""
        content = "This is very important information!"
        result = CodeTemplates.importantbox(content)
        assert content in result

    def test_importantbox_structure(self):
        """importantbox has correct nesting structure."""
        result = CodeTemplates.importantbox("Test")
        lines = result.strip().split("\n")
        assert lines[0] == r"\begin{english}"
        assert lines[1] == r"\begin{importantbox}"
        assert lines[-2] == r"\end{importantbox}"
        assert lines[-1] == r"\end{english}"


class TestNoteboxTemplate:
    """Tests for notebox template."""

    def test_notebox_has_english_wrapper(self):
        """notebox must be wrapped in english environment."""
        result = CodeTemplates.notebox("Note content")
        assert r"\begin{english}" in result
        assert r"\end{english}" in result

    def test_notebox_environment(self):
        """notebox uses correct environment name."""
        result = CodeTemplates.notebox("Content")
        assert r"\begin{notebox}" in result
        assert r"\end{notebox}" in result


class TestExampleboxTemplate:
    """Tests for examplebox template."""

    def test_examplebox_has_english_wrapper(self):
        """examplebox must be wrapped in english environment."""
        result = CodeTemplates.examplebox("Example content")
        assert r"\begin{english}" in result
        assert r"\end{english}" in result

    def test_examplebox_environment(self):
        """examplebox uses correct environment name."""
        result = CodeTemplates.examplebox("Content")
        assert r"\begin{examplebox}" in result
        assert r"\end{examplebox}" in result


class TestSummaryboxTemplate:
    """Tests for summarybox template."""

    def test_summarybox_has_english_wrapper(self):
        """summarybox must be wrapped in english environment."""
        result = CodeTemplates.summarybox("Summary content")
        assert r"\begin{english}" in result
        assert r"\end{english}" in result

    def test_summarybox_environment(self):
        """summarybox uses correct environment name."""
        result = CodeTemplates.summarybox("Content")
        assert r"\begin{summarybox}" in result
        assert r"\end{summarybox}" in result


class TestGenericCalloutBox:
    """Tests for generic callout_box template."""

    def test_callout_box_importantbox(self):
        """callout_box generates correct importantbox."""
        result = CodeTemplates.callout_box("importantbox", "Content")
        assert r"\begin{importantbox}" in result
        assert r"\begin{english}" in result

    def test_callout_box_notebox(self):
        """callout_box generates correct notebox."""
        result = CodeTemplates.callout_box("notebox", "Content")
        assert r"\begin{notebox}" in result

    def test_callout_box_examplebox(self):
        """callout_box generates correct examplebox."""
        result = CodeTemplates.callout_box("examplebox", "Content")
        assert r"\begin{examplebox}" in result

    def test_callout_box_summarybox(self):
        """callout_box generates correct summarybox."""
        result = CodeTemplates.callout_box("summarybox", "Content")
        assert r"\begin{summarybox}" in result

    def test_callout_box_questionbox(self):
        """callout_box generates correct questionbox."""
        result = CodeTemplates.callout_box("questionbox", "Content")
        assert r"\begin{questionbox}" in result

    def test_callout_box_answerbox(self):
        """callout_box generates correct answerbox."""
        result = CodeTemplates.callout_box("answerbox", "Content")
        assert r"\begin{answerbox}" in result

    def test_callout_box_tcolorbox(self):
        """callout_box generates correct tcolorbox."""
        result = CodeTemplates.callout_box("tcolorbox", "Content")
        assert r"\begin{tcolorbox}" in result

    def test_callout_box_invalid_type_raises(self):
        """callout_box raises ValueError for invalid box type."""
        with pytest.raises(ValueError) as exc_info:
            CodeTemplates.callout_box("invalidbox", "Content")
        assert "invalidbox" in str(exc_info.value)
        assert "Must be one of" in str(exc_info.value)

    def test_callout_box_all_have_english_wrapper(self):
        """All callout boxes must have english wrapper."""
        box_types = [
            "importantbox", "notebox", "examplebox",
            "summarybox", "questionbox", "answerbox", "tcolorbox"
        ]
        for box_type in box_types:
            result = CodeTemplates.callout_box(box_type, "Content")
            assert r"\begin{english}" in result, f"{box_type} missing english wrapper"
            assert r"\end{english}" in result, f"{box_type} missing english end"
