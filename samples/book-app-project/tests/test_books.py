import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import books
from books import BookCollection
from exceptions import BookNotFoundError, ValidationError


@pytest.fixture(autouse=True)
def use_temp_data_file(tmp_path, monkeypatch):
    """Use a temporary data file for each test."""
    temp_file = tmp_path / "data.json"
    temp_file.write_text("[]")
    monkeypatch.setattr(books, "DATA_FILE", str(temp_file))


def test_add_book():
    collection = BookCollection()
    initial_count = len(collection.books)
    collection.add_book("1984", "George Orwell", 1949)
    assert len(collection.books) == initial_count + 1
    book = collection.find_book_by_title("1984")
    assert book is not None
    assert book.author == "George Orwell"
    assert book.year == 1949
    assert book.read is False

def test_mark_book_as_read():
    collection = BookCollection()
    collection.add_book("Dune", "Frank Herbert", 1965)
    collection.mark_as_read("Dune")
    book = collection.find_book_by_title("Dune")
    assert book.read is True

def test_mark_book_as_read_invalid():
    collection = BookCollection()
    with pytest.raises(BookNotFoundError):
        collection.mark_as_read("Nonexistent Book")

def test_remove_book():
    collection = BookCollection()
    collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)
    collection.remove_book("The Hobbit")
    book = collection.find_book_by_title("The Hobbit")
    assert book is None

def test_remove_book_invalid():
    collection = BookCollection()
    with pytest.raises(BookNotFoundError):
        collection.remove_book("Nonexistent Book")


def test_search_by_partial_title():
    collection = BookCollection()
    collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)
    collection.add_book("1984", "George Orwell", 1949)
    results = collection.search_books("Hob")
    assert len(results) == 1
    assert results[0].title == "The Hobbit"


def test_search_by_partial_author():
    collection = BookCollection()
    collection.add_book("1984", "George Orwell", 1949)
    collection.add_book("Dune", "Frank Herbert", 1965)
    results = collection.search_books("Orwell")
    assert len(results) == 1
    assert results[0].title == "1984"


def test_search_case_insensitive():
    collection = BookCollection()
    collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)
    results = collection.search_books("the hobbit")
    assert len(results) == 1
    assert results[0].title == "The Hobbit"


def test_search_matches_title_and_author():
    collection = BookCollection()
    collection.add_book("Dune", "Frank Herbert", 1965)
    collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)
    collection.add_book("Frank's Adventure", "Jane Doe", 2020)
    results = collection.search_books("Frank")
    assert len(results) == 2
    titles = {b.title for b in results}
    assert titles == {"Dune", "Frank's Adventure"}


def test_search_no_results():
    collection = BookCollection()
    collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)
    results = collection.search_books("Python")
    assert len(results) == 0


def test_list_by_year_in_range():
    collection = BookCollection()
    collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)
    collection.add_book("1984", "George Orwell", 1949)
    collection.add_book("Dune", "Frank Herbert", 1965)
    results = collection.list_by_year(1940, 1970)
    assert len(results) == 2
    assert [b.title for b in results] == ["1984", "Dune"]


def test_list_by_year_excludes_out_of_range():
    collection = BookCollection()
    collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)
    collection.add_book("1984", "George Orwell", 1949)
    results = collection.list_by_year(1950, 2000)
    assert len(results) == 0


def test_list_by_year_boundary_values():
    collection = BookCollection()
    collection.add_book("1984", "George Orwell", 1949)
    collection.add_book("Dune", "Frank Herbert", 1965)
    results = collection.list_by_year(1949, 1965)
    assert len(results) == 2
    assert [b.year for b in results] == [1949, 1965]


def test_list_by_year_inverted_range():
    collection = BookCollection()
    collection.add_book("1984", "George Orwell", 1949)
    results = collection.list_by_year(2000, 1900)
    assert len(results) == 0


def test_list_by_year_empty_collection():
    collection = BookCollection()
    results = collection.list_by_year(1900, 2000)
    assert len(results) == 0


# ---------------------------------------------------------------------------
# Year-range sorting
# ---------------------------------------------------------------------------

def test_list_by_year_results_sorted_ascending():
    collection = BookCollection()
    collection.add_book("Dune", "Frank Herbert", 1965)
    collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)
    collection.add_book("1984", "George Orwell", 1949)
    results = collection.list_by_year(1900, 2000)
    assert [b.year for b in results] == [1937, 1949, 1965]


def test_list_by_year_same_year_preserves_insertion_order():
    collection = BookCollection()
    collection.add_book("Fahrenheit 451", "Ray Bradbury", 1953)
    collection.add_book("Casino Royale", "Ian Fleming", 1953)
    results = collection.list_by_year(1950, 1960)
    assert [b.title for b in results] == ["Fahrenheit 451", "Casino Royale"]


def test_list_by_year_single_result_trivially_sorted():
    collection = BookCollection()
    collection.add_book("1984", "George Orwell", 1949)
    results = collection.list_by_year(1940, 1950)
    assert len(results) == 1
    assert results[0].year == 1949


def test_list_by_year_all_same_year_preserves_order():
    collection = BookCollection()
    collection.add_book("Book A", "Author A", 2000)
    collection.add_book("Book B", "Author B", 2000)
    collection.add_book("Book C", "Author C", 2000)
    results = collection.list_by_year(1999, 2001)
    assert [b.title for b in results] == ["Book A", "Book B", "Book C"]


# ---------------------------------------------------------------------------
# Year validation
# ---------------------------------------------------------------------------

def test_add_book_negative_year():
    collection = BookCollection()
    with pytest.raises(ValidationError, match="Year must be between"):
        collection.add_book("Title", "Author", -1)


def test_add_book_zero_year():
    collection = BookCollection()
    with pytest.raises(ValidationError, match="Year must be between"):
        collection.add_book("Title", "Author", 0)


def test_add_book_year_below_minimum():
    collection = BookCollection()
    with pytest.raises(ValidationError, match="Year must be between"):
        collection.add_book("Title", "Author", 999)


def test_add_book_future_year():
    import datetime
    collection = BookCollection()
    future = datetime.date.today().year + 1
    with pytest.raises(ValidationError, match="Year must be between"):
        collection.add_book("Title", "Author", future)


def test_add_book_minimum_year_accepted():
    collection = BookCollection()
    book = collection.add_book("Old Book", "Ancient Author", 1000)
    assert book.year == 1000


def test_add_book_current_year_accepted():
    import datetime
    collection = BookCollection()
    current = datetime.date.today().year
    book = collection.add_book("New Book", "Author", current)
    assert book.year == current
