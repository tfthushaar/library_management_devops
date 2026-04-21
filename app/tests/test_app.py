from pathlib import Path

from library_portal import create_app
from library_portal.services import LibraryService


def build_client(tmp_path):
    database_path = Path(tmp_path) / "test-library.db"
    service = LibraryService(str(database_path))
    return create_app(service).test_client()


def test_health_endpoint_returns_healthy_status(tmp_path):
    client = build_client(tmp_path)

    response = client.get("/health")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["status"] == "healthy"
    assert payload["application"] == "library-management-portal"
    assert payload["summary"]["total_books"] >= 1


def test_books_endpoint_lists_seeded_catalog(tmp_path):
    client = build_client(tmp_path)

    response = client.get("/api/books")
    payload = response.get_json()

    assert response.status_code == 200
    assert len(payload["books"]) >= 3
    assert payload["books"][0]["title"]


def test_add_book_and_borrow_return_flow(tmp_path):
    client = build_client(tmp_path)

    create_response = client.post(
        "/api/books",
        json={
            "title": "Site Reliability Engineering",
            "author": "Betsy Beyer",
            "isbn": "978-1491929124",
            "category": "SRE",
            "copies": 2,
        },
    )
    created_book = create_response.get_json()

    borrow_response = client.post(f"/api/books/{created_book['id']}/borrow", json={"member_name": "Asha Nair"})
    return_response = client.post(f"/api/books/{created_book['id']}/return", json={})

    assert create_response.status_code == 201
    assert borrow_response.status_code == 200
    assert return_response.status_code == 200
    assert "Returned" in return_response.get_json()["message"]


def test_book_creation_rejects_invalid_payload(tmp_path):
    client = build_client(tmp_path)

    response = client.post(
        "/api/books",
        json={
            "title": "<script>",
            "author": "1234",
            "isbn": "bad",
            "category": "!",
            "copies": 0,
        },
    )

    assert response.status_code == 400
    assert "unsupported" in response.get_json()["error"] or "between" in response.get_json()["error"]


def test_security_headers_are_present(tmp_path):
    client = build_client(tmp_path)

    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Cache-Control"] == "no-store"
    assert "Content-Security-Policy" in response.headers
