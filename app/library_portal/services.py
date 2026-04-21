import re
import sqlite3
from contextlib import closing
from datetime import datetime, timezone

TITLE_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9\s.,:'&()/-]{1,79}$")
AUTHOR_PATTERN = re.compile(r"^[A-Za-z][A-Za-z\s.'-]{1,59}$")
ISBN_PATTERN = re.compile(r"^[0-9-]{10,17}$")
CATEGORY_PATTERN = re.compile(r"^[A-Za-z][A-Za-z\s&/-]{1,39}$")
MEMBER_PATTERN = re.compile(r"^[A-Za-z][A-Za-z\s.'-]{1,59}$")

SEED_BOOKS = [
    ("Clean Code", "Robert Martin", "978-0132350884", "Software Engineering", 4),
    ("The Pragmatic Programmer", "Andrew Hunt", "978-0201616224", "Software Engineering", 3),
    ("Designing Data-Intensive Applications", "Martin Kleppmann", "978-1449373320", "Distributed Systems", 2),
    ("Introduction to Algorithms", "Thomas Cormen", "978-0262046305", "Algorithms", 5),
    ("Computer Networks", "Andrew Tanenbaum", "978-0132126953", "Networking", 2),
    ("Operating System Concepts", "Abraham Silberschatz", "978-1119800361", "Operating Systems", 3),
]


class ValidationError(ValueError):
    pass


class NotFoundError(LookupError):
    pass


class ConflictError(RuntimeError):
    pass


class LibraryService:
    def __init__(self, database_path):
        self.database_path = database_path
        self._initialize_database()

    def get_summary(self):
        with self._connect() as connection:
            totals = connection.execute(
                """
                SELECT
                  COUNT(*) AS total_books,
                  COALESCE(SUM(available_copies), 0) AS available_copies,
                  COALESCE(SUM(total_copies - available_copies), 0) AS borrowed_copies
                FROM books
                """
            ).fetchone()
            active_members = connection.execute(
                """
                SELECT COUNT(DISTINCT member_name) AS active_members
                FROM loans
                WHERE returned_at IS NULL
                """
            ).fetchone()

        return {
            "total_books": totals["total_books"],
            "available_copies": totals["available_copies"],
            "borrowed_copies": totals["borrowed_copies"],
            "active_members": active_members["active_members"],
        }

    def list_books(self, query=""):
        query = self._validate_optional_search(query)
        sql = """
            SELECT id, title, author, isbn, category, total_copies, available_copies
            FROM books
        """
        params = []
        if query:
            sql += """
                WHERE lower(title) LIKE ? OR lower(author) LIKE ? OR lower(category) LIKE ? OR isbn LIKE ?
            """
            wildcard = f"%{query.lower()}%"
            params = [wildcard, wildcard, wildcard, f"%{query}%"]
        sql += " ORDER BY title ASC"

        with self._connect() as connection:
            rows = connection.execute(sql, params).fetchall()
        return [self._serialize_book(row) for row in rows]

    def list_loans(self):
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT loans.id, loans.member_name, loans.issued_at, books.title, books.author
                FROM loans
                JOIN books ON books.id = loans.book_id
                WHERE loans.returned_at IS NULL
                ORDER BY loans.issued_at DESC
                """
            ).fetchall()

        return [
            {
                "id": row["id"],
                "member_name": row["member_name"],
                "issued_at": row["issued_at"],
                "book_title": row["title"],
                "book_author": row["author"],
            }
            for row in rows
        ]

    def add_book(self, payload):
        title = self._validate_text(payload.get("title", ""), TITLE_PATTERN, "Title", 2, 80)
        author = self._validate_text(payload.get("author", ""), AUTHOR_PATTERN, "Author", 2, 60)
        isbn = self._validate_text(payload.get("isbn", ""), ISBN_PATTERN, "ISBN", 10, 17)
        category = self._validate_text(payload.get("category", ""), CATEGORY_PATTERN, "Category", 2, 40)
        total_copies = self._validate_copies(payload.get("copies", 1))

        with self._connect() as connection:
            try:
                cursor = connection.execute(
                    """
                    INSERT INTO books (title, author, isbn, category, total_copies, available_copies)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (title, author, isbn, category, total_copies, total_copies),
                )
                connection.commit()
            except sqlite3.IntegrityError as exc:
                raise ConflictError("A book with this ISBN already exists.") from exc

            row = connection.execute(
                """
                SELECT id, title, author, isbn, category, total_copies, available_copies
                FROM books
                WHERE id = ?
                """,
                (cursor.lastrowid,),
            ).fetchone()

        return self._serialize_book(row)

    def borrow_book(self, book_id, member_name):
        validated_member = self._validate_text(member_name, MEMBER_PATTERN, "Member name", 2, 60)

        with self._connect() as connection:
            book = connection.execute(
                """
                SELECT id, title, author, isbn, category, total_copies, available_copies
                FROM books
                WHERE id = ?
                """,
                (book_id,),
            ).fetchone()
            if not book:
                raise NotFoundError("Book not found.")
            if book["available_copies"] <= 0:
                raise ConflictError("No copies are currently available for this book.")

            timestamp = self._timestamp()
            connection.execute(
                """
                INSERT INTO loans (book_id, member_name, issued_at, returned_at)
                VALUES (?, ?, ?, NULL)
                """,
                (book_id, validated_member, timestamp),
            )
            connection.execute(
                """
                UPDATE books
                SET available_copies = available_copies - 1
                WHERE id = ?
                """,
                (book_id,),
            )
            connection.commit()

            updated_book = connection.execute(
                """
                SELECT id, title, author, isbn, category, total_copies, available_copies
                FROM books
                WHERE id = ?
                """,
                (book_id,),
            ).fetchone()

        return {
            "message": f"Issued '{updated_book['title']}' to {validated_member}.",
            "book": self._serialize_book(updated_book),
        }

    def return_book(self, book_id):
        with self._connect() as connection:
            book = connection.execute(
                """
                SELECT id, title, author, isbn, category, total_copies, available_copies
                FROM books
                WHERE id = ?
                """,
                (book_id,),
            ).fetchone()
            if not book:
                raise NotFoundError("Book not found.")

            loan = connection.execute(
                """
                SELECT id, member_name
                FROM loans
                WHERE book_id = ? AND returned_at IS NULL
                ORDER BY issued_at DESC
                LIMIT 1
                """,
                (book_id,),
            ).fetchone()
            if not loan:
                raise ConflictError("This book is not currently issued to any member.")

            connection.execute(
                "UPDATE loans SET returned_at = ? WHERE id = ?",
                (self._timestamp(), loan["id"]),
            )
            connection.execute(
                """
                UPDATE books
                SET available_copies = available_copies + 1
                WHERE id = ?
                """,
                (book_id,),
            )
            connection.commit()

            updated_book = connection.execute(
                """
                SELECT id, title, author, isbn, category, total_copies, available_copies
                FROM books
                WHERE id = ?
                """,
                (book_id,),
            ).fetchone()

        return {
            "message": f"Returned '{updated_book['title']}' from {loan['member_name']}.",
            "book": self._serialize_book(updated_book),
        }

    def _connect(self):
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize_database(self):
        with closing(self._connect()) as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author TEXT NOT NULL,
                    isbn TEXT NOT NULL UNIQUE,
                    category TEXT NOT NULL,
                    total_copies INTEGER NOT NULL,
                    available_copies INTEGER NOT NULL
                );

                CREATE TABLE IF NOT EXISTS loans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    book_id INTEGER NOT NULL,
                    member_name TEXT NOT NULL,
                    issued_at TEXT NOT NULL,
                    returned_at TEXT NULL,
                    FOREIGN KEY (book_id) REFERENCES books (id)
                );
                """
            )

            existing_count = connection.execute("SELECT COUNT(*) AS count FROM books").fetchone()["count"]
            if existing_count == 0:
                connection.executemany(
                    """
                    INSERT INTO books (title, author, isbn, category, total_copies, available_copies)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    [(title, author, isbn, category, copies, copies) for title, author, isbn, category, copies in SEED_BOOKS],
                )
            connection.commit()

    def _serialize_book(self, row):
        return {
            "id": row["id"],
            "title": row["title"],
            "author": row["author"],
            "isbn": row["isbn"],
            "category": row["category"],
            "total_copies": row["total_copies"],
            "available_copies": row["available_copies"],
            "status": "Available" if row["available_copies"] > 0 else "Issued Out",
        }

    def _validate_optional_search(self, query):
        query = str(query or "").strip()
        if len(query) > 60:
            raise ValidationError("Search query must be 60 characters or fewer.")
        return query

    def _validate_copies(self, raw_value):
        try:
            copies = int(raw_value)
        except (TypeError, ValueError) as exc:
            raise ValidationError("Copies must be a valid whole number.") from exc
        if copies < 1 or copies > 25:
            raise ValidationError("Copies must be between 1 and 25.")
        return copies

    def _validate_text(self, value, pattern, field_name, min_length, max_length):
        text = str(value or "").strip()
        if not text:
            raise ValidationError(f"{field_name} is required.")
        if len(text) < min_length or len(text) > max_length:
            raise ValidationError(f"{field_name} must be between {min_length} and {max_length} characters long.")
        if not pattern.fullmatch(text):
            raise ValidationError(f"{field_name} contains unsupported characters.")
        return text

    def _timestamp(self):
        return datetime.now(timezone.utc).isoformat()
