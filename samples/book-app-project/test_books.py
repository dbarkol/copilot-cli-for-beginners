"""Tests for books.py — covers current behavior of Book and BookCollection."""

import json
import os
import pytest

# Ensure imports resolve from the book-app-project directory
import sys

sys.path.insert(0, os.path.dirname(__file__))

from books import Book, BookCollection, DATA_FILE
from exceptions import BookNotFoundError, StorageError, ValidationError


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def clean_data_file(tmp_path, monkeypatch):
    """Run every test in a temp directory so data.json is isolated."""
    monkeypatch.chdir(tmp_path)


@pytest.fixture
def empty_collection():
    """A BookCollection with no books (no data.json on disk)."""
    return BookCollection()


@pytest.fixture
def sample_books():
    """Three books written to data.json before collection loads."""
    books = [
        {"title": "The Hobbit", "author": "J.R.R. Tolkien", "year": 1937, "read": False},
        {"title": "1984", "author": "George Orwell", "year": 1949, "read": True},
        {"title": "Dune", "author": "Frank Herbert", "year": 1965, "read": False},
    ]
    with open(DATA_FILE, "w") as f:
        json.dump(books, f)
    return BookCollection()


# ---------------------------------------------------------------------------
# Book dataclass
# ---------------------------------------------------------------------------

class TestBook:
    """Tests for the Book dataclass."""

    def test_defaults(self):
        book = Book(title="Test", author="Author", year=2000)
        assert book.read is False

    def test_all_fields(self):
        book = Book(title="T", author="A", year=1, read=True)
        assert book.title == "T"
        assert book.author == "A"
        assert book.year == 1
        assert book.read is True


# ---------------------------------------------------------------------------
# load_books
# ---------------------------------------------------------------------------

class TestLoadBooks:
    """Tests for BookCollection.load_books."""

    def test_no_file_starts_empty(self, empty_collection):
        assert empty_collection.list_books() == []

    def test_loads_existing_data(self, sample_books):
        assert len(sample_books.list_books()) == 3

    def test_preserves_read_flag(self, sample_books):
        titles = {b.title: b for b in sample_books.list_books()}
        assert titles["1984"].read is True
        assert titles["The Hobbit"].read is False

    def test_corrupt_json_raises_storage_error(self):
        with open(DATA_FILE, "w") as f:
            f.write("{invalid json")
        with pytest.raises(StorageError, match="corrupted"):
            BookCollection()


# ---------------------------------------------------------------------------
# save_books
# ---------------------------------------------------------------------------

class TestSaveBooks:
    """Tests for BookCollection.save_books."""

    def test_creates_data_file(self):
        with BookCollection() as col:
            col.add_book("Test", "Author", 2000)
        assert os.path.exists(DATA_FILE)

    def test_round_trip(self):
        with BookCollection() as col:
            col.add_book("Test", "Author", 2000)
        reloaded = BookCollection()
        assert len(reloaded.list_books()) == 1
        assert reloaded.list_books()[0].title == "Test"

    def test_save_to_readonly_raises_storage_error(self):
        col = BookCollection()
        col.add_book("X", "Y", 1)
        col.save_books()
        os.chmod(DATA_FILE, 0o000)
        try:
            with pytest.raises(StorageError, match="Could not save"):
                col.save_books()
        finally:
            os.chmod(DATA_FILE, 0o644)


# ---------------------------------------------------------------------------
# add_book
# ---------------------------------------------------------------------------

class TestAddBook:
    """Tests for BookCollection.add_book."""

    def test_adds_and_returns_book(self, empty_collection):
        book = empty_collection.add_book("Dune", "Frank Herbert", 1965)
        assert isinstance(book, Book)
        assert book.title == "Dune"

    def test_increments_collection(self, empty_collection):
        empty_collection.add_book("A", "B", 1)
        empty_collection.add_book("C", "D", 2)
        assert len(empty_collection.list_books()) == 2

    def test_strips_whitespace(self, empty_collection):
        book = empty_collection.add_book("  Dune  ", "  Herbert  ", 1965)
        assert book.title == "Dune"
        assert book.author == "Herbert"

    def test_empty_title_raises_validation_error(self, empty_collection):
        with pytest.raises(ValidationError, match="Title"):
            empty_collection.add_book("", "Author", 2000)

    def test_whitespace_title_raises_validation_error(self, empty_collection):
        with pytest.raises(ValidationError, match="Title"):
            empty_collection.add_book("   ", "Author", 2000)

    def test_empty_author_raises_validation_error(self, empty_collection):
        with pytest.raises(ValidationError, match="Author"):
            empty_collection.add_book("Title", "", 2000)

    def test_whitespace_author_raises_validation_error(self, empty_collection):
        with pytest.raises(ValidationError, match="Author"):
            empty_collection.add_book("Title", "   ", 2000)


# ---------------------------------------------------------------------------
# list_books
# ---------------------------------------------------------------------------

class TestListBooks:
    """Tests for BookCollection.list_books."""

    def test_empty(self, empty_collection):
        assert empty_collection.list_books() == []

    def test_returns_all(self, sample_books):
        assert len(sample_books.list_books()) == 3


# ---------------------------------------------------------------------------
# find_book_by_title
# ---------------------------------------------------------------------------

class TestFindBookByTitle:
    """Tests for BookCollection.find_book_by_title."""

    def test_exact_match(self, sample_books):
        book = sample_books.find_book_by_title("Dune")
        assert book is not None
        assert book.author == "Frank Herbert"

    def test_case_insensitive(self, sample_books):
        assert sample_books.find_book_by_title("dune") is not None
        assert sample_books.find_book_by_title("DUNE") is not None

    def test_not_found_returns_none(self, sample_books):
        assert sample_books.find_book_by_title("Nonexistent") is None

    def test_empty_string(self, sample_books):
        assert sample_books.find_book_by_title("") is None


# ---------------------------------------------------------------------------
# mark_as_read
# ---------------------------------------------------------------------------

class TestMarkAsRead:
    """Tests for BookCollection.mark_as_read."""

    def test_marks_unread_book(self, sample_books):
        sample_books.mark_as_read("The Hobbit")
        book = sample_books.find_book_by_title("The Hobbit")
        assert book.read is True

    def test_already_read_stays_read(self, sample_books):
        sample_books.mark_as_read("1984")
        book = sample_books.find_book_by_title("1984")
        assert book.read is True

    def test_not_found_raises(self, sample_books):
        with pytest.raises(BookNotFoundError, match="No book found"):
            sample_books.mark_as_read("Nonexistent")

    def test_case_insensitive(self, sample_books):
        sample_books.mark_as_read("the hobbit")
        book = sample_books.find_book_by_title("The Hobbit")
        assert book.read is True

    def test_persists_to_disk(self, sample_books):
        with sample_books:
            sample_books.mark_as_read("Dune")
        reloaded = BookCollection()
        assert reloaded.find_book_by_title("Dune").read is True


# ---------------------------------------------------------------------------
# remove_book
# ---------------------------------------------------------------------------

class TestRemoveBook:
    """Tests for BookCollection.remove_book."""

    def test_removes_existing(self, sample_books):
        sample_books.remove_book("Dune")
        assert sample_books.find_book_by_title("Dune") is None
        assert len(sample_books.list_books()) == 2

    def test_not_found_raises(self, sample_books):
        with pytest.raises(BookNotFoundError, match="No book found"):
            sample_books.remove_book("Nonexistent")

    def test_case_insensitive(self, sample_books):
        sample_books.remove_book("dune")
        assert sample_books.find_book_by_title("Dune") is None

    def test_persists_to_disk(self, sample_books):
        with sample_books:
            sample_books.remove_book("Dune")
        reloaded = BookCollection()
        assert len(reloaded.list_books()) == 2


# ---------------------------------------------------------------------------
# find_by_author
# ---------------------------------------------------------------------------

class TestFindByAuthor:
    """Tests for BookCollection.find_by_author."""

    def test_finds_matching(self, sample_books):
        results = sample_books.find_by_author("George Orwell")
        assert len(results) == 1
        assert results[0].title == "1984"

    def test_case_insensitive(self, sample_books):
        assert len(sample_books.find_by_author("george orwell")) == 1

    def test_no_match_returns_empty(self, sample_books):
        assert sample_books.find_by_author("Unknown") == []

    def test_multiple_books_by_same_author(self, sample_books):
        sample_books.add_book("Animal Farm", "George Orwell", 1945)
        assert len(sample_books.find_by_author("George Orwell")) == 2


# ---------------------------------------------------------------------------
# search_books
# ---------------------------------------------------------------------------

class TestSearchBooks:
    """Tests for BookCollection.search_books."""

    def test_partial_title_match(self, sample_books):
        results = sample_books.search_books("hob")
        assert len(results) == 1
        assert results[0].title == "The Hobbit"

    def test_partial_author_match(self, sample_books):
        results = sample_books.search_books("tolkien")
        assert len(results) == 1

    def test_case_insensitive(self, sample_books):
        assert len(sample_books.search_books("DUNE")) == 1

    def test_no_match(self, sample_books):
        assert sample_books.search_books("xyz") == []

    def test_empty_query_matches_all(self, sample_books):
        """Current behavior: empty string is a substring of everything."""
        assert len(sample_books.search_books("")) == 3


# ---------------------------------------------------------------------------
# list_by_year
# ---------------------------------------------------------------------------

class TestListByYear:
    """Tests for BookCollection.list_by_year."""

    def test_inclusive_range(self, sample_books):
        results = sample_books.list_by_year(1937, 1949)
        assert len(results) == 2

    def test_single_year(self, sample_books):
        results = sample_books.list_by_year(1965, 1965)
        assert len(results) == 1
        assert results[0].title == "Dune"

    def test_no_match(self, sample_books):
        assert sample_books.list_by_year(2000, 2025) == []

    def test_inverted_range_returns_empty(self, sample_books):
        """Current behavior: start > end silently returns empty list."""
        assert sample_books.list_by_year(2000, 1900) == []

    @pytest.mark.parametrize("start,end,expected_count", [
        (0, 9999, 3),
        (1949, 1949, 1),
        (1938, 1964, 1),
    ])
    def test_various_ranges(self, sample_books, start, end, expected_count):
        assert len(sample_books.list_by_year(start, end)) == expected_count


# ---------------------------------------------------------------------------
# Context manager
# ---------------------------------------------------------------------------

class TestContextManager:
    """Tests for BookCollection used as a context manager."""

    def test_enter_returns_self(self):
        col = BookCollection()
        assert col.__enter__() is col

    def test_saves_on_clean_exit(self):
        with BookCollection() as col:
            col.add_book("Test", "Author", 2000)
        assert os.path.exists(DATA_FILE)
        reloaded = BookCollection()
        assert len(reloaded.list_books()) == 1

    def test_skips_save_on_exception(self):
        with pytest.raises(RuntimeError):
            with BookCollection() as col:
                col.add_book("Test", "Author", 2000)
                raise RuntimeError("boom")
        assert not os.path.exists(DATA_FILE)

    def test_explicit_save_still_works(self):
        col = BookCollection()
        col.add_book("Test", "Author", 2000)
        col.save_books()
        reloaded = BookCollection()
        assert len(reloaded.list_books()) == 1
