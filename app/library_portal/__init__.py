import os

from flask import Flask, jsonify, render_template, request

from .services import ConflictError, LibraryService, NotFoundError, ValidationError


def create_app(library_service=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, "library.db"),
        APP_ENVIRONMENT=os.getenv("APP_ENVIRONMENT", "local"),
    )

    os.makedirs(app.instance_path, exist_ok=True)
    service = library_service or LibraryService(app.config["DATABASE"])

    @app.after_request
    def add_security_headers(response):
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "script-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:;"
        )
        if request.is_secure:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

    @app.errorhandler(ValidationError)
    def handle_validation_error(exc):
        return jsonify({"error": str(exc)}), 400

    @app.errorhandler(NotFoundError)
    def handle_not_found_error(exc):
        return jsonify({"error": str(exc)}), 404

    @app.errorhandler(ConflictError)
    def handle_conflict_error(exc):
        return jsonify({"error": str(exc)}), 409

    @app.route("/")
    def index():
        return render_template("index.html", app_environment=app.config["APP_ENVIRONMENT"])

    @app.route("/health")
    def health():
        return jsonify(
            {
                "status": "healthy",
                "application": "library-management-portal",
                "environment": app.config["APP_ENVIRONMENT"],
                "summary": service.get_summary(),
            }
        )

    @app.route("/api/summary")
    def summary():
        return jsonify(service.get_summary())

    @app.route("/api/books", methods=["GET", "POST"])
    def books():
        if request.method == "GET":
            return jsonify({"books": service.list_books(request.args.get("q", ""))})

        payload = request.get_json(silent=True) or request.form.to_dict()
        return jsonify(service.add_book(payload)), 201

    @app.route("/api/loans")
    def loans():
        return jsonify({"loans": service.list_loans()})

    @app.route("/api/books/<int:book_id>/borrow", methods=["POST"])
    def borrow_book(book_id):
        payload = request.get_json(silent=True) or request.form.to_dict()
        return jsonify(service.borrow_book(book_id, payload.get("member_name", "")))

    @app.route("/api/books/<int:book_id>/return", methods=["POST"])
    def return_book(book_id):
        return jsonify(service.return_book(book_id))

    return app
