import pytest
from unittest.mock import patch, MagicMock

# Force dummy database environment strings so initialization doesn't break
import os
os.environ["DB_USER"] = "test"
os.environ["DB_PASSWORD"] = "test"
os.environ["DB_HOST"] = "test"
os.environ["DB_PORT"] = "5432"
os.environ["DB_NAME"] = "test"

@pytest.fixture
def app():
    """Builds the Flask application instance while mocking out database creation."""
    with patch("flask_sqlalchemy.SQLAlchemy.create_all"):
        from app import create_app
        _app = create_app()
        _app.config["TESTING"] = True
        yield _app

@pytest.fixture
def client(app):
    """Provides the test client."""
    return app.test_client()

# === GET /api/movies ===

def test_get_movies_no_filter(app, client):
    """Verifies that pulling all items returns the correct schema format."""
    # Fix: Wrap patch inside an active app context to prevent descriptor lookup failure
    with app.app_context():
        with patch("app.routes.Movie.query") as mock_query:
            mock_m1 = MagicMock(id=1, title="Inception", description="Dream world")
            mock_m2 = MagicMock(id=2, title="Interstellar", description="Space travel")
            mock_query.all.return_value = [mock_m1, mock_m2]

            response = client.get("/api/movies")
            assert response.status_code == 200
            data = response.get_json()
            assert len(data) == 2
            assert data[0]["title"] == "Inception"

def test_get_movies_with_filter(app, client):
    """Verifies that passing query strings filters results correctly."""
    with app.app_context():
        with patch("app.routes.Movie.query") as mock_query:
            mock_m1 = MagicMock(id=1, title="Inception", description="Dream world")
            mock_filter_chain = MagicMock()
            mock_filter_chain.all.return_value = [mock_m1]
            mock_query.filter.return_value = mock_filter_chain

            response = client.get("/api/movies?title=Inception")
            assert response.status_code == 200
            mock_query.filter.assert_called_once()
            assert response.get_json()[0]["title"] == "Inception"

# === POST /api/movies ===

@patch("app.routes.db.session")
def test_add_movie_success(mock_session, client):
    """Verifies valid movie entities pass logic checks and are committed."""
    payload = {"title": "The Matrix", "description": "Simulation"}
    response = client.post("/api/movies", json=payload)
    
    assert response.status_code == 201
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()

def test_add_movie_validation_failure(client):
    """Verifies that missing structural fields are blocked by the validation layer."""
    payload = {"title": "   "}  # Blank title check
    response = client.post("/api/movies", json=payload)
    
    assert response.status_code == 400
    assert "title is required" in response.get_json()["error"]

# === GET /api/movies/<id> ===

@patch("app.routes.db.session")
def test_get_movie_by_id_found(mock_session, client):
    """Verifies tracking logic returns target data if match exists."""
    mock_movie = MagicMock(id=42, title="Tenet", description="Time inversion")
    mock_session.get.return_value = mock_movie

    response = client.get("/api/movies/42")
    assert response.status_code == 200
    assert response.get_json()["id"] == 42

@patch("app.routes.db.session")
def test_get_movie_by_id_not_found(mock_session, client):
    """Verifies that missing entries properly throw a 404 status resource error."""
    mock_session.get.return_value = None

    response = client.get("/api/movies/999")
    assert response.status_code == 404
    assert "movie not found" in response.get_json()["error"]

# === PUT /api/movies/<id> ===

@patch("app.routes.db.session")
def test_update_movie_success(mock_session, client):
    """Verifies properties shift and apply correctly during PUT payloads."""
    mock_movie = MagicMock(id=1, title="Old Title", description="Old Desc")
    mock_session.get.return_value = mock_movie

    response = client.put("/api/movies/1", json={"title": "New Title"})
    assert response.status_code == 200
    assert mock_movie.title == "New Title"
    mock_session.commit.assert_called_once()

# === DELETE /api/movies/<id> ===

@patch("app.routes.db.session")
def test_delete_movie_success(mock_session, client):
    """Verifies delete calls invoke standard removal behaviors safely."""
    mock_movie = MagicMock(id=5)
    mock_session.get.return_value = mock_movie

    response = client.delete("/api/movies/5")
    assert response.status_code == 200
    mock_session.delete.assert_called_with(mock_movie)
    mock_session.commit.assert_called_once()