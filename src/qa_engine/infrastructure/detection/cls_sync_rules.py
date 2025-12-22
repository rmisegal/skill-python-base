"""
CLS sync detection rules.

Externalized rule definitions for CLSSyncDetector.
Rules define what constitutes a CLS sync issue.
"""

from ...domain.models.issue import Severity

CLS_SYNC_RULES = {
    "cls-sync-content-mismatch": {
        "description": "CLS file content differs from master",
        "severity": Severity.CRITICAL,
        "fix_template": "Sync with master/hebrew-academic-template.cls",
    },
    "cls-sync-size-mismatch": {
        "description": "CLS file size differs from master (quick check)",
        "severity": Severity.WARNING,
        "fix_template": "Copy master CLS to this location",
    },
    "cls-sync-no-master": {
        "description": "No master CLS file found for reference",
        "severity": Severity.CRITICAL,
        "fix_template": "Create master/hebrew-academic-template.cls",
    },
}

# Configuration for CLS file locations
CLS_CONFIG = {
    "filename": "hebrew-academic-template.cls",
    "master_dir": "master",
    "shared_dir": "shared",
    "standalone_pattern": "standalone-chapter*",
    "backup_suffix": ".backup",
}
