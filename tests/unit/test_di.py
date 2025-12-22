"""
Tests for shared/di module.
"""

from abc import ABC, abstractmethod

import pytest
from qa_engine.shared.di import DIContainer, DIError


class IService(ABC):
    """Test interface."""

    @abstractmethod
    def get_value(self) -> str:
        pass


class ServiceImpl(IService):
    """Test implementation."""

    def __init__(self, value: str = "default"):
        self._value = value

    def get_value(self) -> str:
        return self._value


class TestDIContainer:
    """Tests for DIContainer singleton."""

    def setup_method(self):
        """Reset singleton before each test."""
        DIContainer.reset()

    def test_singleton_pattern(self):
        """Test that DIContainer is a singleton."""
        di1 = DIContainer()
        di2 = DIContainer()
        assert di1 is di2

    def test_register_and_resolve(self):
        """Test basic registration and resolution."""
        di = DIContainer()
        di.register(IService, lambda: ServiceImpl("test"))
        service = di.resolve(IService)
        assert service.get_value() == "test"

    def test_singleton_lifetime(self):
        """Test singleton services return same instance."""
        di = DIContainer()
        di.register(IService, lambda: ServiceImpl("test"), singleton=True)
        service1 = di.resolve(IService)
        service2 = di.resolve(IService)
        assert service1 is service2

    def test_transient_lifetime(self):
        """Test transient services return new instances."""
        di = DIContainer()
        di.register(IService, lambda: ServiceImpl("test"), singleton=False)
        service1 = di.resolve(IService)
        service2 = di.resolve(IService)
        assert service1 is not service2

    def test_register_instance(self):
        """Test registering existing instance."""
        di = DIContainer()
        instance = ServiceImpl("existing")
        di.register_instance(IService, instance)
        resolved = di.resolve(IService)
        assert resolved is instance

    def test_resolve_not_registered(self):
        """Test resolving unregistered service raises error."""
        di = DIContainer()
        with pytest.raises(DIError):
            di.resolve(IService)

    def test_is_registered(self):
        """Test is_registered method."""
        di = DIContainer()
        assert di.is_registered(IService) is False
        di.register(IService, lambda: ServiceImpl("test"))
        assert di.is_registered(IService) is True

    def test_override_registration(self):
        """Test overriding registration."""
        di = DIContainer()
        di.register(IService, lambda: ServiceImpl("first"))
        di.register(IService, lambda: ServiceImpl("second"))
        service = di.resolve(IService)
        assert service.get_value() == "second"

    def test_multiple_types(self):
        """Test registering multiple types."""

        class IAnother(ABC):
            @abstractmethod
            def get_name(self) -> str:
                pass

        class AnotherImpl(IAnother):
            def get_name(self) -> str:
                return "another"

        di = DIContainer()
        di.register(IService, lambda: ServiceImpl("service"))
        di.register(IAnother, lambda: AnotherImpl())

        service = di.resolve(IService)
        another = di.resolve(IAnother)

        assert service.get_value() == "service"
        assert another.get_name() == "another"
