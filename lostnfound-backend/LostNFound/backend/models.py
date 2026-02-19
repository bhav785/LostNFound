from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from database import Base


class LostItem(Base):
    __tablename__ = "lost_items"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    image_path = Column(String)


class FoundItem(Base):
    __tablename__ = "found_items"

    id = Column(Integer, primary_key=True, index=True)
    caption = Column(String)
    image_path = Column(String)

class DetectiveRequest(BaseModel):
    history: list
    userInput: str


class FinalizeRequest(BaseModel):
    history: list
