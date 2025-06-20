from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from create_db import AchievementT, DB_NAME, create_db
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ACHIEVEMENTS_FILE = BASE_DIR / "config" / "achievements_config.json"

confirm = input("Внимание! Все данные будут удалены и заменены. Продолжить? (y/n): ").strip().lower()
if confirm != 'y':
    print("Операция отменена.")
    exit()

create_db()

engine = create_engine(f"sqlite:///{DB_NAME}")
Session = sessionmaker(bind=engine)
session = Session()

# Capture current state before deletion
existing_achievements = session.query(AchievementT).all()
if existing_achievements:
    print("Удалены существующие записи AchievementT:")
    for ach in existing_achievements:
        print(f"  ID: {ach.id}, Name: {ach.name}")
else:
    print("В таблице AchievementT не было существующих записей.")

# Perform deletion
session.query(AchievementT).delete()

# Load new data
with open(ACHIEVEMENTS_FILE, "r", encoding="utf-8") as f:
    achievement_data = json.load(f)

# Insert new data
new_achievements = [AchievementT(id=a["id"], name=a["name"]) for a in achievement_data]
session.add_all(new_achievements)
session.commit()

print("Добавлены новые записи AchievementT:")
for ach in new_achievements:
    print(f"  ID: {ach.id}, Name: {ach.name}")

print("База данных успешно инициализирована.")
