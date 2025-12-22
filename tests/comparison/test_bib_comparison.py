"""Comparison tests: qa-bib skill.md v1.1 vs Python BibOrchestrator.

Verifies Python implementation matches skill.md specification exactly.
"""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from qa_engine.bibliography import (
    BibOrchestrator, BibDetector, BibFixer,
    BibDetectResult, BibIssueType, BibSeverity
)


class TestQaBibDetectComparison:
    """Compare qa-bib-detect skill.md v1.5 with Python BibDetector."""

    def setup_method(self):
        self.detector = BibDetector()

    # ========== Step 1: Extract Citations from .tex ==========
    # skill.md: Support \cite{}, \citep{}, \citet{}, \parencite{}, \textcite{}

    @pytest.mark.parametrize("cmd,expected", [
        (r"\cite{key1}", ["key1"]),
        (r"\citep{key2}", ["key2"]),
        (r"\citet{key3}", ["key3"]),
        (r"\parencite{key4}", ["key4"]),
        (r"\textcite{key5}", ["key5"]),
        (r"\autocite{key6}", ["key6"]),
        (r"\fullcite{key7}", ["key7"]),
    ])
    def test_citation_command_extraction(self, cmd, expected):
        """Step 1: Extract citations from various commands."""
        citations = self.detector.extract_citations_from_content(cmd)
        keys = [c[0] for c in citations]
        for key in expected:
            assert key in keys, f"Expected {key} from {cmd}"

    def test_multiple_keys_in_cite(self):
        """Step 1: Multiple keys in single \cite{}."""
        tex = r"\cite{smith2020,vapnik1995,hinton2012}"
        citations = self.detector.extract_citations_from_content(tex)
        assert len(citations) == 3
        keys = [c[0] for c in citations]
        assert "smith2020" in keys
        assert "vapnik1995" in keys
        assert "hinton2012" in keys

    def test_citation_with_options(self):
        """Step 1: Citations with optional arguments."""
        tex = r"\cite[p.~42]{smith2020}"
        citations = self.detector.extract_citations_from_content(tex)
        keys = [c[0] for c in citations]
        assert "smith2020" in keys

    # ========== Step 2: Parse .bib File ==========
    # skill.md: Extract all entry keys from @type{key, ...}

    @pytest.mark.parametrize("entry_type", [
        "article", "book", "inproceedings", "misc", "online",
        "phdthesis", "mastersthesis", "techreport"
    ])
    def test_bib_entry_type_parsing(self, entry_type):
        """Step 2: Parse various entry types."""
        bib = f"@{entry_type}{{test_key, author={{A}}, title={{T}}}}"
        keys = self.detector.extract_bib_keys_from_content(bib)
        assert "test_key" in keys

    def test_multiple_bib_entries(self):
        """Step 2: Parse multiple entries."""
        bib = """@article{key1, author={A}}
@book{key2, author={B}}
@misc{key3, author={C}}"""
        keys = self.detector.extract_bib_keys_from_content(bib)
        assert len(keys) == 3
        assert "key1" in keys
        assert "key2" in keys
        assert "key3" in keys

    # ========== Step 3: Cross-Reference Check ==========
    # skill.md: Compare cited keys with .bib entries

    def test_all_citations_found(self):
        """Step 3: All citations have entries - no missing."""
        tex = r"\cite{key1}\cite{key2}"
        bib = "@article{key1,author={A}}\n@book{key2,author={B}}"
        result = self.detector.detect_content(tex, bib)
        assert len(result.missing_entries) == 0

    def test_missing_citation_detected(self):
        """Step 3: Missing entry detected."""
        tex = r"\cite{missing_key}"
        bib = "@article{other_key, author={A}}"
        result = self.detector.detect_content(tex, bib)
        assert "missing_key" in result.missing_entries
        assert any(i.type == BibIssueType.MISSING_ENTRY for i in result.issues)

    def test_unused_entry_detected(self):
        """Step 3: Unused entry detected."""
        tex = r"\cite{used_key}"
        bib = "@article{used_key,author={A}}\n@book{unused_key,author={B}}"
        result = self.detector.detect_content(tex, bib)
        assert "unused_key" in result.unused_entries
        assert any(i.type == BibIssueType.UNUSED_ENTRY for i in result.issues)

    # ========== Step 4: Check Bibliography Command ==========
    # skill.md: Verify \printbibliography or \printenglishbibliography exists

    def test_printbibliography_detected(self):
        """Step 4: Standard printbibliography detected."""
        tex = r"\printbibliography"
        result = self.detector.detect_content(tex, "")
        assert result.has_printbib

    def test_printenglishbibliography_detected(self):
        """Step 4: Hebrew printenglishbibliography detected."""
        tex = r"\printenglishbibliography"
        result = self.detector.detect_content(tex, "")
        assert result.has_printbib

    def test_missing_printbib_detected(self):
        """Step 4: Missing printbibliography detected."""
        tex = r"\cite{key1}"
        bib = "@article{key1,author={A}}"
        result = self.detector.detect_content(tex, bib)
        assert not result.has_printbib
        assert any(i.type == BibIssueType.MISSING_PRINTBIB for i in result.issues)

    # ========== Step 5: TOC Entry Check ==========
    # skill.md: Check heading=bibintoc option

    def test_toc_bibintoc_detected(self):
        """Step 5: TOC via bibintoc option."""
        tex = r"\printbibliography[heading=bibintoc]"
        result = self.detector.detect_content(tex, "")
        assert result.bib_in_toc

    def test_toc_bibintoc_with_title(self):
        """Step 5: TOC with title option."""
        tex = r"\printbibliography[heading=bibintoc,title={References}]"
        result = self.detector.detect_content(tex, "")
        assert result.bib_in_toc

    def test_not_in_toc_detected(self):
        """Step 5: NOT_IN_TOC issue detected."""
        tex = r"\cite{k}\printbibliography"
        bib = "@article{k,author={A}}"
        result = self.detector.detect_content(tex, bib)
        assert not result.bib_in_toc
        assert any(i.type == BibIssueType.NOT_IN_TOC for i in result.issues)

    # ========== Step 6: English Environment (v1.1) ==========
    # skill.md v1.1: Check if printbibliography is inside english environment

    def test_in_english_environment(self):
        """Step 6: Bibliography in english environment."""
        tex = r"\begin{english}\printbibliography\end{english}"
        result = self.detector.detect_content(tex, "")
        assert result.bib_in_english

    def test_not_in_english_environment(self):
        """Step 6: Bibliography not in english environment."""
        tex = r"\printbibliography"
        result = self.detector.detect_content(tex, "")
        assert not result.bib_in_english

    # ========== Verdict Logic ==========
    # skill.md: FAIL/WARNING/PASS based on issue severity

    def test_verdict_fail_missing_entry(self):
        """Verdict: FAIL for missing entry (CRITICAL)."""
        tex = r"\cite{missing}"
        result = self.detector.detect_content(tex, "")
        assert result.verdict == "FAIL"

    def test_verdict_fail_missing_printbib(self):
        """Verdict: FAIL for missing printbibliography (CRITICAL)."""
        tex = r"\cite{key}"
        bib = "@article{key,author={A}}"
        result = self.detector.detect_content(tex, bib)
        assert result.verdict == "FAIL"

    def test_verdict_warning_not_in_toc(self):
        """Verdict: WARNING for not in TOC (WARNING severity)."""
        tex = r"\begin{english}\printbibliography\end{english}"
        result = self.detector.detect_content(tex, "")
        assert result.verdict == "WARNING"

    def test_verdict_warning_unused_entry(self):
        """Verdict: WARNING for unused entry."""
        tex = r"\cite{used}\begin{english}\printbibliography[heading=bibintoc]\end{english}"
        bib = "@article{used,author={A}}\n@book{unused,author={B}}"
        result = self.detector.detect_content(tex, bib)
        assert result.verdict == "WARNING"

    def test_verdict_pass_all_good(self):
        """Verdict: PASS when all checks pass."""
        tex = r"\begin{english}\printbibliography[heading=bibintoc]\end{english}"
        result = self.detector.detect_content(tex, "")
        assert result.verdict == "PASS"

    # ========== Output Format ==========
    # skill.md: Required output fields

    def test_output_has_skill_name(self):
        """Output: skill field = 'qa-bib-detect'."""
        result = self.detector.detect_content("", "")
        output = self.detector.to_dict(result)
        assert output["skill"] == "qa-bib-detect"

    def test_output_has_status(self):
        """Output: status field present."""
        result = self.detector.detect_content("", "")
        output = self.detector.to_dict(result)
        assert "status" in output
        assert output["status"] == "DONE"

    def test_output_has_verdict(self):
        """Output: verdict field present."""
        result = self.detector.detect_content("", "")
        output = self.detector.to_dict(result)
        assert "verdict" in output

    def test_output_has_citations(self):
        """Output: citations section present."""
        result = self.detector.detect_content(r"\cite{k}", "@article{k,a={A}}")
        output = self.detector.to_dict(result)
        assert "citations" in output

    def test_output_has_bib_file(self):
        """Output: bib_file section present."""
        result = self.detector.detect_content("", "")
        output = self.detector.to_dict(result)
        assert "bib_file" in output

    def test_output_has_issues(self):
        """Output: issues list present."""
        result = self.detector.detect_content("", "")
        output = self.detector.to_dict(result)
        assert "issues" in output

    def test_output_has_triggers(self):
        """Output: triggers field present."""
        result = self.detector.detect_content("", "")
        output = self.detector.to_dict(result)
        assert "triggers" in output


class TestQaBibFixMissingComparison:
    """Compare qa-bib-fix-missing skill.md v1.0 with Python BibFixer."""

    def setup_method(self):
        self.fixer = BibFixer()

    # ========== Fix 1: Missing Bibliography Entry ==========
    # skill.md: Add placeholder entry with TODO fields

    def test_add_entry_misc_template(self):
        """Fix 1: Add misc placeholder entry."""
        bib = ""
        updated, fix = self.fixer.add_missing_entry(bib, "new_key", "misc")
        assert "@misc{new_key" in updated
        assert "TODO" in updated
        assert fix["type"] == "added_entry"

    def test_add_entry_article_template(self):
        """Fix 1: Add article placeholder entry."""
        bib = ""
        updated, fix = self.fixer.add_missing_entry(bib, "key", "article")
        assert "@article{key" in updated
        assert "journal" in updated.lower()

    def test_add_entry_book_template(self):
        """Fix 1: Add book placeholder entry."""
        bib = ""
        updated, fix = self.fixer.add_missing_entry(bib, "key", "book")
        assert "@book{key" in updated
        assert "publisher" in updated.lower()

    def test_add_entry_inproceedings_template(self):
        """Fix 1: Add inproceedings placeholder entry."""
        bib = ""
        updated, fix = self.fixer.add_missing_entry(bib, "key", "inproceedings")
        assert "@inproceedings{key" in updated
        assert "booktitle" in updated.lower()

    def test_entry_has_keywords_english(self):
        """Fix 1: Entry has keywords=english for biblatex filter."""
        bib = ""
        updated, _ = self.fixer.add_missing_entry(bib, "key")
        assert "keywords" in updated.lower()
        assert "english" in updated

    # ========== Fix 2: Missing Print Command ==========
    # skill.md: Add printbibliography before \end{document}

    def test_add_printbib_hebrew(self):
        """Fix 2: Add printenglishbibliography for Hebrew docs."""
        tex = r"\begin{document}Hello\end{document}"
        updated, fix = self.fixer.add_printbibliography(tex, is_hebrew=True)
        assert "printenglishbibliography" in updated
        assert fix["type"] == "added_printbib"

    def test_add_printbib_standard(self):
        """Fix 2: Add printbibliography with bibintoc for standard docs."""
        tex = r"\begin{document}Hello\end{document}"
        updated, fix = self.fixer.add_printbibliography(tex, is_hebrew=False)
        assert "printbibliography" in updated
        assert "bibintoc" in updated

    def test_add_printbib_with_newpage(self):
        """Fix 2: Include newpage before bibliography."""
        tex = r"\begin{document}Hello\end{document}"
        updated, _ = self.fixer.add_printbibliography(tex)
        assert "newpage" in updated

    # ========== Fix 3: TOC Entry ==========
    # skill.md: Add heading=bibintoc or manual TOC entry

    def test_add_toc_bibintoc_method(self):
        """Fix 3: Add TOC via bibintoc option."""
        tex = r"\printbibliography"
        updated, fix = self.fixer.add_toc_entry(tex, "bibintoc")
        assert "bibintoc" in updated
        assert fix["method"] == "bibintoc"

    def test_add_toc_manual_method(self):
        """Fix 3: Add manual TOC entry."""
        tex = r"\printbibliography"
        updated, fix = self.fixer.add_toc_entry(tex, "manual")
        assert "addcontentsline" in updated
        assert fix["method"] == "manual"

    def test_toc_manual_has_phantomsection(self):
        """Fix 3: Manual TOC has phantomsection for hyperref."""
        tex = r"\printbibliography"
        updated, _ = self.fixer.add_toc_entry(tex, "manual")
        assert "phantomsection" in updated

    # ========== Fix 4: English Wrapper ==========
    # skill.md v1.1: Wrap in english environment for RTL docs

    def test_add_english_wrapper(self):
        """Fix 4: Wrap printbibliography in english environment."""
        tex = r"\printbibliography"
        updated, fix = self.fixer.add_english_wrapper(tex)
        assert r"\begin{english}" in updated
        assert r"\end{english}" in updated
        assert fix["type"] == "added_english_wrapper"

    def test_english_wrapper_preserves_options(self):
        """Fix 4: English wrapper preserves existing options."""
        tex = r"\printbibliography[heading=bibintoc]"
        updated, _ = self.fixer.add_english_wrapper(tex)
        assert "bibintoc" in updated
        assert r"\begin{english}" in updated

    # ========== Bibitemsep Setting ==========
    # skill.md: Add bibitemsep for spacing

    def test_add_bibitemsep(self):
        """Add bibitemsep spacing setting."""
        tex = r"\printbibliography"
        updated, fix = self.fixer.add_bibitemsep(tex)
        assert "bibitemsep" in updated
        assert fix["type"] == "added_bibitemsep"

    def test_bibitemsep_custom_spacing(self):
        """Add bibitemsep with custom spacing."""
        tex = r"\printbibliography"
        updated, _ = self.fixer.add_bibitemsep(tex, spacing="1em")
        assert "1em" in updated

    # ========== Output Format ==========
    # skill.md: Required output fields

    def test_output_has_skill_name(self):
        """Output: skill field = 'qa-bib-fix-missing'."""
        from qa_engine.bibliography import BibFixResult
        result = BibFixResult()
        output = self.fixer.to_dict(result)
        assert output["skill"] == "qa-bib-fix-missing"

    def test_output_has_fixes_applied(self):
        """Output: fixes_applied list present."""
        from qa_engine.bibliography import BibFixResult
        result = BibFixResult()
        output = self.fixer.to_dict(result)
        assert "fixes_applied" in output

    def test_output_has_manual_actions(self):
        """Output: manual_actions_required list present."""
        from qa_engine.bibliography import BibFixResult
        result = BibFixResult()
        output = self.fixer.to_dict(result)
        assert "manual_actions_required" in output

    def test_output_has_verification(self):
        """Output: verification section present."""
        from qa_engine.bibliography import BibFixResult
        result = BibFixResult()
        output = self.fixer.to_dict(result)
        assert "verification" in output


class TestQaBibOrchestratorComparison:
    """Compare qa-bib skill.md v1.0 (Level 1) with Python BibOrchestrator."""

    def setup_method(self):
        self.orchestrator = BibOrchestrator()

    # ========== Child Skills ==========
    # skill.md: Manages qa-bib-detect and qa-bib-fix-missing

    def test_child_skills_defined(self):
        """Orchestrator: Has correct child skills."""
        children = self.orchestrator.get_child_skills()
        skill_names = [c["skill"] for c in children]
        assert "qa-bib-detect" in skill_names
        assert "qa-bib-fix-missing" in skill_names

    def test_child_skills_count(self):
        """Orchestrator: Has exactly 2 child skills."""
        children = self.orchestrator.get_child_skills()
        assert len(children) == 2

    # ========== Detection Categories ==========
    # skill.md: 5 detection categories

    def test_detection_categories_count(self):
        """Orchestrator: Has 5 detection categories."""
        categories = self.orchestrator.get_detection_categories()
        assert len(categories) == 5

    @pytest.mark.parametrize("category_name", [
        "Missing Bibliography Entry",
        "Missing Bibliography Command",
        "Missing TOC Entry",
        "Empty Bibliography",
        "Unused Entry"
    ])
    def test_detection_category_exists(self, category_name):
        """Orchestrator: Has required detection category."""
        categories = self.orchestrator.get_detection_categories()
        names = [c["name"] for c in categories]
        assert category_name in names

    # ========== Verdict Logic ==========
    # skill.md: FAIL/WARNING/PASS definitions

    def test_verdict_logic_fail_defined(self):
        """Orchestrator: FAIL verdict defined."""
        logic = self.orchestrator.get_verdict_logic()
        assert "FAIL" in logic

    def test_verdict_logic_warning_defined(self):
        """Orchestrator: WARNING verdict defined."""
        logic = self.orchestrator.get_verdict_logic()
        assert "WARNING" in logic

    def test_verdict_logic_pass_defined(self):
        """Orchestrator: PASS verdict defined."""
        logic = self.orchestrator.get_verdict_logic()
        assert "PASS" in logic

    # ========== Orchestration Flow ==========
    # skill.md: Detection then optional fixing

    def test_run_detection_only(self):
        """Orchestrator: Runs detection only by default."""
        tex = r"\cite{key}"
        bib = "@article{key,author={A}}"
        result = self.orchestrator.run_on_content(tex, bib, auto_fix=False)
        assert result.detect_result is not None

    def test_run_with_auto_fix(self):
        """Orchestrator: Runs fixes when requested."""
        tex = r"\cite{missing}"
        result = self.orchestrator.run_on_content(tex, "", auto_fix=True)
        assert result.detect_result is not None
        # Fix result may be present if triggers detected

    # ========== Output Format ==========
    # skill.md: Required output structure

    def test_output_has_skill_name(self):
        """Output: skill field = 'qa-bib'."""
        result = self.orchestrator.run_on_content("", "")
        output = self.orchestrator.to_dict(result)
        assert output["skill"] == "qa-bib"

    def test_output_has_status(self):
        """Output: status field present."""
        result = self.orchestrator.run_on_content("", "")
        output = self.orchestrator.to_dict(result)
        assert "status" in output

    def test_output_has_verdict(self):
        """Output: verdict field present."""
        result = self.orchestrator.run_on_content("", "")
        output = self.orchestrator.to_dict(result)
        assert "verdict" in output

    def test_output_has_children_results(self):
        """Output: children_results dict present."""
        result = self.orchestrator.run_on_content("", "")
        output = self.orchestrator.to_dict(result)
        assert "children_results" in output

    def test_output_has_detect_in_children(self):
        """Output: qa-bib-detect in children_results."""
        tex = r"\cite{k}"
        bib = "@article{k,author={A}}"
        result = self.orchestrator.run_on_content(tex, bib)
        output = self.orchestrator.to_dict(result)
        assert "qa-bib-detect" in output["children_results"]

    def test_output_has_summary(self):
        """Output: summary section present."""
        result = self.orchestrator.run_on_content("", "")
        output = self.orchestrator.to_dict(result)
        assert "summary" in output

    # ========== Summary Fields ==========
    # skill.md: Required summary fields

    @pytest.mark.parametrize("field", [
        "citations_found",
        "bib_entries",
        "missing_entries",
        "unused_entries",
        "has_printbib",
        "in_toc"
    ])
    def test_summary_has_field(self, field):
        """Summary: Has required field."""
        tex = r"\cite{k}"
        bib = "@article{k,author={A}}"
        result = self.orchestrator.run_on_content(tex, bib)
        output = self.orchestrator.to_dict(result)
        assert field in output["summary"]


class TestEndToEndScenarios:
    """End-to-end scenarios comparing skill.md workflow with Python tool."""

    def setup_method(self):
        self.orchestrator = BibOrchestrator()
        self.detector = BibDetector()
        self.fixer = BibFixer()

    def test_scenario_clean_document(self):
        """Scenario: Clean document with all citations resolved."""
        tex = r"""
\documentclass{article}
\usepackage{biblatex}
\begin{document}
According to \cite{smith2020}, the method works.
Also see \cite{jones2019} for background.
\begin{english}
\printbibliography[heading=bibintoc,title={References}]
\end{english}
\end{document}
"""
        bib = """
@article{smith2020,
  author = {Smith, John},
  title = {A Method},
  journal = {Journal},
  year = {2020}
}
@book{jones2019,
  author = {Jones, Mary},
  title = {Background},
  publisher = {Press},
  year = {2019}
}
"""
        result = self.orchestrator.run_on_content(tex, bib)
        assert result.detect_result.verdict == "PASS"
        assert len(result.detect_result.missing_entries) == 0
        assert len(result.detect_result.unused_entries) == 0

    def test_scenario_missing_entry(self):
        """Scenario: Document with missing citation entry."""
        tex = r"\cite{missing_citation}"
        bib = "@article{other,author={A}}"
        result = self.orchestrator.run_on_content(tex, bib)
        assert result.detect_result.verdict == "FAIL"
        assert "missing_citation" in result.detect_result.missing_entries

    def test_scenario_fix_missing_entry(self):
        """Scenario: Fix a missing citation entry."""
        bib = "@article{existing,author={A}}"
        updated_bib, fix = self.fixer.add_missing_entry(bib, "new_citation")

        # Re-detect after fix
        tex = r"\cite{existing}\cite{new_citation}"
        result = self.detector.detect_content(tex, updated_bib)
        assert "new_citation" not in result.missing_entries

    def test_scenario_hebrew_document(self):
        """Scenario: Hebrew RTL document."""
        tex = r"""
\documentclass{article}
\usepackage{polyglossia}
\setmainlanguage{hebrew}
\begin{document}
מקור: \cite{hebrew_source}
\begin{english}
\printbibliography[heading=bibintoc]
\end{english}
\end{document}
"""
        bib = "@article{hebrew_source,author={Author},keywords={english}}"
        result = self.orchestrator.run_on_content(tex, bib)
        assert result.detect_result.bib_in_english
        assert result.detect_result.bib_in_toc

    def test_scenario_missing_toc_entry(self):
        """Scenario: Bibliography not in TOC."""
        tex = r"\cite{k}\begin{english}\printbibliography\end{english}"
        bib = "@article{k,author={A}}"
        result = self.orchestrator.run_on_content(tex, bib)
        assert result.detect_result.verdict == "WARNING"
        assert not result.detect_result.bib_in_toc

    def test_scenario_multiple_citations_same_key(self):
        """Scenario: Same key cited multiple times."""
        tex = r"\cite{repeated}\cite{repeated}\cite{repeated}"
        bib = "@article{repeated,author={A}}"
        result = self.detector.detect_content(tex, bib)
        # Should count unique keys correctly
        assert result.citations_total == 3  # 3 citations
        assert len(result.unique_keys) == 1  # 1 unique key
