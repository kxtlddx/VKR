import json
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from create_db import (
    create_db, DB_NAME, AchievementT, Event
)

BASE_DIR = Path(__file__).resolve().parent.parent
ACHIEVEMENTS_FILE = BASE_DIR / "config" / "achievements_config.json"
EVENTS_FILE       = BASE_DIR / "config" / "events_config.json"

confirm = input(
    "Внимание! Все данные в БД будут удалены и заменены. Продолжить? (y/n): "
).strip().lower()
if confirm != "y":
    print("Операция отменена.")
    exit()

# reset schema
create_db()
engine = create_engine(f"sqlite:///{DB_NAME}")
Session = sessionmaker(bind=engine)
session = Session()

# -- achievements
with open(ACHIEVEMENTS_FILE, encoding="utf-8") as f:
    ach_data = json.load(f)

session.query(AchievementT).delete()
new_ach = [AchievementT(id=a["id"], name=a["name"]) for a in ach_data]
session.add_all(new_ach)
print(f"Inserted {len(new_ach)} achievements.")

# -- events
with open(EVENTS_FILE, encoding="utf-8") as f:
    ev_data = json.load(f)

session.query(Event).delete()
new_ev = [
    Event(
        id=e["id"],
        name=e["name"],
        achievement_affected_id=e["achievement_affected_id"],
        reward_points=e["reward_points"],
    )
    for e in ev_data
]
session.add_all(new_ev)
print(f"Inserted {len(new_ev)} events.")

session.commit()
print("DB init completed.")
