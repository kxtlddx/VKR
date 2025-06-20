from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.create_db import DB_NAME, AchievementT

router = APIRouter(prefix="/achievements", tags=["Achievements"])
engine = create_engine(f"sqlite:///{DB_NAME}")
SessionLocal = sessionmaker(bind=engine)

class AchievementTypeIn(BaseModel):
    name: str

class AchievementTypeOut(BaseModel):
    id: int
    name: str

@router.post(
    "/", response_model=AchievementTypeOut, status_code=status.HTTP_201_CREATED
)
def create_achievement_type(payload: AchievementTypeIn):
    session = SessionLocal()
    exists = session.query(AchievementT).filter_by(name=payload.name).first()
    if exists:
        raise HTTPException(400, "Achievement type already exists")
    ach = AchievementT(name=payload.name)
    session.add(ach)
    session.commit()
    session.refresh(ach)
    return ach

@router.get("/", response_model=list[AchievementTypeOut])
def list_achievement_types():
    session = SessionLocal()
    return session.query(AchievementT).all()

@router.get("/{ach_id}", response_model=AchievementTypeOut)
def get_achievement_type(ach_id: int):
    session = SessionLocal()
    ach = session.query(AchievementT).get(ach_id)
    if not ach:
        raise HTTPException(404, "Not found")
    return ach

@router.put("/{ach_id}", response_model=AchievementTypeOut)
def update_achievement_type(ach_id: int, payload: AchievementTypeIn):
    session = SessionLocal()
    ach = session.query(AchievementT).get(ach_id)
    if not ach:
        raise HTTPException(404, "Not found")
    ach.name = payload.name
    session.commit()
    return ach

# @router.delete("/{ach_id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_achievement_type(ach_id: int):
#     session = SessionLocal()
#     ach = session.query(AchievementT).get(ach_id)
#     if not ach:
#         raise HTTPException(404, "Not found")
#     session.delete(ach)
#     session.commit()
#     return
