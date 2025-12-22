"""
Dependency Injection container module.

Provides a simple DI container for managing service dependencies.
"""

from __future__ import annotations

from threading import Lock
from typing import Any, Callable, Dict, Optional, Type, TypeVar

T = TypeVar("T")


class DIError(Exception):
    """Raised when DI registration or resolution fails."""


class DIContainer:
    """
    Thread-safe singleton dependency injection container.

    Supports both singleton and transient service lifetimes.
    """

    _instance: Optional[DIContainer] = None
    _lock: Lock = Lock()

    def __new__(cls) -> DIContainer:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._registrations: Dict[str, Dict[str, Any]] = {}
        self._singletons: Dict[str, Any] = {}
        self._container_lock = Lock()
        self._initialized = True

    def register(
        self,
        interface: Type[T],
        factory: Callable[[], T],
        singleton: bool = True,
    ) -> None:
        """
        Register a service factory.

        Args:
            interface: The type/interface to register
            factory: Factory function that creates the service
            singleton: If True, only one instance is created
        """
        key = self._get_key(interface)
        with self._container_lock:
            self._registrations[key] = {
                "factory": factory,
                "singleton": singleton,
            }

    def register_instance(self, interface: Type[T], instance: T) -> None:
        """
        Register an existing instance as a singleton.

        Args:
            interface: The type/interface to register
            instance: The instance to register
        """
        key = self._get_key(interface)
        with self._container_lock:
            self._registrations[key] = {
                "factory": lambda: instance,
                "singleton": True,
            }
            self._singletons[key] = instance

    def resolve(self, interface: Type[T]) -> T:
        """
        Resolve a service by its interface.

        Args:
            interface: The type/interface to resolve

        Returns:
            The service instance

        Raises:
            DIError: If service is not registered
        """
        key = self._get_key(interface)
        with self._container_lock:
            if key not in self._registrations:
                raise DIError(f"Service not registered: {interface.__name__}")

            registration = self._registrations[key]

            if registration["singleton"]:
                if key not in self._singletons:
                    self._singletons[key] = registration["factory"]()
                return self._singletons[key]

            return registration["factory"]()

    def is_registered(self, interface: Type[T]) -> bool:
        """Check if a service is registered."""
        key = self._get_key(interface)
        with self._container_lock:
            return key in self._registrations

    def _get_key(self, interface: Type[Any]) -> str:
        """Generate unique key for interface type."""
        return f"{interface.__module__}.{interface.__name__}"

    @classmethod
    def reset(cls) -> None:
        """Reset singleton instance (for testing)."""
        with cls._lock:
            if cls._instance is not None:
                cls._instance._registrations.clear()
                cls._instance._singletons.clear()
            cls._instance = None
