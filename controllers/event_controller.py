from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.create_db import DB_NAME, Event, UserEventTracker, Achievement, AchievementT

from logic import (
    get_achievement_level,
    get_level_score_curr,
    get_level_score_full
)

router = APIRouter(prefix="/events", tags=["Events"])
engine = create_engine(f"sqlite:///{DB_NAME}")
SessionLocal = sessionmaker(bind=engine)

class EventIn(BaseModel):
    name: str
    achievement_affected_id: int
    reward_points: int

class EventOut(EventIn):
    id: int

class EventTriggerIn(BaseModel):
    user_id: int
    event_id: int

@router.post("/trigger", status_code=status.HTTP_200_OK)
def trigger_event(payload: EventTriggerIn):
    session = SessionLocal()
    # 1) fetch event
    ev = session.query(Event).get(payload.event_id)
    if not ev:
        raise HTTPException(404, "Event not found")

    # 2) fetch or create achievement
    ach = session.query(Achievement).filter_by(
        user_id=payload.user_id,
        achievement_t_id=ev.achievement_affected_id
    ).first()

    if ach:
        ach.score += ev.reward_points
    else:
        ach = Achievement(
            user_id=payload.user_id,
            achievement_t_id=ev.achievement_affected_id,
            score=ev.reward_points
        )
        session.add(ach)

    # 3) fetch or create tracker
    tracker = session.query(UserEventTracker).filter_by(
        user_id=payload.user_id,
        event_id=payload.event_id
    ).first()

    if tracker:
        tracker.event_triggered_count += 1
    else:
        tracker = UserEventTracker(
            user_id=payload.user_id,
            event_id=payload.event_id,
            event_triggered_count=1
        )
        session.add(tracker)

    session.commit()
    session.refresh(ach)

    # 4) build response exactly like “get user achievements” for this one
    meta = session.query(AchievementT).get(ach.achievement_t_id)
    level = get_achievement_level(ach.id, ach.score)
    return {
        "achievement": {
            "achievement_id": ach.id,
            "name": meta.name,
            "score": ach.score,
            "level": level,
            "level_score": get_level_score_curr(ach.id, level, ach.score),
            "level_score_full": get_level_score_full(ach.id, level, ach.score),
        }
    }


@router.get("/{event_id}/tracker/{user_id}")
def get_event_tracker(event_id: int, user_id: int):
    session = SessionLocal()
    ev = session.query(Event).get(event_id)
    if not ev:
        raise HTTPException(404, "Event not found")

    tracker = session.query(UserEventTracker).filter_by(
        user_id=user_id,
        event_id=event_id
    ).first()

    if not tracker:
        return {"count": 0, "total_points": 0}

    total = tracker.event_triggered_count * ev.reward_points
    return {
        "count": tracker.event_triggered_count,
        "total_points": total
    }

@router.post("/", response_model=EventOut, status_code=status.HTTP_201_CREATED)
def create_event(payload: EventIn):
    session = SessionLocal()
    if session.query(Event).filter_by(name=payload.name).first():
        raise HTTPException(400, "Event already exists")
    ev = Event(**payload.dict())
    session.add(ev)
    session.commit()
    session.refresh(ev)
    return ev

@router.get("/", response_model=list[EventOut])
def list_events():
    session = SessionLocal()
    return session.query(Event).all()

@router.get("/{event_id}", response_model=EventOut)
def get_event(event_id: int):
    session = SessionLocal()
    ev = session.query(Event).get(event_id)
    if not ev:
        raise HTTPException(404, "Not found")
    return ev

@router.put("/{event_id}", response_model=EventOut)
def update_event(event_id: int, payload: EventIn):
    session = SessionLocal()
    ev = session.query(Event).get(event_id)
    if not ev:
        raise HTTPException(404, "Not found")
    for k, v in payload.dict().items():
        setattr(ev, k, v)
    session.commit()
    return ev

# @router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_event(event_id: int):
#     session = SessionLocal()
#     ev = session.query(Event).get(event_id)
#     if not ev:
#         raise HTTPException(404, "Not found")
#     session.delete(ev)
#     session.commit()
#     return
