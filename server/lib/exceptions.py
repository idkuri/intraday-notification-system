from __future__ import annotations


class NotFoundError(Exception):
    """Raised when a requested entity does not exist."""


class DomainValidationError(Exception):
    """Raised when a domain rule rejects input."""
