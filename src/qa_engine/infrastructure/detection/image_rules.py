"""
Image detection rules definitions.

Source-level detection for image/figure issues in LaTeX documents.
All rules are regex-based and deterministic.

PDF-level validation (missing rendered images) requires LLM.
"""

from ...domain.models.issue import Severity

IMAGE_RULES = {
    # Rule 1: includegraphics without file
    "img-file-not-found": {
        "description": "Image file referenced but not found on disk",
        "pattern": r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}",
        "check_file_exists": True,
        "severity": Severity.CRITICAL,
        "fix_template": "Create or provide the missing image file",
    },
    # Rule 2: Missing graphicspath
    "img-no-graphicspath": {
        "description": "Document uses images but no graphicspath defined",
        "pattern": r"\\includegraphics",
        "negative_pattern": r"\\graphicspath",
        "document_context": True,
        "severity": Severity.WARNING,
        "fix_template": "Add \\graphicspath{{{{images/}}}}",
    },
    # Rule 3: Wrong extension
    "img-wrong-extension": {
        "description": "Image file has different extension than specified",
        "pattern": r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\.(png|jpg|jpeg|pdf)\}",
        "check_extension_match": True,
        "severity": Severity.WARNING,
        "fix_template": "Change extension to match actual file",
    },
    # Rule 4: Case mismatch (Windows issue)
    "img-case-mismatch": {
        "description": "Image filename has case mismatch with actual file",
        "pattern": r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}",
        "check_case_match": True,
        "severity": Severity.WARNING,
        "fix_template": "Fix filename case to match actual file",
    },
    # Rule 5: Placeholder box instead of image
    "img-placeholder-box": {
        "description": "Figure uses placeholder box instead of actual image",
        "pattern": r"\\fbox\{\\parbox\{[^}]*\}\{[^}]*\}\}",
        "context_pattern": r"\\begin\{figure\}|\\hebrewfigure",
        "severity": Severity.WARNING,
        "fix_template": "Replace with \\includegraphics{{images/your-image.png}}",
    },
    # Rule 6: Empty figure environment
    "img-empty-figure": {
        "description": "Figure environment without includegraphics",
        "pattern": r"\\begin\{figure\}",
        "negative_pattern": r"\\includegraphics",
        "document_context": True,
        "severity": Severity.WARNING,
        "fix_template": "Add \\includegraphics to figure environment",
    },
    # Rule 7: hebrewfigure without image
    "img-hebrew-figure-empty": {
        "description": "hebrewfigure command without actual image",
        "pattern": r"\\hebrewfigure(?:\[[^\]]*\])?\{([^}]*)\}",
        "check_has_includegraphics": True,
        "severity": Severity.WARNING,
        "fix_template": "Add \\includegraphics inside hebrewfigure",
    },
    # Rule 8: Missing width/height specification
    "img-no-size-spec": {
        "description": "includegraphics without width or height",
        "pattern": r"\\includegraphics\{([^}]+)\}",
        "negative_pattern": r"\\includegraphics\[.*(?:width|height|scale).*\]",
        "severity": Severity.INFO,
        "fix_template": "Add [width=0.8\\textwidth] for better control",
    },
}
