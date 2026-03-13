import sys
from books import BookCollection
from exceptions import BookAppError, BookNotFoundError, StorageError, ValidationError
from utils import show_books


collection: BookCollection


def handle_list() -> None:
    books = collection.list_books()
    show_books(books)


def handle_add() -> None:
    print("\nAdd a New Book\n")

    title = input("Title: ").strip()
    author = input("Author: ").strip()
    year_str = input("Year: ").strip()

    try:
        year = int(year_str) if year_str else 0
    except ValueError:
        print(f"\nError: '{year_str}' is not a valid year.\n")
        return

    try:
        collection.add_book(title, author, year)
        print("\nBook added successfully.\n")
    except ValidationError as e:
        print(f"\nError: {e}\n")


def handle_remove() -> None:
    print("\nRemove a Book\n")

    title = input("Enter the title of the book to remove: ").strip()

    try:
        collection.remove_book(title)
        print(f"\n'{title}' removed successfully.\n")
    except BookNotFoundError as e:
        print(f"\nError: {e}\n")


def handle_find() -> None:
    print("\nFind Books by Author\n")

    author = input("Author name: ").strip()
    books = collection.find_by_author(author)

    show_books(books)


def handle_search() -> None:
    print("\nSearch Books\n")

    query = input("Search query: ").strip()
    books = collection.search_books(query)

    show_books(books)


def handle_year() -> None:
    print("\nFilter Books by Year Range\n")

    while True:
        start_str = input("Start year: ").strip()
        try:
            start = int(start_str)
            break
        except ValueError:
            print("Please enter a valid year.")

    while True:
        end_str = input("End year: ").strip()
        try:
            end = int(end_str)
            break
        except ValueError:
            print("Please enter a valid year.")

    books = collection.list_by_year(start, end)
    show_books(books)


def show_help() -> None:
    print("""
Book Collection Helper

Commands:
  list     - Show all books
  add      - Add a new book
  remove   - Remove a book by title
  find     - Find books by author
  search   - Search books by title or author
  year     - Filter books by publication year range
  help     - Show this help message
""")


COMMANDS = {
    "list": handle_list,
    "add": handle_add,
    "remove": handle_remove,
    "find": handle_find,
    "search": handle_search,
    "year": handle_year,
    "help": show_help,
}


def main() -> None:
    global collection

    try:
        with BookCollection() as col:
            collection = col

            if len(sys.argv) < 2:
                show_help()
                return

            command = sys.argv[1].lower()
            handler = COMMANDS.get(command)

            if handler:
                try:
                    handler()
                except BookAppError as e:
                    print(f"\nError: {e}\n")
            else:
                print("Unknown command.\n")
                show_help()
    except StorageError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)
    except EOFError:
        print("\nInput closed. Exiting.")
        sys.exit(0)
