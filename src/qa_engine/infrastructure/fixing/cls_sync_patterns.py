"""
CLS sync fixer patterns.

Externalized configuration for CLSSyncFixer.
"""

CLS_SYNC_FIX_CONFIG = {
    "filename": "hebrew-academic-template.cls",
    "master_dir": "master",
    "shared_dir": "shared",
    "standalone_pattern": "standalone-chapter*",
    "backup_suffix": ".backup",
    "encoding": "utf-8",
}

CLS_SYNC_FIX_PATTERNS = {
    "sync-to-master": {
        "description": "Copy master CLS content to target file",
        "creates_backup": True,
    },
}
