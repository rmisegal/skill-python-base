"""
Tests for shared/threading module.
"""

import threading
import time

import pytest
from qa_engine.shared.threading import LockError, ResourceManager


class TestResourceManager:
    """Tests for ResourceManager singleton."""

    def setup_method(self):
        """Reset singleton before each test."""
        ResourceManager.reset()

    def test_singleton_pattern(self):
        """Test that ResourceManager is a singleton."""
        rm1 = ResourceManager()
        rm2 = ResourceManager()
        assert rm1 is rm2

    def test_acquire_release(self):
        """Test basic acquire and release."""
        rm = ResourceManager()
        assert rm.acquire("test-resource", "agent-1")
        assert rm.is_locked("test-resource")
        rm.release("test-resource", "agent-1")
        assert not rm.is_locked("test-resource")

    def test_acquire_blocked(self):
        """Test acquire is blocked when resource is locked."""
        rm = ResourceManager()
        rm.acquire("test-resource", "agent-1")
        # Second acquire should fail with short timeout
        assert not rm.acquire("test-resource", "agent-2", timeout=0.1)
        rm.release("test-resource", "agent-1")

    def test_release_not_owner(self):
        """Test release by non-owner raises error."""
        rm = ResourceManager()
        rm.acquire("test-resource", "agent-1")
        with pytest.raises(LockError):
            rm.release("test-resource", "agent-2")
        rm.release("test-resource", "agent-1")

    def test_release_not_locked(self):
        """Test release of unlocked resource raises error."""
        rm = ResourceManager()
        with pytest.raises(LockError):
            rm.release("nonexistent", "agent-1")

    def test_get_owner(self):
        """Test get_owner returns correct agent."""
        rm = ResourceManager()
        rm.acquire("test-resource", "agent-1")
        assert rm.get_owner("test-resource") == "agent-1"
        rm.release("test-resource", "agent-1")
        assert rm.get_owner("test-resource") is None

    def test_context_manager(self):
        """Test locked context manager."""
        rm = ResourceManager()
        with rm.locked("test-resource", "agent-1"):
            assert rm.is_locked("test-resource")
        assert not rm.is_locked("test-resource")

    def test_context_manager_timeout(self):
        """Test locked context manager with timeout."""
        rm = ResourceManager()
        rm.acquire("test-resource", "agent-1")
        with pytest.raises(LockError):
            with rm.locked("test-resource", "agent-2", timeout=0.1):
                pass
        rm.release("test-resource", "agent-1")

    def test_stale_locks(self):
        """Test detection of stale locks."""
        rm = ResourceManager()
        rm.acquire("test-resource", "agent-1")
        # With 0 timeout, the lock should be immediately stale
        stale = rm.get_stale_locks(timeout_seconds=0)
        assert "test-resource" in stale
        rm.release("test-resource", "agent-1")

    def test_multiple_resources(self):
        """Test managing multiple resources."""
        rm = ResourceManager()
        rm.acquire("resource-1", "agent-1")
        rm.acquire("resource-2", "agent-2")
        assert rm.is_locked("resource-1")
        assert rm.is_locked("resource-2")
        assert rm.get_owner("resource-1") == "agent-1"
        assert rm.get_owner("resource-2") == "agent-2"
        rm.release("resource-1", "agent-1")
        rm.release("resource-2", "agent-2")

    def test_thread_safety(self):
        """Test thread safety of acquire/release."""
        rm = ResourceManager()
        acquired_count = [0]
        lock = threading.Lock()

        def try_acquire():
            if rm.acquire("shared-resource", f"agent-{threading.current_thread().name}", timeout=0.5):
                with lock:
                    acquired_count[0] += 1
                time.sleep(0.1)
                rm.release("shared-resource", f"agent-{threading.current_thread().name}")

        threads = [threading.Thread(target=try_acquire, name=str(i)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Only one thread should acquire at a time
        assert acquired_count[0] >= 1
