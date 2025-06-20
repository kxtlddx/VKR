import json
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from create_db import DB_NAME, AchievementT, Event

BASE_DIR = Path(__file__).resolve().parent.parent
ACHIEVEMENTS_FILE = BASE_DIR / "config" / "achievements_config.json"
EVENTS_FILE       = BASE_DIR / "config" / "events_config.json"

engine  = create_engine(f"sqlite:///{DB_NAME}")
Session = sessionmaker(bind=engine)
session = Session()

# load configs
with open(ACHIEVEMENTS_FILE, encoding="utf-8") as f:
    desired_ach = json.load(f)
with open(EVENTS_FILE, encoding="utf-8") as f:
    desired_ev  = json.load(f)

# prepare maps and sets
ach_names         = {a["name"] for a in desired_ach}
existing_ach_objs = session.query(AchievementT).all()

ev_map            = {e["name"]: e for e in desired_ev}
existing_ev_objs  = {e.name: e for e in session.query(Event).all()}

# track changes
removed_ach = []
added_ach   = []

removed_ev  = []
added_ev    = []
updated_ev  = []

# 1) sync achievements: delete missing, add new
for ach in existing_ach_objs:
    if ach.name not in ach_names:
        removed_ach.append(ach.name)
        session.delete(ach)

to_add_ach = ach_names - {a.name for a in existing_ach_objs}
for name in to_add_ach:
    added_ach.append(name)
    session.add(AchievementT(name=name))

# 2) sync events: delete missing
for name, ev in list(existing_ev_objs.items()):
    if name not in ev_map:
        removed_ev.append(name)
        session.delete(ev)
        existing_ev_objs.pop(name)

# add or update events
for name, cfg in ev_map.items():
    if name in existing_ev_objs:
        ev = existing_ev_objs[name]
        changed = False
        if ev.achievement_affected_id != cfg["achievement_affected_id"]:
            ev.achievement_affected_id = cfg["achievement_affected_id"]
            changed = True
        if ev.reward_points != cfg["reward_points"]:
            ev.reward_points = cfg["reward_points"]
            changed = True
        if changed:
            updated_ev.append(name)
    else:
        added_ev.append(name)
        session.add(Event(
            name=cfg["name"],
            achievement_affected_id=cfg["achievement_affected_id"],
            reward_points=cfg["reward_points"],
        ))

# commit and report
session.commit()

print("=== Achievements sync ===")
print(f"  Added:   {added_ach or []}")
print(f"  Removed: {removed_ach or []}")

print("\n=== Events sync ===")
print(f"  Added:   {added_ev or []}")
print(f"  Removed: {removed_ev or []}")
print(f"  Updated: {updated_ev or []}")
