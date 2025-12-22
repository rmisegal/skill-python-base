"""
Run QA Pipeline using the proper architecture.

Uses QAController which reads configuration from qa_setup.json
and applies detection and fixing according to the configuration.
"""

import sys
import io
from pathlib import Path

# Force UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from qa_engine.sdk.controller import QAController
from qa_engine.shared.config import ConfigManager


def main():
    """Main entry point for QA pipeline."""
    # Set up paths
    project_path = Path(__file__).parent.parent
    test_data = project_path / "test-data" / "CLS-examples"
    config_path = project_path / "config" / "qa_setup.json"

    if not test_data.exists():
        print(f"Test data not found: {test_data}")
        return 1

    print("\n" + "=" * 60)
    print("QA PIPELINE - CONFIGURATION-DRIVEN")
    print("=" * 60)
    print(f"Project: {test_data}")
    print(f"Config: {config_path}")

    # Load and display config
    config = ConfigManager()
    config.load(config_path)
    print(f"\nEnabled families: {config.get('enabled_families')}")
    print(f"Auto-fix enabled: {config.get_bool('auto_fix')}")

    # Run multiple passes until no more fixes needed
    max_passes = 3
    for pass_num in range(1, max_passes + 1):
        print(f"\n--- Pass {pass_num} ---")

        # Reset config manager for fresh controller
        ConfigManager.reset()

        # Create controller and run QA
        controller = QAController(test_data, config_path)
        status = controller.run()

        print(f"Run ID: {status.run_id}")
        print(f"Duration: {(status.completed_at - status.started_at).total_seconds():.2f}s")

        # Show family results
        for family, entry in status.entries.items():
            print(f"  {family}: {entry.issues_found} issues")

        # Check total remaining issues by re-running detection
        ConfigManager.reset()
        verify_controller = QAController(test_data, config_path)

        # Temporarily disable auto_fix for verification
        from qa_engine.infrastructure.detection import (
            BiDiDetector, CodeDetector, TableDetector, BibDetector
        )

        total_remaining = 0
        for detector_name, detector in [
            ("BiDi", BiDiDetector()),
            ("code", CodeDetector()),
            ("table", TableDetector()),
            ("bib", BibDetector()),
        ]:
            tex_files = list(test_data.rglob("*.tex"))
            for tex_file in tex_files:
                if "_patch" in tex_file.name or tex_file.suffix != ".tex":
                    continue
                content = tex_file.read_text(encoding="utf-8", errors="ignore")
                issues = detector.detect(content, str(tex_file))
                # Filter by enabled rules from config
                family_rules = config.get(f"families.{detector_name}.rules", {})
                enabled_issues = [
                    i for i in issues
                    if family_rules.get(i.rule, {}).get("enabled", True)
                ]
                total_remaining += len(enabled_issues)

        print(f"\nTotal remaining issues: {total_remaining}")

        if total_remaining == 0:
            print("\nAll issues fixed!")
            break

        controller.cleanup()

    print("\n" + "=" * 60)
    print("QA PIPELINE COMPLETE")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
