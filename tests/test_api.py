import pytest
from fastapi.testclient import TestClient
from main import app, load_actions, get_action_by_name
from database.create_db import create_db, DB_NAME, AchievementT
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

client = TestClient(app)
engine = create_engine(f"sqlite:///{DB_NAME}")
Session = sessionmaker(bind=engine)

@pytest.fixture(autouse=True)
def setup_db():
    pass
    # from database.create_db import create_db
    # create_db()

def test_action_execution():
    action = load_actions()[0]
    response = client.post("/achievements/v1/user_action/", json={
        "user_id": 123,
        "action_name": action["name"]
    })
    if response.status_code != 200:
        print("\nRequest failed:")
        print("Status code:", response.status_code)
        print("Response JSON:", response.text)
    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_user_achievements_returns_expected_fields():
    client.post("/achievements/v1/user_action/", json={
        "user_id": 42,
        "action_name": load_actions()[0]["name"]
    })
    r = client.get("/achievements/v1/get_user_achievements/42")
    data = r.json()
    assert r.status_code == 200
    assert "achievements" in data
    assert all("name" in a and "level" in a for a in data["achievements"])

def test_leaderboard_includes_users():
    client.post("/achievements/v1/user_action/", json={
        "user_id": 1,
        "action_name": load_actions()[0]["name"]
    })
    r = client.get("/achievements/v1/get_leaderboard")
    assert r.status_code == 200
    assert "leaderboard" in r.json()
