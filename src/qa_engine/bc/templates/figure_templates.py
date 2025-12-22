"""
QA-compliant figure templates for BC content generation.

All templates pass these QA rules:
- img-empty-figure: Always has includegraphics or tikzpicture
- bidi-tikz-rtl: TikZ wrapped in english environment

CRITICAL TikZ RULES - DO NOT VIOLATE:
=====================================
TikZ code is ALREADY in LTR/English context (wrapped in \\begin{english}).
Therefore, TikZ code must NEVER contain:
- \\en{} wrappers - BREAKS TikZ parsing
- \\num{} wrappers - BREAKS coordinate parsing
- \\textenglish{} - BREAKS node names
- Hebrew text - use \\texthebrew{} ONLY in node content, not in commands

WRONG (will cause compilation failure):
    \\node[\\en{block}] (\\en{input}) \\en{at} (\\num{0}, \\num{0}) {...}

CORRECT:
    \\node[block] (input) at (0, 0) {...}

For Hebrew labels inside nodes, use:
    \\node[block] (input) at (0,0) {Input\\\\\\scriptsize \\texthebrew{קלט}};
"""

from typing import Optional


class FigureTemplates:
    """QA-compliant figure templates."""

    @staticmethod
    def image_figure(
        caption: str,
        label: str,
        image_path: str,
        width: str = "0.8\\textwidth",
    ) -> str:
        """
        Generate a QA-compliant figure with image.

        Args:
            caption: Hebrew caption
            label: LaTeX label (e.g., 'fig:example')
            image_path: Path to image file
            width: Image width specification

        Returns:
            LaTeX code for figure with image
        """
        return f"""\\begin{{hebrewfigure}}
\\centering
\\includegraphics[width={width}]{{{image_path}}}
\\caption{{{caption}}}
\\label{{{label}}}
\\end{{hebrewfigure}}"""

    @staticmethod
    def tikz_figure(
        caption: str,
        label: str,
        tikz_code: str,
    ) -> str:
        """
        Generate a QA-compliant figure with TikZ diagram.
        TikZ is wrapped in english environment for correct LTR rendering.

        Args:
            caption: Hebrew caption
            label: LaTeX label
            tikz_code: TikZ drawing code (without begin/end tikzpicture)

        Returns:
            LaTeX code for figure with TikZ
        """
        return f"""\\begin{{hebrewfigure}}
\\centering
\\begin{{english}}
\\begin{{tikzpicture}}
{tikz_code}
\\end{{tikzpicture}}
\\end{{english}}
\\caption{{{caption}}}
\\label{{{label}}}
\\end{{hebrewfigure}}"""

    @staticmethod
    def placeholder_figure(
        caption: str,
        label: str,
        description: str,
        width: str = "0.8\\textwidth",
        height: str = "5cm",
    ) -> str:
        """
        Generate a placeholder figure with description.
        Uses TikZ to create a labeled placeholder box.

        Args:
            caption: Hebrew caption
            label: LaTeX label
            description: English description of what image should show
            width: Box width
            height: Box height

        Returns:
            LaTeX code for placeholder figure
        """
        # Use TikZ to create a proper placeholder (not empty figure)
        return f"""\\begin{{hebrewfigure}}
\\centering
\\begin{{english}}
\\begin{{tikzpicture}}
\\draw[thick, dashed] (0,0) rectangle (10,5);
\\node[align=center] at (5,2.5) {{{description}}};
\\end{{tikzpicture}}
\\end{{english}}
\\caption{{{caption}}}
\\label{{{label}}}
\\end{{hebrewfigure}}"""

    @staticmethod
    def flowchart_figure(
        caption: str,
        label: str,
        nodes: list,
        connections: list,
    ) -> str:
        """
        Generate a flowchart figure using TikZ.

        Args:
            caption: Hebrew caption
            label: LaTeX label
            nodes: List of (id, x, y, text) tuples
            connections: List of (from_id, to_id, label) tuples

        Returns:
            LaTeX code for flowchart figure
        """
        tikz_lines = ["\\tikzstyle{block} = [rectangle, draw, minimum width=2.5cm, minimum height=1cm, align=center]"]
        tikz_lines.append("\\tikzstyle{arrow} = [thick,->,>=stealth]")

        # Add nodes
        for node_id, x, y, text in nodes:
            tikz_lines.append(f"\\node[block] ({node_id}) at ({x},{y}) {{{text}}};")

        # Add connections
        for from_id, to_id, edge_label in connections:
            if edge_label:
                tikz_lines.append(f"\\draw[arrow] ({from_id}) -- node[above] {{{edge_label}}} ({to_id});")
            else:
                tikz_lines.append(f"\\draw[arrow] ({from_id}) -- ({to_id});")

        tikz_code = "\n".join(tikz_lines)
        return FigureTemplates.tikz_figure(caption, label, tikz_code)
