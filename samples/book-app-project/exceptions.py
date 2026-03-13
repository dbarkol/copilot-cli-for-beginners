"""Custom exceptions for the book collection app.

Hierarchy:
    BookAppError
    ├── ValidationError      — invalid input data
    ├── BookNotFoundError    — book lookup failed
    └── StorageError         — load/save failure
"""


class BookAppError(Exception):
    """Base exception for the book collection app."""


class ValidationError(BookAppError):
    """Raised when input data is invalid."""


class BookNotFoundError(BookAppError):
    """Raised when a book lookup fails."""


class StorageError(BookAppError):
    """Raised when loading or saving book data fails."""
