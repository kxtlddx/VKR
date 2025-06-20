from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from create_db import AchievementT, DB_NAME
import json
from pathlib import Path

ACHIEVEMENTS_FILE = Path("config/achievements_config.json")

engine = create_engine(f"sqlite:///{DB_NAME}")
Session = sessionmaker(bind=engine)
session = Session()

with open(ACHIEVEMENTS_FILE, "r", encoding="utf-8") as f:
    desired_achievements = json.load(f)

desired_names = set(a["name"] for a in desired_achievements)
existing_achievements = session.query(AchievementT).all()
existing_names = set(a.name for a in existing_achievements)


to_delete = [a for a in existing_achievements if a.name not in desired_names]
for a in to_delete:
    session.delete(a)

to_add = desired_names - existing_names
session.add_all([AchievementT(name=name) for name in to_add])

session.commit()
print("AchievementT обновлён на основе achievements_config.json")
