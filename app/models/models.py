from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.database.database import Base  

class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    gender = Column(String)
    avatar = Column(String)  
    latitude = Column(Float)
    longitude = Column(Float)
    password = Column(String)  
    created_at = Column(DateTime, default=datetime.utcnow)
    daily_match_count = Column(Integer, default=0)
    last_match_date = Column(DateTime, default=datetime.utcnow) 