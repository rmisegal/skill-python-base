"""Encoding replacement patterns for EncodingFixer."""

# Text context patterns (for regular LaTeX text)
TEXT_PATTERNS = {
    "math-minus": {"pattern": r"\u2212", "replace": "-", "description": "Mathematical minus (U+2212) to ASCII"},
    "en-dash": {"pattern": r"\u2013", "replace": "-", "description": "En dash (U+2013) to ASCII"},
    "em-dash": {"pattern": r"\u2014", "replace": "-", "description": "Em dash (U+2014) to ASCII"},
    "left-single-quote": {"pattern": r"\u2018", "replace": "'", "description": "Left single quote to ASCII"},
    "right-single-quote": {"pattern": r"\u2019", "replace": "'", "description": "Right single quote to ASCII"},
    "left-double-quote": {"pattern": r"\u201C", "replace": '"', "description": "Left double quote to ASCII"},
    "right-double-quote": {"pattern": r"\u201D", "replace": '"', "description": "Right double quote to ASCII"},
    "multiplication": {"pattern": r"\u00D7", "replace": r"$\times$", "description": "Multiplication sign to LaTeX"},
    "right-arrow": {"pattern": r"\u2192", "replace": r"$\rightarrow$", "description": "Right arrow to LaTeX"},
    "check-mark": {"pattern": r"[\u2713\u2705]", "replace": "[+]", "description": "Check mark to text"},
    "ballot-x": {"pattern": r"\u2717", "replace": "[-]", "description": "Ballot X to text"},
    "smiley": {"pattern": r"[\U0001F60A\U0001F642]", "replace": ":)", "description": "Smiley emoji to ASCII"},
    "note": {"pattern": r"\U0001F4DD", "replace": "[Note]", "description": "Note emoji to text"},
    "user": {"pattern": r"\U0001F464", "replace": "[User]", "description": "User emoji to text"},
    "robot": {"pattern": r"\U0001F916", "replace": "[Bot]", "description": "Robot emoji to text"},
    "chart": {"pattern": r"\U0001F4CA", "replace": "[Stats]", "description": "Chart emoji to text"},
}

# Code context patterns (for code blocks)
CODE_PATTERNS = {
    "math-minus": {"pattern": r"\u2212", "replace": "-", "description": "Mathematical minus to ASCII"},
    "en-dash": {"pattern": r"\u2013", "replace": "-", "description": "En dash to ASCII"},
    "em-dash": {"pattern": r"\u2014", "replace": "-", "description": "Em dash to ASCII"},
    "left-single-quote": {"pattern": r"\u2018", "replace": "'", "description": "Left single quote to ASCII"},
    "right-single-quote": {"pattern": r"\u2019", "replace": "'", "description": "Right single quote to ASCII"},
    "left-double-quote": {"pattern": r"\u201C", "replace": '"', "description": "Left double quote to ASCII"},
    "right-double-quote": {"pattern": r"\u201D", "replace": '"', "description": "Right double quote to ASCII"},
    "multiplication": {"pattern": r"\u00D7", "replace": "*", "description": "Multiplication sign to asterisk"},
    "right-arrow": {"pattern": r"\u2192", "replace": "->", "description": "Right arrow to ASCII"},
    "check-mark": {"pattern": r"[\u2713\u2705]", "replace": "[+]", "description": "Check mark to text"},
    "ballot-x": {"pattern": r"\u2717", "replace": "[-]", "description": "Ballot X to text"},
}
