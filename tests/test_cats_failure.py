def test_create_spy_cat_bad_request(client):
    response = client.post(
        "/cats/",
        json={
            "breed": "Bengal",
            "years_of_experience": 3,
            "salary": 5000
        }
    )
    assert response.status_code == 422

    response = client.post(
        "/cats/",
        json={
            "name": "Whiskers",
            "breed": "Bengal",
            "years_of_experience": 3,
            "salary": "five thousand"
        }
    )
    assert response.status_code == 422

def test_get_nonexistent_spy_cat(client):
    response = client.get("/cats/999")
    assert response.status_code == 404

def test_update_nonexistent_spy_cat(client):
    response = client.patch(
        "/cats/999",
        json={"salary": 6000}
    )
    assert response.status_code == 404

def test_update_spy_cat_invalid_data(client):
    response = client.patch(
        "/cats/1",
        json={"salary": "six thousand"}
    )
    assert response.status_code == 422

def test_delete_nonexistent_spy_cat(client):
    response = client.delete("/cats/999")
    assert response.status_code == 404
