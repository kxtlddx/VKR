from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.create_db import DB_NAME, Achievement, AchievementT
import json
from pathlib import Path

from logic import (
    transform_achievements_for_leaderboard,
    get_achievement_level,
    get_level_score_curr,
    get_level_score_full
)

app = FastAPI(
    title="Achievement Microservice",
    docs_url="/swagger"  # Now Swagger UI will be at /swagger
)


engine = create_engine(f"sqlite:///{DB_NAME}")
Session = sessionmaker(bind=engine)
ACTIONS_FILE = Path("config/actions_config.json")

def load_actions():
    with open(ACTIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def get_action_by_name(name: str):
    for action in load_actions():
        if action["name"] == name:
            return action
    return None

def get_achievement_t_by_action(action):
    """
    Сопоставляет имя действия с именем типа достижения и выполняет запрос один раз.
    """
    achievement_name = action["achievement_affected"]

    session = Session()
    return session.query(AchievementT).filter_by(name=achievement_name).first()



class ActionInput(BaseModel):
    user_id: int
    action_name: str  # заменили с action_id на имя действия

@app.post("/achievements/v1/user_action/")
def user_action(data: ActionInput):
    session = Session()

    action = get_action_by_name(data.action_name)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
 
    ach_t = get_achievement_t_by_action(action)
    if not ach_t:
        raise HTTPException(status_code=404, detail="Achievement type not found for this action {action["name"]}")

    achievement = session.query(Achievement).filter(
        Achievement.user_id == data.user_id,
        Achievement.achievement_t_id == ach_t.id
    ).first()

    if achievement:
        achievement.score += action["reward_points"]
    else:
        new_achievement = Achievement(
            user_id=data.user_id,
            achievement_t_id=ach_t.id,
            score=action["reward_points"]
        )
        session.add(new_achievement)

    session.commit()
    return {"status": "success"}


@app.get("/achievements/v1/get_leaderboard")
def get_leaderboard():
    session = Session()
    all_achievements = session.query(Achievement).all()

    leaderboard = transform_achievements_for_leaderboard(all_achievements)
    leaderboard.sort(key=lambda x: x["total_score"], reverse=True)

    return {"leaderboard": leaderboard}

@app.get("/achievements/v1/get_user_achievements/{user_id}")
def get_user_achievements(user_id: int):
    session = Session()
    achievements = session.query(Achievement).filter_by(user_id=user_id).all()
    
    result = []
    for ach in achievements:
        ach_t = session.query(AchievementT).filter_by(id=ach.achievement_t_id).first()
        if not ach_t:
            continue  # пропускаем, если тип достижения не найден

        level = get_achievement_level(ach.id, ach.score)
        result.append({
            "achievement_id": ach.id,
            "name": ach_t.name,
            "score": ach.score,
            "level": level,
            "level_score": get_level_score_curr(ach.id, level, ach.score),
            "level_score_full": get_level_score_full(ach.id, level, ach.score),
        })

    return {"achievements": result}

@app.get("/achievements/v1/get_all_achievements")
def get_all_achievements():
    session = Session()
    achievements = session.query(AchievementT).all()

    return {
        "achievements": [
            {"id": ach.id, "name": ach.name} for ach in achievements
        ]
    }

@app.get("/achievements/v1/get_all_actions")
def get_all_actions():
    try:
        with open(ACTIONS_FILE, "r", encoding="utf-8") as f:
            actions = json.load(f)
        return actions
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="actions_config.json not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="actions_config.json is invalid")
