def test_create_mission(client, mission_data):
    response = client.post("/missions/", json=mission_data)
    assert response.status_code == 201
    data = response.json()
    
    assert data["complete"] == mission_data["complete"]
    
    assert len(data["targets"]) == len(mission_data["targets"])
    for target_data, target_response in zip(mission_data["targets"], data["targets"]):
        assert target_response["name"] == target_data["name"]
        assert target_response["country"] == target_data["country"]
        assert target_response["notes"] == target_data["notes"]
        assert target_response["complete"] == target_data["complete"]

def test_get_mission(client, mission_data, created_mission):
    mission_id = created_mission["id"]
    response = client.get(f"/missions/{mission_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == mission_id
    assert data["complete"] == mission_data["complete"]

def test_update_mission(client, mission_data, created_mission):
    mission_id = created_mission["id"]
    updated_data = {
        "complete": True,
        "targets": [
            {
                "name": "Enemy Base Alpha",
                "country": "Nowhere Land",
                "notes": "Mission accomplished",
                "complete": True
            }
        ]
    }
    response = client.patch(f"/missions/{mission_id}", json=updated_data)
    assert response.status_code == 200
    data = response.json()
    assert data["complete"] is True

def test_list_missions(client, mission_data, created_mission):
    response = client.get("/missions/")
    assert response.status_code == 200
    missions = response.json()
    assert any(mission["complete"] == mission_data["complete"] for mission in missions)

def test_delete_mission(client, mission_data, created_mission):
    mission_id = created_mission["id"]
    response = client.delete(f"/missions/{mission_id}")
    assert response.status_code == 204
    response = client.get(f"/missions/{mission_id}")
    assert response.status_code == 404
