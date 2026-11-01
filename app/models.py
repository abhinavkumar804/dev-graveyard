from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    tech_stack = Column(String(250), nullable=False)
    repo_url = Column(String(300), nullable=True)
    status = Column(String(50), default="Orphaned")
    adopter_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)