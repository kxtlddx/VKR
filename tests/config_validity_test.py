import json
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.create_db import DB_NAME, AchievementT

def test_all_achievement_affected_exist():
    # Загрузка всех доступных типов достижений из БД
    engine = create_engine(f"sqlite:///{DB_NAME}")
    Session = sessionmaker(bind=engine)
    session = Session()
    existing_ids = {row.id for row in session.query(AchievementT).all()}

    # Загрузка всех событий из config/events_config.json
    events_file = Path("config") / "events_config.json"
    with events_file.open(encoding="utf-8") as f:
        events = json.load(f)

    # Проверяем, что каждое событие ссылается на существующее достижение
    for ev in events:
        achievement_id = ev.get("achievement_affected_id")
        assert achievement_id in existing_ids, (
            f"'{achievement_id}' из events_config.json не найден в AchievementT"
        )
