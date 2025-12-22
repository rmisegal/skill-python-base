"""
Image fix patterns definitions.

Patterns for fixing image-related issues in LaTeX documents.
All patterns are deterministic string operations.
"""

IMAGE_PATTERNS = {
    # Pattern 1: Add graphicspath to preamble
    "add-graphicspath": {
        "description": "Add graphicspath configuration to preamble",
        "find": r"(\\begin\{document\})",
        "replace": r"\\graphicspath{{images/}{./images/}}\n\n\1",
        "applies_to": ["img-no-graphicspath"],
    },
    # Pattern 2: Fix relative path - add images/ prefix
    "fix-path-prefix": {
        "description": "Add images/ prefix to includegraphics path",
        "find": r"\\includegraphics(\[[^\]]*\])?\{(?!images/)([^}]+)\}",
        "replace": r"\\includegraphics\1{images/\2}",
        "applies_to": ["img-file-not-found"],
    },
    # Pattern 3: Replace placeholder with includegraphics
    "replace-placeholder": {
        "description": "Replace fbox placeholder with includegraphics",
        "find": r"\\fbox\{\\parbox\{[^}]*\}\{[^}]*\}\}",
        "replace": r"\\includegraphics[width=0.8\\textwidth]{images/placeholder.png}",
        "applies_to": ["img-placeholder-box"],
    },
    # Pattern 4: Add width specification
    "add-width-spec": {
        "description": "Add width specification to includegraphics",
        "find": r"\\includegraphics\{([^}]+)\}",
        "replace": r"\\includegraphics[width=0.8\\textwidth]{\1}",
        "applies_to": ["img-no-size-spec"],
    },
    # Pattern 5: Fix PNG extension
    "fix-extension-png": {
        "description": "Change extension to .png",
        "find": r"\\includegraphics(\[[^\]]*\])?\{([^}]+)\.(jpg|jpeg|pdf)\}",
        "replace": r"\\includegraphics\1{\2.png}",
        "applies_to": ["img-wrong-extension"],
    },
    # Pattern 6: Fix case to lowercase
    "fix-case-lower": {
        "description": "Convert filename to lowercase",
        "find": r"\\includegraphics(\[[^\]]*\])?\{([^}]+)\}",
        "replace_func": "lowercase_filename",
        "applies_to": ["img-case-mismatch"],
    },
}
