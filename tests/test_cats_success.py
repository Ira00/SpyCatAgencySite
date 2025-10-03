def test_create_spy_cat(client):
    response = client.post(
        "/cats/",
        json={
            "name": "Whiskers2.0",
            "breed": "Bengal",
            "years_of_experience": 3,
            "salary": 5000
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Whiskers2.0"
    assert data["breed"] == "Bengal"
    assert data["years_of_experience"] == 3
    assert data["salary"] == 5000

def test_list_spy_cats(client):
    response = client.get("/cats/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_spy_cat(client, created_spy_cat):
    cat_id = created_spy_cat["id"]
    response = client.get(f"/cats/{cat_id}")
    assert response.status_code == 200
    assert response.json()["id"] == cat_id

def test_update_spy_cat(client, created_spy_cat):
    cat_id = created_spy_cat["id"]
    response = client.patch(
        f"/cats/{cat_id}",
        json={"salary": 6000}
    )
    assert response.status_code == 200
    assert response.json()["salary"] == 6000

def test_delete_spy_cat(client, created_spy_cat):
    cat_id = created_spy_cat["id"]
    response = client.delete(f"/cats/{cat_id}")
    assert response.status_code == 204