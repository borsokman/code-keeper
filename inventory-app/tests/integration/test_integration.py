def test_add_and_retrieve_movie(client, session):
    """Integration test: Write to Postgres and read it back."""
    # 1. Write to the database
    payload = {"title": "The Matrix", "description": "A simulation movie"}
    post_response = client.post("/api/movies", json=payload)

    assert post_response.status_code == 201
    data = post_response.get_json()
    assert data["id"] is not None
    movie_id = data["id"]

    # 2. Read from the database to verify persistence
    get_response = client.get(f"/api/movies/{movie_id}")
    assert get_response.status_code == 200

    retrieved_data = get_response.get_json()
    assert retrieved_data["title"] == "The Matrix"
    assert retrieved_data["description"] == "A simulation movie"


def test_delete_movie(client, session):
    """Integration test: Delete a record from Postgres."""
    # 1. Create a movie
    payload = {"title": "Inception", "description": "Dream within a dream"}
    post_response = client.post("/api/movies", json=payload)
    movie_id = post_response.get_json()["id"]

    # 2. Delete the movie
    delete_response = client.delete(f"/api/movies/{movie_id}")
    assert delete_response.status_code == 200

    # 3. Verify it is removed from the database
    get_response = client.get(f"/api/movies/{movie_id}")
    assert get_response.status_code == 404
