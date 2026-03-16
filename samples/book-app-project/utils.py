from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from exceptions import ValidationError

if TYPE_CHECKING:
    from books import Book

MIN_YEAR = 1000


# ---------------------------------------------------------------------------
# Pure validation / formatting helpers (no I/O)
# ---------------------------------------------------------------------------

def validate_year(year: int) -> int:
    """Validate that *year* is within the acceptable range.

    Returns the year unchanged if valid, otherwise raises
    :class:`ValidationError`.  The upper bound is the current
    calendar year so the check stays correct without hard-coding.
    """
    max_year = datetime.date.today().year
    if year < MIN_YEAR or year > max_year:
        raise ValidationError(
            f"Year must be between {MIN_YEAR} and {max_year}."
        )
    return year


def validate_menu_choice(choice: str) -> str | None:
    """Return the choice if valid (digit 1-5), or None."""
    if choice.isdigit() and 1 <= int(choice) <= 5:
        return choice
    return None


def parse_year(value: str) -> int | None:
    """Parse a year string. Return int on success, None on failure."""
    try:
        return int(value)
    except ValueError:
        return None


def format_book_line(book: Book, index: int) -> str:
    """Format a single book as a compact CLI line."""
    status = "✓" if book.read else " "
    return f"{index}. [{status}] {book.title} by {book.author} ({book.year})"


def format_book_detail(book: Book, index: int) -> str:
    """Format a single book with emoji status."""
    status = "✅ Read" if book.read else "📖 Unread"
    return f"{index}. {book.title} by {book.author} ({book.year}) - {status}"


# ---------------------------------------------------------------------------
# Display functions (output only — no logic)
# ---------------------------------------------------------------------------

def print_menu() -> None:
    print("\n📚 Book Collection App")
    print("1. Add a book")
    print("2. List books")
    print("3. Mark book as read")
    print("4. Remove a book")
    print("5. Exit")


def show_books(books: list[Book]) -> None:
    """Display books in a user-friendly format."""
    if not books:
        print("No books found.")
        return

    print("\nYour Book Collection:\n")
    for index, book in enumerate(books, start=1):
        print(format_book_line(book, index))
    print()


def print_books(books: list[Book]) -> None:
    if not books:
        print("No books in your collection.")
        return

    print("\nYour Books:")
    for index, book in enumerate(books, start=1):
        print(format_book_detail(book, index))


# ---------------------------------------------------------------------------
# Interactive input functions (I/O wrappers using validators above)
# ---------------------------------------------------------------------------

def get_user_choice() -> str:
    """Prompt for a menu choice, re-prompting on invalid input."""
    while True:
        raw = input("Choose an option (1-5): ").strip()
        if not raw:
            print("No input provided. Please enter a number between 1 and 5.")
            continue
        choice = validate_menu_choice(raw)
        if choice is None:
            print(f"Invalid choice: '{raw}'. Please enter a number between 1 and 5.")
            continue
        return choice


def get_book_details() -> tuple[str, str, int]:
    """Interactively prompt the user for book details.

    Title and author are required and will re-prompt until non-empty.
    Year must be a valid integer between :data:`MIN_YEAR` and the current
    year; the prompt repeats until a valid value is entered.

    Returns:
        tuple: (title, author, year)
    """
    while True:
        title = input("Enter book title: ").strip()
        if title:
            break
        print("Title cannot be empty. Please enter a book title.")

    while True:
        author = input("Enter author: ").strip()
        if author:
            break
        print("Author cannot be empty. Please enter an author name.")

    max_year = datetime.date.today().year
    while True:
        year_input = input("Enter publication year: ").strip()
        year = parse_year(year_input)
        if year is None:
            print("Please enter a valid number.")
            continue
        try:
            validate_year(year)
            break
        except ValidationError as e:
            print(f"{e}")

    return title, author, year
