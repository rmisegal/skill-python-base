"""
QA-compliant code block templates for BC content generation.

All templates pass these QA rules:
- code-background-overflow: pythonbox wrapped in english environment
- code-direction-hebrew: No Hebrew in code
- code-encoding-emoji: No emoji characters
- code-syntax: Uses [title] not {title} for pythonbox

CRITICAL: pythonbox uses SQUARE BRACKETS for title: \\begin{pythonbox}[Title]
         NOT curly braces: \\begin{pythonbox}{Title} <- WRONG!
"""


class CodeTemplates:
    """QA-compliant code block templates."""

    @staticmethod
    def python_code(
        title_eng: str,
        code: str,
        long_block: bool = False,
    ) -> str:
        """
        Generate a QA-compliant Python code block.

        CRITICAL: pythonbox must be wrapped in english environment
        and use SQUARE BRACKETS for title (not curly braces).

        Args:
            title_eng: English title for the code block (NOT Hebrew!)
            code: Python code (must be English only, no emoji)
            long_block: Use pythonbox* for long blocks

        Returns:
            LaTeX code for pythonbox wrapped in english environment
        """
        env = "pythonbox*" if long_block else "pythonbox"
        # CRITICAL: Use square brackets [title] NOT curly braces {title}
        # CRITICAL: Wrap in english environment for RTL documents
        return f"""\\begin{{english}}
\\begin{{{env}}}[{title_eng}]
{code}
\\end{{{env}}}
\\end{{english}}"""

    @staticmethod
    def python_function(
        title_eng: str,
        func_name: str,
        args: list,
        docstring: str,
        body: str,
        returns: str = None,
    ) -> str:
        """
        Generate a Python function code block.

        Args:
            title_eng: English title (NOT Hebrew - code blocks use English)
            func_name: Function name
            args: List of (arg_name, type_hint) tuples
            docstring: Function docstring
            body: Function body code
            returns: Optional return type

        Returns:
            LaTeX code for function block wrapped in english environment
        """
        # Build args string
        args_str = ", ".join([f"{name}: {typ}" for name, typ in args])
        return_hint = f" -> {returns}" if returns else ""

        code = f'''def {func_name}({args_str}){return_hint}:
    """
    {docstring}
    """
    {body}'''

        return CodeTemplates.python_code(title_eng, code)

    @staticmethod
    def python_class(
        title_eng: str,
        class_name: str,
        docstring: str,
        methods: list,
    ) -> str:
        """
        Generate a Python class code block.

        Args:
            title_eng: English title (NOT Hebrew - code blocks use English)
            class_name: Class name
            docstring: Class docstring
            methods: List of method code strings

        Returns:
            LaTeX code for class block wrapped in english environment
        """
        methods_code = "\n\n    ".join(methods)
        code = f'''class {class_name}:
    """
    {docstring}
    """

    {methods_code}'''

        return CodeTemplates.python_code(title_eng, code, long_block=True)

    @staticmethod
    def pseudocode(
        title_eng: str,
        algorithm: str,
    ) -> str:
        """
        Generate pseudocode block.

        Args:
            title_eng: English title (NOT Hebrew - code blocks use English)
            algorithm: Pseudocode algorithm (English)

        Returns:
            LaTeX code for pseudocode block wrapped in english environment
        """
        # CRITICAL: Wrap in english environment and use square brackets
        return f"""\\begin{{english}}
\\begin{{pythonbox}}[{title_eng}]
# Pseudocode
{algorithm}
\\end{{pythonbox}}
\\end{{english}}"""

    @staticmethod
    def numpy_example(
        title_eng: str,
        description: str,
        operations: list,
    ) -> str:
        """
        Generate NumPy example code block.

        Args:
            title_eng: English title (NOT Hebrew - code blocks use English)
            description: English comment describing the example
            operations: List of NumPy operation lines

        Returns:
            LaTeX code for NumPy example wrapped in english environment
        """
        ops_code = "\n".join(operations)
        code = f'''import numpy as np

# {description}
{ops_code}'''

        return CodeTemplates.python_code(title_eng, code)
