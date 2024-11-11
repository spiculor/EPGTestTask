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


def get_participant(db: Session, id: int):
    return db.query(models.Participant).filter(models.Participant.id == id).first()


def find_mutual_matches(db: Session, current_user):
    matches = db.query(models.Participant).filter(models.Participant.email != current_user.email).all()
    return matches


def get_participants(
    db: Session,
    gender: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    sort_by: Optional[str] = None
) -> List[models.Participant]:
    query = db.query(models.Participant)
    
    if gender:
        query = query.filter(models.Participant.gender == gender)
    if first_name:
        query = query.filter(models.Participant.first_name == first_name)
    if last_name:
        query = query.filter(models.Participant.last_name == last_name)
    if sort_by == "date":
        query = query.order_by(models.Participant.created_at.desc())
    
    return query.all()


def check_and_update_match_limit(db: Session, participant: Participant, limit: int = 5):
    now = datetime.utcnow()
    if participant.last_match_date.date() != now.date():
        participant.daily_match_count = 1
        participant.last_match_date = now
    elif participant.daily_match_count >= limit:
        raise ValueError("Daily match limit reached")
    else:
        participant.daily_match_count += 1
    db.commit()
    db.refresh(participant)