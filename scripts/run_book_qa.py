"""
Run comprehensive QA on the AI-tools-in-business book.

This script runs all QA families with detection verification.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from qa_engine.infrastructure.detection.cls_detector import CLSDetector
from qa_engine.infrastructure.detection.bidi_detector import BiDiDetector
from qa_engine.infrastructure.detection.code_detector import CodeDetector
from qa_engine.infrastructure.detection.table_detector import TableDetector
from qa_engine.infrastructure.detection.bib_detector import BibDetector
from qa_engine.infrastructure.detection.typeset_detector import TypesetDetector
from qa_engine.infrastructure.detection.image_detector import ImageDetector
from qa_engine.infrastructure.detection.heb_math_detector import HebMathDetector
from qa_engine.infrastructure.fixing.cls_fixer import CLSFixer
from qa_engine.infrastructure.fixing.bidi_fixer import BiDiFixer
from qa_engine.infrastructure.fixing.code_fixer import CodeFixer
from qa_engine.infrastructure.fixing.table_fixer import TableFixer
from qa_engine.infrastructure.fixing.bib_fixer import BibFixer
from qa_engine.infrastructure.fixing.heb_math_fixer import HebMathFixer
from qa_engine.infrastructure.fixing.image_fixer import ImageFixer
from qa_engine.infrastructure.fixing.cls_tex_updater import CLSTexUpdater
from qa_engine.infrastructure.coordination.detection_verifier import DetectionVerifier
from qa_engine.infrastructure.reporting.report_models import (
    QASuperReport, FamilyResult, CLSCheckResult
)
from qa_engine.infrastructure.reporting.qa_super_formatter import QASuperFormatter
from qa_engine.domain.models.issue import Issue, Severity
from datetime import datetime
import json


def run_full_qa(book_path: Path):
    """Run comprehensive QA on book."""
    print(f"\n{'='*60}")
    print("QA SUPER - Full Book Analysis")
    print(f"{'='*60}")
    print(f"Book path: {book_path}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Initialize report
    report = QASuperReport(document_name="AI-tools-in-business")
    all_issues: list[Issue] = []
    verifier = DetectionVerifier()

    # Get all tex files
    tex_files = list(book_path.rglob("*.tex"))
    print(f"\nFound {len(tex_files)} .tex files")

    # Phase 0: CLS Version Check (BLOCKING)
    print(f"\n{'='*60}")
    print("PHASE 0: CLS Version Check (BLOCKING)")
    print(f"{'='*60}")

    cls_detector = CLSDetector()
    cls_file = book_path / "hebrew-academic-template.cls"
    if cls_file.exists():
        content = cls_file.read_text(encoding="utf-8")
        cls_issues = cls_detector.detect(content, str(cls_file))
        if cls_issues:
            print(f"  CLS issues found: {len(cls_issues)}")
            report.cls_check = CLSCheckResult(
                status="NEEDS_UPDATE",
                version="unknown",
                action_taken=f"Found {len(cls_issues)} issues"
            )
        else:
            print("  CLS is current")
            report.cls_check = CLSCheckResult(status="CURRENT", version="2.0")
    else:
        print("  No CLS file found")
        report.cls_check = CLSCheckResult(status="MISSING", action_taken="No CLS file")

    # Run CLS TeX Updater
    tex_updater = CLSTexUpdater()
    update_report = tex_updater.update_project(book_path)
    if update_report.total_changes > 0:
        print(f"  CLSTexUpdater: {update_report.total_changes} changes in {update_report.files_updated} files")
        report.cls_check.action_taken += f", Updated {update_report.files_updated} tex files"

    # Define all QA families with (family_name, detector_class_name, detector, fixer)
    families = [
        ("BiDi", "BiDiDetector", BiDiDetector(), BiDiFixer()),
        ("code", "CodeDetector", CodeDetector(), CodeFixer()),
        ("table", "TableDetector", TableDetector(), TableFixer()),
        ("bib", "BibDetector", BibDetector(), BibFixer()),
        ("typeset", "TypesetDetector", TypesetDetector(), None),
        ("heb_math", "HebMathDetector", HebMathDetector(), HebMathFixer()),
        ("img", "ImageDetector", ImageDetector(), ImageFixer()),
    ]

    # Run each family
    for family_name, detector_class_name, detector, fixer in families:
        print(f"\n{'='*60}")
        print(f"FAMILY: {family_name}")
        print(f"{'='*60}")

        family_issues = []
        files_scanned = 0

        for tex_file in tex_files:
            try:
                content = tex_file.read_text(encoding="utf-8")
                issues = detector.detect(content, str(tex_file))
                family_issues.extend(issues)
                files_scanned += 1
            except Exception as e:
                print(f"  Error scanning {tex_file.name}: {e}")

        # Record detection with correct class name
        verifier.record_detection(
            detector_name=detector_class_name,
            files_scanned=files_scanned,
            issues_found=len(family_issues),
        )

        print(f"  Files scanned: {files_scanned}")
        print(f"  Issues found: {len(family_issues)}")

        # Apply fixes if available
        fixed_count = 0
        if fixer and family_issues:
            print(f"  Applying fixes...")
            # Group issues by file
            issues_by_file: dict[str, list[Issue]] = {}
            for issue in family_issues:
                if issue.file not in issues_by_file:
                    issues_by_file[issue.file] = []
                issues_by_file[issue.file].append(issue)

            for file_path, file_issues in issues_by_file.items():
                try:
                    tex_file = Path(file_path)
                    if tex_file.exists():
                        content = tex_file.read_text(encoding="utf-8")
                        # Use fix_with_context for BibFixer
                        if hasattr(fixer, 'fix_with_context') and family_name == "bib":
                            new_content = fixer.fix_with_context(content, file_issues, file_path)
                            # Also apply regular fix for malformed cites
                            new_content = fixer.fix(new_content, file_issues)
                        else:
                            new_content = fixer.fix(content, file_issues)
                        if new_content != content:
                            tex_file.write_text(new_content, encoding="utf-8")
                            fixed_count += len(file_issues)
                except Exception as e:
                    print(f"    Error fixing {Path(file_path).name}: {e}")
            print(f"  Fixes applied: {fixed_count}")

        # Determine verdict
        if not family_issues:
            verdict = "PASS"
        elif fixed_count == len(family_issues):
            verdict = "PASS"
        elif any(i.severity == Severity.CRITICAL for i in family_issues):
            verdict = "FAIL"
        else:
            verdict = "WARNING"

        # Verify detection ran
        verification = verifier.verify_family(family_name)

        report.families.append(FamilyResult(
            family=family_name,
            verdict=verdict,
            issues_found=len(family_issues),
            issues_fixed=fixed_count,
            detection_verified=verification.is_verified,
        ))

        # Collect issues for report
        all_issues.extend(family_issues)

        # Show sample issues
        if family_issues:
            print(f"  Sample issues:")
            for issue in family_issues[:3]:
                print(f"    - {issue.rule} in {Path(issue.file).name}:{issue.line}")

    # Categorize issues
    for issue in all_issues:
        if issue.severity == Severity.CRITICAL:
            report.critical_issues.append(issue)
        elif issue.severity == Severity.WARNING:
            report.warnings.append(issue)

    # Verification summary
    print(f"\n{'='*60}")
    print("DETECTION VERIFICATION")
    print(f"{'='*60}")
    verification_report = verifier.get_verification_report()
    for family, data in verification_report.items():
        status = "VERIFIED" if data["verified"] else "NOT VERIFIED"
        print(f"  {family}: {status}")

    # Add recommendations
    if report.critical_issues:
        report.recommendations.append("Address critical issues before publishing")
    if any(not f.detection_verified for f in report.families):
        report.recommendations.append("Re-run QA to verify all detections")

    # Generate report
    print(f"\n{'='*60}")
    print("GENERATING REPORT")
    print(f"{'='*60}")

    formatter = QASuperFormatter()
    markdown = formatter.format(report)

    report_path = book_path / "QA-REPORT.md"
    report_path.write_text(markdown, encoding="utf-8")
    print(f"  Report saved to: {report_path}")

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"  Total issues found: {len(all_issues)}")
    print(f"  Critical issues: {len(report.critical_issues)}")
    print(f"  Warnings: {len(report.warnings)}")
    print(f"  Families executed: {len(report.families)}")

    # Show family results
    print(f"\n  Family Results:")
    for f in report.families:
        icon = {"PASS": "OK", "FAIL": "FAIL", "WARNING": "WARN"}.get(f.verdict, "?")
        print(f"    [{icon}] {f.family}: {f.issues_found} issues, {f.issues_fixed} fixed")

    return report


if __name__ == "__main__":
    book_path = Path(__file__).parent.parent / "book"
    run_full_qa(book_path)
