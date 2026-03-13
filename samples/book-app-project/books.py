import json
from dataclasses import dataclass, asdict
from typing import List, Optional

from exceptions import BookNotFoundError, StorageError, ValidationError

DATA_FILE = "data.json"


@dataclass
class Book:
    title: str
    author: str
    year: int
    read: bool = False


class BookCollection:
    def __init__(self):
        self.books: List[Book] = []
        self.load_books()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.save_books()
        return False

    def load_books(self):
        """Load books from the JSON file if it exists."""
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                self.books = [Book(**b) for b in data]
        except FileNotFoundError:
            self.books = []
        except json.JSONDecodeError as e:
            raise StorageError(
                f"data.json is corrupted and could not be read: {e}"
            ) from e

    def save_books(self):
        """Save the current book collection to JSON."""
        try:
            with open(DATA_FILE, "w") as f:
                json.dump([asdict(b) for b in self.books], f, indent=2)
        except OSError as e:
            raise StorageError(f"Could not save to {DATA_FILE}: {e}") from e

    def add_book(self, title: str, author: str, year: int) -> Book:
        if not title or not title.strip():
            raise ValidationError("Title cannot be empty.")
        if not author or not author.strip():
            raise ValidationError("Author cannot be empty.")

        book = Book(title=title.strip(), author=author.strip(), year=year)
        self.books.append(book)
        return book

    def list_books(self) -> List[Book]:
        return self.books

    def find_book_by_title(self, title: str) -> Optional[Book]:
        for book in self.books:
            if book.title.lower() == title.lower():
                return book
        return None

    def mark_as_read(self, title: str) -> None:
        book = self.find_book_by_title(title)
        if not book:
            raise BookNotFoundError(f"No book found with title '{title}'.")
        book.read = True

    def remove_book(self, title: str) -> None:
        """Remove a book by title."""
        book = self.find_book_by_title(title)
        if not book:
            raise BookNotFoundError(f"No book found with title '{title}'.")
        self.books.remove(book)

    def find_by_author(self, author: str) -> List[Book]:
        """Find all books by a given author."""
        return [b for b in self.books if b.author.lower() == author.lower()]

    def search_books(self, query: str) -> List[Book]:
        """Search books by partial match on title or author."""
        query_lower = query.lower()
        return [
            b for b in self.books
            if query_lower in b.title.lower() or query_lower in b.author.lower()
        ]

    def list_by_year(self, start: int, end: int) -> List[Book]:
        """Return books with a publication year within the given inclusive range."""
        return [b for b in self.books if start <= b.year <= end]
