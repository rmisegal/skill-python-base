"""
Float fix patterns for typeset issues.

Deterministic patterns for fixing "Float too large" warnings.
Context-dependent fixes (like code splitting) require LLM.
"""

FLOAT_PATTERNS = {
    # Pattern 1: Add breakable option to tcolorbox
    "add-breakable-tcolorbox": {
        "description": "Add breakable option to tcolorbox environment",
        "find": r"\\begin\{tcolorbox\}(?!\[.*breakable)",
        "replace": r"\\begin{tcolorbox}[breakable]",
        "applies_to": ["typeset-float-too-large"],
        "content_type": "any",
    },
    # Pattern 2: Add breakable to existing tcolorbox options
    "add-breakable-tcolorbox-options": {
        "description": "Add breakable to existing tcolorbox options",
        "find": r"\\begin\{tcolorbox\}\[([^\]]*)\]",
        "replace": r"\\begin{tcolorbox}[\1, breakable]",
        "condition": "breakable not in options",
        "applies_to": ["typeset-float-too-large"],
        "content_type": "any",
    },
    # Pattern 3: Scale figure to textheight
    "scale-figure-height": {
        "description": "Add height constraint to large figures",
        "find": r"\\includegraphics\{([^}]+)\}",
        "replace": r"\\includegraphics[height=0.85\\textheight,keepaspectratio]{\1}",
        "applies_to": ["typeset-float-too-large"],
        "content_type": "figure",
    },
    # Pattern 4: Add height to existing includegraphics options
    "scale-figure-height-options": {
        "description": "Add height constraint to existing includegraphics",
        "find": r"\\includegraphics\[([^\]]*)\]\{([^}]+)\}",
        "replace": r"\\includegraphics[\1,height=0.85\\textheight]{\2}",
        "condition": "height not in options",
        "applies_to": ["typeset-float-too-large"],
        "content_type": "figure",
    },
    # Pattern 5: Use smaller font in lstlisting
    "use-small-lstlisting": {
        "description": "Add smaller font to lstlisting",
        "find": r"\\begin\{lstlisting\}(?!\[)",
        "replace": r"\\begin{lstlisting}[basicstyle=\\small\\ttfamily]",
        "applies_to": ["typeset-float-too-large"],
        "content_type": "code",
    },
    # Pattern 6: Add small font to existing lstlisting options
    "use-small-lstlisting-options": {
        "description": "Add smaller font to existing lstlisting options",
        "find": r"\\begin\{lstlisting\}\[([^\]]*)\]",
        "replace": r"\\begin{lstlisting}[\1, basicstyle=\\small\\ttfamily]",
        "condition": "basicstyle not in options",
        "applies_to": ["typeset-float-too-large"],
        "content_type": "code",
    },
    # Pattern 7: Use page placement for large floats
    "use-page-placement": {
        "description": "Change float placement to page-only [p]",
        "find": r"\\begin\{figure\}\[htbp?\]",
        "replace": r"\\begin{figure}[p]",
        "applies_to": ["typeset-float-too-large"],
        "content_type": "figure",
    },
    # Pattern 8: Add page to figure placement options
    "add-page-placement": {
        "description": "Add page placement option to figure",
        "find": r"\\begin\{figure\}\[([hbt]+)\]",
        "replace": r"\\begin{figure}[\1p]",
        "condition": "p not in options",
        "applies_to": ["typeset-float-too-large"],
        "content_type": "figure",
    },
}

# Overflow thresholds for fix selection (in points)
OVERFLOW_THRESHOLDS = {
    "critical": 100.0,  # > 100pt: needs splitting or major restructure
    "warning": 50.0,    # 50-100pt: font size + minor adjustments
    "minor": 0.0,       # < 50pt: font size or placement change
}

# Content type detection patterns
CONTENT_TYPE_PATTERNS = {
    "code": [
        r"\\begin\{lstlisting\}",
        r"\\begin\{pythonbox\}",
        r"\\begin\{verbatim\}",
        r"\\begin\{minted\}",
    ],
    "table": [
        r"\\begin\{table\}",
        r"\\begin\{tabular\}",
        r"\\begin\{longtable\}",
    ],
    "figure": [
        r"\\begin\{figure\}",
        r"\\includegraphics",
    ],
}
