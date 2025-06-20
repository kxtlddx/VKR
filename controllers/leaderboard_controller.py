from fastapi import APIRouter
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.create_db import DB_NAME, Achievement, AchievementT, UserEventTracker, Event
from logic import (
    transform_achievements_for_leaderboard,
    get_achievement_level,
    get_level_score_curr,
    get_level_score_full
)

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])
engine = create_engine(f"sqlite:///{DB_NAME}")
SessionLocal = sessionmaker(bind=engine)

@router.get("/")
def get_leaderboard():
    session = SessionLocal()
    all_ach = session.query(Achievement).all()
    board = transform_achievements_for_leaderboard(all_ach)
    board.sort(key=lambda x: x["total_score"], reverse=True)
    return {"leaderboard": board}

@router.get("/user/{user_id}")
def get_user_achievements(user_id: int):
    session = SessionLocal()
    achs = session.query(Achievement).filter_by(user_id=user_id).all()
    result = []
    for a in achs:
        meta = session.query(AchievementT).get(a.achievement_t_id)
        lvl = get_achievement_level(a.id, a.score)
        result.append({
            "achievement_id": a.id,
            "name": meta.name,
            "score": a.score,
            "level": lvl,
            "level_score": get_level_score_curr(a.id, lvl, a.score),
            "level_score_full": get_level_score_full(a.id, lvl, a.score),
        })
    return {"achievements": result}
