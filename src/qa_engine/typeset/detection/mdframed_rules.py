"""Mdframed detection rules and patterns."""

# Log patterns for detecting warnings
LOG_PATTERNS = {
    "mdframed_warning": r"Package mdframed Warning:.*bad break",
    "tcolorbox_warning": r"Package tcolorbox Warning:.*splitt",
    "underfull_vbox": r"Underfull \\vbox \(badness (\d+)\).*\\output",
    "line_number": r"l\.(\d+)\s+.*\\begin\{(dobox|dontbox|tcolorbox)\}",
}

# Source patterns for box environments
SOURCE_PATTERNS = {
    "box_env": r"\\begin\{(dobox|dontbox|tcolorbox)\}(\[.*?\])?",
    "section_near_box": r"\\(sub)?section\{([^}]*)\}[\s\S]{0,500}\\begin\{(dobox|dontbox)\}",
}

# Detection rules
MDFRAMED_RULES = {
    "mdframed-bad-break": "mdframed bad break warning in log",
    "tcolorbox-split": "tcolorbox split warning in log",
    "underfull-vbox-near-box": "Underfull vbox near box environment",
    "box-near-section": "Box environment near section heading",
}
