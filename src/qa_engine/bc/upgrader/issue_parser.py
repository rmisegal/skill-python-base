"""Issue parser for BC-QA upgrader."""

import re
from typing import List
from .models import ParsedIssue, IssueCategory


class IssueParser:
    """Parse issue IDs from command arguments."""

    CATEGORY_PATTERN = re.compile(
        r"^(BIDI|CODE|TABLE|BIB|IMG|TYPE)-(\d{3})$",
        re.IGNORECASE
    )

    def parse(self, issues_arg: str) -> List[ParsedIssue]:
        """Parse comma-separated issue IDs."""
        issues = []
        raw_ids = [s.strip() for s in issues_arg.split(",")]

        for raw_id in raw_ids:
            if not raw_id:
                continue
            parsed = self._parse_single(raw_id.upper())
            if parsed:
                issues.append(parsed)

        return issues

    def _parse_single(self, issue_id: str) -> ParsedIssue | None:
        """Parse a single issue ID."""
        match = self.CATEGORY_PATTERN.match(issue_id)
        if not match:
            return None

        category_str, number_str = match.groups()
        try:
            category = IssueCategory(category_str)
            number = int(number_str)
        except (ValueError, KeyError):
            return None

        return ParsedIssue(
            issue_id=issue_id,
            category=category,
            number=number
        )

    def validate(self, issues: List[ParsedIssue]) -> List[str]:
        """Validate parsed issues, return error messages."""
        errors = []
        if not issues:
            errors.append("No valid issues provided")
        return errors
