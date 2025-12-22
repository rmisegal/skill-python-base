"""Section orphan detection rules and patterns."""

# Section command patterns
SECTION_PATTERNS = {
    "hebrewsection": r"\\hebrewsection\{([^}]*)\}",
    "hebrewsubsection": r"\\hebrewsubsection\{([^}]*)\}",
    "section": r"\\section\{([^}]*)\}",
    "subsection": r"\\subsection\{([^}]*)\}",
    "subsubsection": r"\\subsubsection\{([^}]*)\}",
}

# Needspace pattern - checks if needspace precedes section
NEEDSPACE_PATTERN = r"\\needspace\{(\d+)\\baselineskip\}"
NEEDSPACE_PAR_PATTERN = r"\\par\s*\\needspace\{(\d+)\\baselineskip\}"

# Line thresholds for orphan detection
ORPHAN_THRESHOLDS = {
    "section": 5,
    "hebrewsection": 5,
    "subsection": 4,
    "hebrewsubsection": 4,
    "subsubsection": 3,
}

# Detection rules
ORPHAN_RULES = {
    "missing-needspace-section": "Section without \\needspace orphan protection",
    "missing-needspace-subsection": "Subsection without \\needspace orphan protection",
    "short-content-after-section": "Section with short content before next section/page",
    "section-near-end": "Section title near end of content block",
}
