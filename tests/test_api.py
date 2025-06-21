import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from database import create_db as db_mod
from database.create_db import DB_NAME

@pytest.fixture(autouse=True)
def reset_test_db(tmp_path, monkeypatch):
    # Установим путь к временной БД
    test_db = tmp_path / "test.db"
    monkeypatch.setattr(db_mod, "DB_NAME", str(test_db))
    from database.create_db import create_db
    create_db()

    # Перезагружаем main, чтобы он использовал новую БД
    import importlib
    import main
    importlib.reload(main)

    yield

@pytest.fixture
def client():
    import main
    return TestClient(main.app)

def test_trigger_event_and_leaderboard(client):
    # 1. Добавляем achievement type
    ach_name = "KillGoblin"
    ach_resp = client.post("/api/v1/achievements/", json={"name": ach_name})
    assert ach_resp.status_code == 201
    ach_id = ach_resp.json()["id"]

    # 2. Добавляем event, который ссылается на achievement
    event_data = {
        "name": "GoblinSlain",
        "achievement_affected_id": ach_id,
        "reward_points": 150
    }
    ev_resp = client.post("/api/v1/events/", json=event_data)
    assert ev_resp.status_code == 201
    ev_id = ev_resp.json()["id"]

    # 3. Тригерим событие
    trig_resp = client.post("/api/v1/events/trigger", json={
        "user_id": 42,
        "event_id": ev_id
    })
    assert trig_resp.status_code == 200
    data = trig_resp.json()["achievement"]
    assert data["name"] == ach_name
    assert data["score"] == 150
    assert data["level"] == 1

    # 4. Получаем user achievements
    ua = client.get("/api/v1/leaderboard/user/42")
    assert ua.status_code == 200
    achievements = ua.json()["achievements"]
    assert len(achievements) == 1
    assert achievements[0]["name"] == ach_name

    # 5. Проверка leaderboard
    lb = client.get("/api/v1/leaderboard/")
    assert lb.status_code == 200
    board = lb.json()["leaderboard"]
    assert any(user["user_id"] == 42 for user in board)
