from sqlalchemy import (
    create_engine, Column, Integer, String, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import declarative_base

DB_NAME = "vkr.db"
Base = declarative_base()

class AchievementT(Base):
    __tablename__ = "achievement_t"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)

class Achievement(Base):
    __tablename__ = "achievement"
    id = Column(Integer, primary_key=True, autoincrement=True)
    achievement_t_id = Column(Integer, ForeignKey("achievement_t.id"), nullable=False)
    user_id = Column(Integer, nullable=False)
    score = Column(Integer, default=0, nullable=False)
    UniqueConstraint("achievement_t_id", "user_id", name="uix_user_achievement")

class Event(Base):
    __tablename__ = "event"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    achievement_affected_id = Column(Integer, ForeignKey("achievement_t.id"), nullable=False)
    reward_points = Column(Integer, default=0, nullable=False)

class UserEventTracker(Base):
    __tablename__ = "user_event_tracker"
    user_id = Column(Integer, primary_key=True, nullable=False)
    event_id = Column(Integer, ForeignKey("event.id"), primary_key=True, nullable=False)
    event_triggered_count = Column(Integer, default=0, nullable=False)

def create_db():
    engine = create_engine(f"sqlite:///{DB_NAME}")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
