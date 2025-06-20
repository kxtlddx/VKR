from main import load_actions
from database.create_db import DB_NAME, AchievementT
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def test_all_achievement_affected_exist():
    engine = create_engine(f"sqlite:///{DB_NAME}")
    Session = sessionmaker(bind=engine)
    session = Session()

    action_data = load_actions()
    existing_names = set(row.name for row in session.query(AchievementT).all())

    for action in action_data:
        assert action["achievement_affected"] in existing_names, \
            f"{action['achievement_affected']} is not present in AchievementT"
