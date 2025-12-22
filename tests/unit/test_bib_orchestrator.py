"""Unit tests for Bibliography QA module aligned with qa-bib skill.md family."""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from qa_engine.bibliography import (
    BibOrchestrator, BibDetector, BibFixer,
    BibDetectResult, BibIssueType, BibSeverity
)


class TestBibDetector:
    """Tests for BibDetector (qa-bib-detect)."""

    def setup_method(self):
        self.detector = BibDetector()

    # Step 1: Extract Citations
    def test_extract_cite(self):
        """Test \\cite{} extraction."""
        tex = r"\cite{smith2020}"
        citations = self.detector.extract_citations_from_content(tex)
        assert len(citations) == 1
        assert citations[0][0] == "smith2020"

    def test_extract_multiple_cite(self):
        """Test multiple citations in one command."""
        tex = r"\cite{smith2020,vapnik1995,hinton2012}"
        citations = self.detector.extract_citations_from_content(tex)
        assert len(citations) == 3

    def test_extract_citep(self):
        """Test \\citep{} extraction."""
        tex = r"\citep{smith2020}"
        citations = self.detector.extract_citations_from_content(tex)
        assert len(citations) == 1

    def test_extract_citet(self):
        """Test \\citet{} extraction."""
        tex = r"\citet{smith2020}"
        citations = self.detector.extract_citations_from_content(tex)
        assert len(citations) == 1

    def test_extract_parencite(self):
        """Test \\parencite{} extraction."""
        tex = r"\parencite{smith2020}"
        citations = self.detector.extract_citations_from_content(tex)
        assert len(citations) == 1

    def test_extract_textcite(self):
        """Test \\textcite{} extraction."""
        tex = r"\textcite{smith2020}"
        citations = self.detector.extract_citations_from_content(tex)
        assert len(citations) == 1

    # Step 2: Parse .bib File
    def test_extract_bib_keys(self):
        """Test bibliography key extraction."""
        bib = """@article{smith2020,
  author = {Smith},
  title = {Title}
}
@book{jones2019,
  author = {Jones},
  title = {Book}
}"""
        keys = self.detector.extract_bib_keys_from_content(bib)
        assert "smith2020" in keys
        assert "jones2019" in keys
        assert len(keys) == 2

    # Step 3: Cross-Reference Check
    def test_detect_missing_entry(self):
        """Test detection of missing bibliography entry."""
        tex = r"\cite{missing_key}"
        bib = "@article{other_key, author={A}, title={T}}"
        result = self.detector.detect_content(tex, bib)
        assert any(i.type == BibIssueType.MISSING_ENTRY for i in result.issues)
        assert "missing_key" in result.missing_entries

    def test_detect_unused_entry(self):
        """Test detection of unused bibliography entry."""
        tex = r"\cite{used_key}"
        bib = """@article{used_key, author={A}}
@article{unused_key, author={B}}"""
        result = self.detector.detect_content(tex, bib)
        assert any(i.type == BibIssueType.UNUSED_ENTRY for i in result.issues)
        assert "unused_key" in result.unused_entries

    # Step 4: Check for Bibliography Command
    def test_detect_missing_printbib(self):
        """Test detection of missing \\printbibliography."""
        tex = r"\cite{key1}"
        bib = "@article{key1, author={A}}"
        result = self.detector.detect_content(tex, bib)
        assert any(i.type == BibIssueType.MISSING_PRINTBIB for i in result.issues)

    def test_detect_has_printbib(self):
        """Test detection when \\printbibliography exists."""
        tex = r"\cite{key1}\printbibliography[heading=bibintoc]"
        bib = "@article{key1, author={A}}"
        result = self.detector.detect_content(tex, bib)
        assert result.has_printbib

    # Step 5: TOC Entry
    def test_detect_toc_bibintoc(self):
        """Test TOC detection via bibintoc option."""
        tex = r"\printbibliography[heading=bibintoc]"
        result = self.detector.detect_content(tex, "")
        assert result.bib_in_toc

    def test_detect_not_in_toc(self):
        """Test detection when bibliography not in TOC."""
        tex = r"\cite{k}\printbibliography"
        bib = "@article{k, author={A}}"
        result = self.detector.detect_content(tex, bib)
        assert any(i.type == BibIssueType.NOT_IN_TOC for i in result.issues)

    # Pattern 6: English Environment (v1.1)
    def test_detect_not_in_english(self):
        """Test detection when not in English environment."""
        tex = r"\cite{k}\printbibliography"
        bib = "@article{k, author={A}}"
        result = self.detector.detect_content(tex, bib)
        assert not result.bib_in_english

    def test_detect_in_english(self):
        """Test detection when in English environment."""
        tex = r"\begin{english}\printbibliography[heading=bibintoc]\end{english}"
        result = self.detector.detect_content(tex, "")
        assert result.bib_in_english

    # Verdict Logic
    def test_verdict_fail_missing_entry(self):
        """Test FAIL verdict for missing entry."""
        tex = r"\cite{missing}"
        result = self.detector.detect_content(tex, "")
        assert result.verdict == "FAIL"

    def test_verdict_warning_not_in_toc(self):
        """Test WARNING verdict for not in TOC."""
        tex = r"\begin{english}\printbibliography\end{english}"
        result = self.detector.detect_content(tex, "")
        assert result.verdict == "WARNING"

    def test_verdict_pass(self):
        """Test PASS verdict when all good."""
        tex = r"\begin{english}\printbibliography[heading=bibintoc]\end{english}"
        result = self.detector.detect_content(tex, "")
        assert result.verdict == "PASS"

    # Output Format
    def test_output_format(self):
        """Test output format matches skill.md."""
        tex = r"\cite{k1}"
        bib = "@article{k1, author={A}}"
        result = self.detector.detect_content(tex, bib)
        output = self.detector.to_dict(result)

        assert output["skill"] == "qa-bib-detect"
        assert output["status"] == "DONE"
        assert "verdict" in output
        assert "citations" in output
        assert "bib_file" in output
        assert "issues" in output
        assert "summary" in output
        assert "triggers" in output


class TestBibFixer:
    """Tests for BibFixer (qa-bib-fix-missing)."""

    def setup_method(self):
        self.fixer = BibFixer()

    # Fix 1: Missing Entry
    def test_add_missing_entry(self):
        """Test adding placeholder entry."""
        bib = "@article{existing, author={A}}"
        updated, fix = self.fixer.add_missing_entry(bib, "new_key")
        assert "new_key" in updated
        assert "TODO" in updated
        assert fix["type"] == "added_entry"

    def test_add_entry_article_template(self):
        """Test article template."""
        bib = ""
        updated, fix = self.fixer.add_missing_entry(bib, "key", "article")
        assert "@article{key" in updated

    def test_add_entry_book_template(self):
        """Test book template."""
        bib = ""
        updated, fix = self.fixer.add_missing_entry(bib, "key", "book")
        assert "@book{key" in updated

    # Fix 2: Missing Print Command
    def test_add_printbibliography_hebrew(self):
        """Test adding printbibliography for Hebrew docs."""
        tex = r"\begin{document}Hello\end{document}"
        updated, fix = self.fixer.add_printbibliography(tex, is_hebrew=True)
        assert "printenglishbibliography" in updated
        assert fix["type"] == "added_printbib"

    def test_add_printbibliography_standard(self):
        """Test adding printbibliography for standard docs."""
        tex = r"\begin{document}Hello\end{document}"
        updated, fix = self.fixer.add_printbibliography(tex, is_hebrew=False)
        assert "printbibliography" in updated
        assert "bibintoc" in updated

    # Fix 3: TOC Entry
    def test_add_toc_bibintoc(self):
        """Test adding TOC via bibintoc."""
        tex = r"\printbibliography"
        updated, fix = self.fixer.add_toc_entry(tex, "bibintoc")
        assert "bibintoc" in updated

    def test_add_toc_manual(self):
        """Test adding manual TOC entry."""
        tex = r"\printbibliography"
        updated, fix = self.fixer.add_toc_entry(tex, "manual")
        assert "addcontentsline" in updated

    # Fix English Wrapper
    def test_add_english_wrapper(self):
        """Test wrapping in English environment."""
        tex = r"\printbibliography"
        updated, fix = self.fixer.add_english_wrapper(tex)
        assert r"\begin{english}" in updated
        assert r"\end{english}" in updated

    # Fix Bibitemsep
    def test_add_bibitemsep(self):
        """Test adding bibitemsep."""
        tex = r"\printbibliography"
        updated, fix = self.fixer.add_bibitemsep(tex)
        assert "bibitemsep" in updated

    # Entry Templates
    def test_get_entry_templates(self):
        """Test entry templates are available."""
        templates = self.fixer.get_entry_templates()
        assert "misc" in templates
        assert "article" in templates
        assert "book" in templates
        assert "inproceedings" in templates

    # Output Format
    def test_output_format(self):
        """Test output format matches skill.md."""
        from qa_engine.bibliography import BibFixResult
        result = BibFixResult()
        result.fixes_applied.append({"type": "added_entry", "key": "k"})
        output = self.fixer.to_dict(result)

        assert output["skill"] == "qa-bib-fix-missing"
        assert "status" in output
        assert "fixes_applied" in output
        assert "manual_actions_required" in output
        assert "verification" in output


class TestBibOrchestrator:
    """Tests for BibOrchestrator (qa-bib Level 1)."""

    def setup_method(self):
        self.orchestrator = BibOrchestrator()

    def test_run_on_content_detection_only(self):
        """Test orchestrator runs detection."""
        tex = r"\cite{key1}"
        bib = "@article{key1, author={A}}"
        result = self.orchestrator.run_on_content(tex, bib)
        assert result.detect_result is not None
        assert result.detect_result.citations_total == 1

    def test_run_on_content_with_fixes(self):
        """Test orchestrator runs fixes when requested."""
        tex = r"\cite{missing}"
        result = self.orchestrator.run_on_content(tex, "", auto_fix=True)
        assert result.detect_result is not None
        # Fixes would be prepared

    def test_get_child_skills(self):
        """Test child skills are defined."""
        children = self.orchestrator.get_child_skills()
        assert len(children) == 2
        assert any(c["skill"] == "qa-bib-detect" for c in children)
        assert any(c["skill"] == "qa-bib-fix-missing" for c in children)

    def test_get_detection_categories(self):
        """Test detection categories are defined."""
        categories = self.orchestrator.get_detection_categories()
        assert len(categories) == 5

    def test_get_verdict_logic(self):
        """Test verdict logic is defined."""
        logic = self.orchestrator.get_verdict_logic()
        assert "FAIL" in logic
        assert "WARNING" in logic
        assert "PASS" in logic

    def test_output_format(self):
        """Test output format matches qa-bib skill.md."""
        tex = r"\cite{k}\begin{english}\printbibliography[heading=bibintoc]\end{english}"
        bib = "@article{k, author={A}}"
        result = self.orchestrator.run_on_content(tex, bib)
        output = self.orchestrator.to_dict(result)

        assert output["skill"] == "qa-bib"
        assert output["status"] == "DONE"
        assert "verdict" in output
        assert "children_results" in output
        assert "summary" in output
        assert "qa-bib-detect" in output["children_results"]

    def test_summary_fields(self):
        """Test summary contains all required fields."""
        tex = r"\cite{k}"
        bib = "@article{k, author={A}}"
        result = self.orchestrator.run_on_content(tex, bib)
        output = self.orchestrator.to_dict(result)

        summary = output["summary"]
        assert "citations_found" in summary
        assert "bib_entries" in summary
        assert "missing_entries" in summary
        assert "unused_entries" in summary
        assert "has_printbib" in summary
        assert "in_toc" in summary
