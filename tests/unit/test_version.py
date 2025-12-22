"""
Tests for shared/version module.
"""

import pytest
from qa_engine.shared.version import SemanticVersion, VersionManager


class TestSemanticVersion:
    """Tests for SemanticVersion dataclass."""

    def test_parse_valid_version(self):
        """Test parsing valid version string."""
        version = SemanticVersion.parse("1.2.3")
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3

    def test_parse_invalid_version(self):
        """Test parsing invalid version string raises ValueError."""
        with pytest.raises(ValueError):
            SemanticVersion.parse("invalid")

    def test_parse_partial_version(self):
        """Test parsing partial version raises ValueError."""
        with pytest.raises(ValueError):
            SemanticVersion.parse("1.2")

    def test_str_representation(self):
        """Test string representation."""
        version = SemanticVersion(1, 2, 3)
        assert str(version) == "1.2.3"

    def test_comparison_less_than(self):
        """Test version comparison less than."""
        v1 = SemanticVersion(1, 0, 0)
        v2 = SemanticVersion(2, 0, 0)
        assert v1 < v2

    def test_comparison_equal(self):
        """Test version comparison equal."""
        v1 = SemanticVersion(1, 2, 3)
        v2 = SemanticVersion(1, 2, 3)
        assert v1 == v2

    def test_comparison_minor(self):
        """Test minor version comparison."""
        v1 = SemanticVersion(1, 1, 0)
        v2 = SemanticVersion(1, 2, 0)
        assert v1 < v2


class TestVersionManager:
    """Tests for VersionManager singleton."""

    def setup_method(self):
        """Reset singleton before each test."""
        VersionManager.reset()

    def test_singleton_pattern(self):
        """Test that VersionManager is a singleton."""
        vm1 = VersionManager()
        vm2 = VersionManager()
        assert vm1 is vm2

    def test_default_version(self):
        """Test default version is 1.0.0."""
        vm = VersionManager()
        assert vm.version_string == "1.0.0"

    def test_set_version(self):
        """Test setting version from string."""
        vm = VersionManager()
        vm.set_version("2.1.0")
        assert vm.version_string == "2.1.0"

    def test_is_compatible_true(self):
        """Test compatibility check when version meets requirement."""
        vm = VersionManager()
        vm.set_version("2.0.0")
        assert vm.is_compatible("1.0.0") is True

    def test_is_compatible_false(self):
        """Test compatibility check when version doesn't meet requirement."""
        vm = VersionManager()
        vm.set_version("1.0.0")
        assert vm.is_compatible("2.0.0") is False

    def test_is_compatible_equal(self):
        """Test compatibility check with equal versions."""
        vm = VersionManager()
        vm.set_version("1.5.0")
        assert vm.is_compatible("1.5.0") is True
