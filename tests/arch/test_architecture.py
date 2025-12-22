"""
Architecture tests for QA Engine.

Validates:
1. Project structure follows mandatory layout
2. Dependency rules between layers
3. Singleton patterns
4. File size constraints
"""

import ast
from pathlib import Path

import pytest


# Get project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
SRC_ROOT = PROJECT_ROOT / "src" / "qa_engine"


class TestProjectStructure:
    """Tests for mandatory project structure."""

    def test_src_directory_exists(self):
        """Test that src directory exists."""
        assert SRC_ROOT.exists()

    def test_shared_directory_exists(self):
        """Test that shared directory exists."""
        assert (SRC_ROOT / "shared").exists()

    def test_domain_directory_exists(self):
        """Test that domain directory exists."""
        assert (SRC_ROOT / "domain").exists()

    def test_infrastructure_directory_exists(self):
        """Test that infrastructure directory exists."""
        assert (SRC_ROOT / "infrastructure").exists()

    def test_sdk_directory_exists(self):
        """Test that sdk directory exists."""
        assert (SRC_ROOT / "sdk").exists()

    def test_config_directory_exists(self):
        """Test that config directory exists."""
        assert (PROJECT_ROOT / "config").exists()

    def test_tests_directory_exists(self):
        """Test that tests directory exists."""
        assert (PROJECT_ROOT / "tests").exists()


class TestSharedModules:
    """Tests for required shared modules."""

    def test_config_module_exists(self):
        """Test config.py exists in shared."""
        assert (SRC_ROOT / "shared" / "config.py").exists()

    def test_logging_module_exists(self):
        """Test logging.py exists in shared."""
        assert (SRC_ROOT / "shared" / "logging.py").exists()

    def test_version_module_exists(self):
        """Test version.py exists in shared."""
        assert (SRC_ROOT / "shared" / "version.py").exists()

    def test_threading_module_exists(self):
        """Test threading.py exists in shared."""
        assert (SRC_ROOT / "shared" / "threading.py").exists()

    def test_di_module_exists(self):
        """Test di.py exists in shared."""
        assert (SRC_ROOT / "shared" / "di.py").exists()


class TestDomainModules:
    """Tests for required domain modules."""

    def test_models_directory_exists(self):
        """Test models directory exists."""
        assert (SRC_ROOT / "domain" / "models").exists()

    def test_services_directory_exists(self):
        """Test services directory exists."""
        assert (SRC_ROOT / "domain" / "services").exists()

    def test_interfaces_module_exists(self):
        """Test interfaces.py exists."""
        assert (SRC_ROOT / "domain" / "interfaces.py").exists()


class TestInfrastructureModules:
    """Tests for required infrastructure modules."""

    def test_coordination_directory_exists(self):
        """Test coordination directory exists."""
        assert (SRC_ROOT / "infrastructure" / "coordination").exists()

    def test_detection_directory_exists(self):
        """Test detection directory exists."""
        assert (SRC_ROOT / "infrastructure" / "detection").exists()

    def test_fixing_directory_exists(self):
        """Test fixing directory exists."""
        assert (SRC_ROOT / "infrastructure" / "fixing").exists()


class TestFileSizeConstraints:
    """Tests for file size constraints (max 250 lines for complex modules)."""

    MAX_LINES = 250

    def get_python_files(self):
        """Get all Python files in src directory."""
        return list(SRC_ROOT.rglob("*.py"))

    def count_lines(self, file_path: Path) -> int:
        """Count non-empty, non-comment lines in a file."""
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return len([l for l in lines if l.strip() and not l.strip().startswith("#")])

    def test_all_files_under_max_lines(self):
        """Test all Python files are under max line limit."""
        violations = []
        for py_file in self.get_python_files():
            line_count = self.count_lines(py_file)
            if line_count > self.MAX_LINES:
                violations.append(f"{py_file.name}: {line_count} lines")

        if violations:
            pytest.fail(
                f"Files exceeding {self.MAX_LINES} lines:\n" + "\n".join(violations)
            )


class TestSingletonPatterns:
    """Tests for singleton pattern implementation."""

    def test_config_manager_singleton(self):
        """Test ConfigManager is a singleton."""
        from qa_engine.shared.config import ConfigManager

        cm1 = ConfigManager()
        cm2 = ConfigManager()
        assert cm1 is cm2
        ConfigManager.reset()

    def test_version_manager_singleton(self):
        """Test VersionManager is a singleton."""
        from qa_engine.shared.version import VersionManager

        vm1 = VersionManager()
        vm2 = VersionManager()
        assert vm1 is vm2
        VersionManager.reset()

    def test_resource_manager_singleton(self):
        """Test ResourceManager is a singleton."""
        from qa_engine.shared.threading import ResourceManager

        rm1 = ResourceManager()
        rm2 = ResourceManager()
        assert rm1 is rm2
        ResourceManager.reset()

    def test_di_container_singleton(self):
        """Test DIContainer is a singleton."""
        from qa_engine.shared.di import DIContainer

        di1 = DIContainer()
        di2 = DIContainer()
        assert di1 is di2
        DIContainer.reset()


class TestDependencyRules:
    """Tests for layer dependency rules."""

    def get_imports(self, file_path: Path) -> list:
        """Parse file and extract import statements."""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        try:
            tree = ast.parse(content)
        except SyntaxError:
            return []

        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

        return imports

    def test_shared_no_domain_imports(self):
        """Test shared layer doesn't import from domain."""
        shared_files = list((SRC_ROOT / "shared").rglob("*.py"))
        violations = []

        for py_file in shared_files:
            imports = self.get_imports(py_file)
            domain_imports = [i for i in imports if "domain" in i]
            if domain_imports:
                violations.append(f"{py_file.name}: {domain_imports}")

        if violations:
            pytest.fail(
                "Shared layer should not import from domain:\n" + "\n".join(violations)
            )

    def test_shared_no_infrastructure_imports(self):
        """Test shared layer doesn't import from infrastructure."""
        shared_files = list((SRC_ROOT / "shared").rglob("*.py"))
        violations = []

        for py_file in shared_files:
            imports = self.get_imports(py_file)
            infra_imports = [i for i in imports if "infrastructure" in i]
            if infra_imports:
                violations.append(f"{py_file.name}: {infra_imports}")

        if violations:
            pytest.fail(
                "Shared layer should not import from infrastructure:\n"
                + "\n".join(violations)
            )

    def test_domain_no_infrastructure_imports(self):
        """Test domain layer doesn't import from infrastructure."""
        domain_files = list((SRC_ROOT / "domain").rglob("*.py"))
        violations = []

        for py_file in domain_files:
            imports = self.get_imports(py_file)
            infra_imports = [i for i in imports if "infrastructure" in i]
            if infra_imports:
                violations.append(f"{py_file.name}: {infra_imports}")

        if violations:
            pytest.fail(
                "Domain layer should not import from infrastructure:\n"
                + "\n".join(violations)
            )

    def test_domain_no_sdk_imports(self):
        """Test domain layer doesn't import from sdk."""
        domain_files = list((SRC_ROOT / "domain").rglob("*.py"))
        violations = []

        for py_file in domain_files:
            imports = self.get_imports(py_file)
            sdk_imports = [i for i in imports if "sdk" in i]
            if sdk_imports:
                violations.append(f"{py_file.name}: {sdk_imports}")

        if violations:
            pytest.fail(
                "Domain layer should not import from sdk:\n" + "\n".join(violations)
            )
