from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas import schemas
from app.models import models
from passlib.hash import bcrypt
from datetime import datetime
from passlib.context import CryptContext
from app.models.models import Participant

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_participant(db: Session, participant: schemas.ParticipantCreate, avatar_path: str) -> schemas.ParticipantResponse:

    existing_participant = db.query(models.Participant).filter(models.Participant.email == participant.email).first()
    if existing_participant:
        raise ValueError("Participant with this email already exists.")

    hashed_password = pwd_context.hash(participant.password)
    
    db_participant = models.Participant(
        first_name=participant.first_name,
        last_name=participant.last_name,
        email=participant.email,
        gender=participant.gender,
        avatar=avatar_path,
        latitude=participant.latitude,
        longitude=participant.longitude,
        password=hashed_password,
        created_at=datetime.utcnow()  
    )
    db.add(db_participant)
    db.commit()
    db.refresh(db_participant)
    
    participant_data = {
        "id": db_participant.id,
        "first_name": db_participant.first_name,
        "last_name": db_participant.last_name,
        "email": db_participant.email,
        "gender": db_participant.gender,
        "latitude": db_participant.latitude,
        "longitude": db_participant.longitude,
        "created_at": db_participant.created_at.isoformat()  # Преобразуем дату в строку
    }
    
    return schemas.ParticipantResponse(**participant_data)