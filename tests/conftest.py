import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.database import Base, get_db
from main import app


SQLALCHEMY_DATABASE_URL = "sqlite:///db.sqlite3"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    yield TestClient(app)

@pytest.fixture
def created_spy_cat(client):
    cat_data = {
        "name": "Kitty",
        "breed": "Bombay",
        "years_of_experience": 3,
        "salary": 5000
    }
    response = client.post("/cats/", json=cat_data)
    assert response.status_code == 201
    return response.json()

@pytest.fixture
def created_mission(client, mission_data):
    response = client.post("/missions/", json=mission_data)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def mission_data():
    return {
        "complete": False,
        "targets": [
            {
                "name": "Enemy Base Alpha",
                "country": "Nowhere Land",
                "notes": "",
                "complete": False
            }
        ]
    }


@pytest.fixture
def invalid_mission_data():
    return {
        "description": "Incomplete mission data",
        "duration": -5,
        "cost": "expensive",
        "complete": False,
        "targets": []
    }
