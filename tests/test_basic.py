import pytest
from app import create_app


def test_create_app_and_blueprints():
    app = create_app()
    assert app is not None
    # Blueprints registered in app/__init__.py
    assert 'user_bp' in app.blueprints
    assert 'book_bp' in app.blueprints
    assert 'transaction_bp' in app.blueprints


def test_test_client_context():
    app = create_app()
    # Ensure we can create a test client without touching the DB
    with app.test_client() as client:
        resp = client.get('/')
        # Root isn't defined in this app; make sure we get a valid HTTP response (404 or similar)
        assert resp.status_code in (200, 404)
