"""BC Validator interface following DetectorInterface/FixerInterface patterns."""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import threading

from ...domain.models.issue import Issue
from ...domain.interfaces import DetectorInterface, FixerInterface
from ...shared.logging import PrintManager, JsonLogger
from ...shared.threading import ResourceManager
from .config import BCConfigManager
from .result import ValidationResult, FixAttempt, BCValidationIssue


class BCValidatorInterface(ABC):
    """Abstract base class for BC validators wrapping QA detectors/fixers."""

    def __init__(
        self,
        detector: DetectorInterface,
        fixer: Optional[FixerInterface] = None,
        validator_name: Optional[str] = None,
    ) -> None:
        """Initialize validator with detector and optional fixer."""
        self._detector = detector
        self._fixer = fixer
        self._name = validator_name or self.__class__.__name__
        self._config = BCConfigManager()
        self._logger = PrintManager()
        self._json_logger = JsonLogger()
        self._resource_manager = ResourceManager()
        self._lock = threading.Lock()

    @property
    def name(self) -> str:
        return self._name

    @property
    def enabled(self) -> bool:
        return self._config.get(f"validators.{self._name}.enabled", True)

    @property
    def rules(self) -> List[str]:
        return self._config.get(f"validators.{self._name}.rules", [])

    @property
    def auto_fix_rules(self) -> List[str]:
        return self._config.get(f"validators.{self._name}.auto_fix_rules", [])

    @property
    def block_on_critical(self) -> bool:
        return self._config.get(f"validators.{self._name}.block_on_critical", True)

    def validate(self, content: str, file_path: str = "inline") -> ValidationResult:
        """Validate content and return result."""
        if not self.enabled:
            return ValidationResult(self._name, content, True)

        all_issues = self._detector.detect(content, file_path)
        issues = [i for i in all_issues if i.rule in self.rules]

        if not issues:
            return ValidationResult(self._name, content, True)

        return ValidationResult(
            self._name, content, False, issues=issues, unfixable_issues=issues.copy()
        )

    def validate_and_fix(self, content: str, file_path: str = "inline") -> ValidationResult:
        """Validate content and auto-fix where possible."""
        if not self.enabled:
            return ValidationResult(self._name, content, True)

        all_issues = self._detector.detect(content, file_path)
        issues = [i for i in all_issues if i.rule in self.rules]

        if not issues:
            return ValidationResult(self._name, content, True)

        fixable = [i for i in issues if i.rule in self.auto_fix_rules]
        unfixable = [i for i in issues if i.rule not in self.auto_fix_rules]

        fixed_content = content
        fix_attempts: List[FixAttempt] = []

        if self._fixer and fixable:
            try:
                fixed_content = self._fixer.fix(content, fixable)
                fix_attempts = [
                    FixAttempt(i.rule, True, i.content, "[auto-fixed]")
                    for i in fixable
                ]
            except Exception as e:
                self._logger.error(f"Fix failed: {e}")
                fix_attempts = [
                    FixAttempt(i.rule, False, i.content, error=str(e))
                    for i in fixable
                ]
                unfixable.extend(fixable)

        return ValidationResult(
            self._name,
            fixed_content,
            len(unfixable) == 0,
            issues=issues,
            fixed_issues=fix_attempts,
            unfixable_issues=unfixable,
        )

    @abstractmethod
    def get_rules(self) -> Dict[str, str]:
        """Return rule name -> description mapping."""
        pass
