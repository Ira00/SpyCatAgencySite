def test_create_mission_invalid(client, invalid_mission_data):
    response = client.post("/missions/", json=invalid_mission_data)
    assert response.status_code == 422

def test_get_nonexistent_mission(client):
    response = client.get("/missions/9999")
    assert response.status_code == 404

def test_update_nonexistent_mission(client):
    response = client.patch("/missions/9999", json={"complete": True})
    assert response.status_code == 404

def test_delete_nonexistent_mission(client):
    response = client.delete("/missions/9999")
    assert response.status_code == 404

def test_cat_conflict(client, mission_data):
    cat_response = client.post("/cats/", json={
        "name": "Whiskers",
        "breed": "Bengal",
        "years_of_experience": 3,
        "salary": 5000
    })
    cat_id = cat_response.json()["id"]

    response1 = client.post("/missions/", json=mission_data)
    mission1_id = response1.json()["id"]

    client.patch(f"/missions/{mission1_id}/assign", json={"cat_id": cat_id})

    another_mission = mission_data.copy()
    another_mission["name"] = "Operation Shadow Paw"
    response2 = client.post("/missions/", json=another_mission)
    mission2_id = response2.json()["id"]

    response = client.patch(f"/missions/{mission2_id}/assign", json={"cat_id": cat_id})
    
    assert response.status_code == 400

