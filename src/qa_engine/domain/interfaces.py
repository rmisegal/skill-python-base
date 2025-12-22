"""
Core interfaces for QA detection and fix tools.

Defines the contracts that all detectors and fixers must implement.
Follows strict separation principle from PRD Section 7.7.
"""

from abc import ABC, abstractmethod
from typing import Dict, List

from .models.issue import Issue


class DetectorInterface(ABC):
    """
    Interface for detection tools.

    MUST NOT modify content - read-only operations only.
    Returns List[Issue] containing all detected problems.

    Requirements (from PRD 7.7):
    - Single Responsibility: ONLY detect issues, never fix them
    - Stateless: No side effects, no file modifications
    - Deterministic: Same input always produces same output
    - Complete Output: Return ALL detected issues
    - No Fix Logic: NEVER contain fix patterns
    """

    @abstractmethod
    def detect(
        self,
        content: str,
        file_path: str,
        offset: int = 0,
    ) -> List[Issue]:
        """
        Detect issues in content.

        Args:
            content: The text content to analyze
            file_path: Path to the source file
            offset: Line number offset for chunked processing

        Returns:
            List of Issue objects found
        """
        pass

    @abstractmethod
    def get_rules(self) -> Dict[str, str]:
        """
        Return dict of rule_name -> description.

        Returns:
            Dictionary mapping rule names to their descriptions
        """
        pass


class FixerInterface(ABC):
    """
    Interface for fix tools.

    MUST NOT detect new issues - operates only on provided Issue list.
    Takes issues from detector and returns fixed content.

    Requirements (from PRD 7.7):
    - Single Responsibility: ONLY fix issues provided by detector
    - Issue-Driven: Operate ONLY on issues passed from detector
    - No Detection: NEVER search for issues independently
    - Targeted Changes: Only modify what's needed to fix the issue
    - Verification Ready: Output should be verifiable by re-running detector
    """

    @abstractmethod
    def fix(self, content: str, issues: List[Issue]) -> str:
        """
        Apply fixes to content based on provided issues.

        Args:
            content: The text content to fix
            issues: List of Issue objects to fix

        Returns:
            Fixed content string
        """
        pass

    @abstractmethod
    def get_patterns(self) -> Dict[str, Dict[str, str]]:
        """
        Return dict of pattern_name -> {find, replace, description}.

        Returns:
            Dictionary mapping pattern names to their definitions
        """
        pass


class CreatorInterface(ABC):
    """
    Interface for file creation tools.

    Creates actual files on disk (images, directories, etc.).
    Used when files need to be generated, not just LaTeX source modified.

    Requirements:
    - Single Responsibility: ONLY create files, not modify LaTeX source
    - File-Driven: Operate based on issue list or explicit requests
    - Idempotent: Creating same file twice should not cause errors
    - Verification Ready: Created files should be verifiable
    """

    @abstractmethod
    def create(self, path: str, **options) -> bool:
        """
        Create a file at the specified path.

        Args:
            path: Target file path
            **options: Additional options for creation

        Returns:
            True if file was created successfully
        """
        pass

    @abstractmethod
    def create_from_issues(self, issues: List[Issue]) -> Dict[str, bool]:
        """
        Create files based on detected issues.

        Args:
            issues: List of Issue objects indicating missing files

        Returns:
            Dictionary mapping file paths to creation success status
        """
        pass

    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """
        Return list of supported file formats.

        Returns:
            List of file extensions (e.g., ['.png', '.jpg', '.pdf'])
        """
        pass
