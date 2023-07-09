"""Test fixtures and utilities."""
from contextlib import contextmanager


@contextmanager
def does_not_raise():
    """No-op context manager to compliment pytest.raises.

    Yields:
        None
    """
    yield
