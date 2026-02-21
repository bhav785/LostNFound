from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from database import Base


class LostItem(Base):
    __tablename__ = "lost_items"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    image_path = Column(String)
    email = Column(String)
    created_at = Column(String)
    matched = Column(Integer, default=0) # 0 = false, 1 = true


class FoundItem(Base):
    __tablename__ = "found_items"

    id = Column(Integer, primary_key=True, index=True)
    caption = Column(String)
    image_path = Column(String)
    location = Column(String)
    condition = Column(String)
    created_at = Column(String)
    matched = Column(Integer, default=0)

class Match(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True, index=True)
    lost_item_id = Column(Integer)
    found_item_id = Column(Integer)
    similarity_score = Column(Integer)
    created_at = Column(String)
    verified = Column(Integer, default=0)

class DetectiveRequest(BaseModel):
    history: list
    userInput: str


class FinalizeRequest(BaseModel):
    history: list
