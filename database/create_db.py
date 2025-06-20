from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base

DB_NAME = "vkr.db"
Base = declarative_base()

class AchievementT(Base):
    __tablename__ = "achievement_t"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

class Achievement(Base):
    __tablename__ = "achievement"
    id = Column(Integer, primary_key=True)
    achievement_t_id = Column(Integer, ForeignKey("achievement_t.id"))
    user_id = Column(Integer)  # foreign key to external employee DB
    score = Column(Integer)

def create_db():
    engine = create_engine(f"sqlite:///{DB_NAME}")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
