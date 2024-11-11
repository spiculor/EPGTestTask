from fastapi import FastAPI, Depends, UploadFile, File, HTTPException,Form
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas.schemas import ParticipantCreate, ParticipantResponse,MatchResponse  # Импортируем из app.schemas
from app.crud import crud
from app.database.database import get_db, init_db
from app.utils.watermark import add_watermark
import os
from geopy.distance import geodesic
from app.utils.redis_client import redis_client
import json 
app = FastAPI()


@app.on_event("startup")
def on_startup():
    init_db()


@app.post("/api/clients/create", response_model=ParticipantResponse)
async def create_participant(
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    gender: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    password: str = Form(...),
    avatar: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        os.makedirs("uploads", exist_ok=True)

        image_data = await avatar.read()
        output_path = f"uploads/{email}_avatar.jpg"
        watermark_path = os.path.abspath("static/watermark.png")
        await add_watermark(image_data, watermark_path, output_path)

        participant_data = ParticipantCreate(
            first_name=first_name,
            last_name=last_name,
            email=email,
            gender=gender,
            latitude=latitude,
            longitude=longitude,
            password=password
        )

        db_participant = crud.create_participant(db, participant_data, avatar_path=output_path)
        return db_participant

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@app.post("/api/clients/{id}/match", response_model=MatchResponse)
def match_participant(id: int, db: Session = Depends(get_db)):
    current_user = crud.get_participant(db, id=id)
    if not current_user:
        raise HTTPException(status_code=404, detail="Participant not found")
    
    try:
        crud.check_and_update_match_limit(db, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    matches = crud.find_mutual_matches(db, current_user)
    if matches:
        matched_user = matches[0]
        return MatchResponse(
            message=f"You matched with {matched_user.first_name}!",
            email=matched_user.email
        )

    return MatchResponse(message="No match found")


@app.get("/api/list", response_model=List[ParticipantResponse])
def list_participants(
    gender: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    sort_by: Optional[str] = None,
    max_distance: Optional[float] = None,
    user_latitude: Optional[float] = None,
    user_longitude: Optional[float] = None,
    db: Session = Depends(get_db)
):
    participants = crud.get_participants(db, gender, first_name, last_name, sort_by)

    if max_distance and user_latitude is not None and user_longitude is not None:
        filtered_participants = []
        user_location = (user_latitude, user_longitude)
        for participant in participants:
            participant_location = (participant.latitude, participant.longitude)
            distance = geodesic(user_location, participant_location).km
            if distance <= max_distance:
                filtered_participants.append(participant)
        participants = filtered_participants

    participants_dict = [
        {**ParticipantResponse.from_orm(p).dict(), "created_at": p.created_at.isoformat()}
        for p in participants
    ]
    cache_key = f"participants_{gender}_{first_name}_{last_name}_{sort_by}_{max_distance}_{user_latitude}_{user_longitude}"
    redis_client.setex(cache_key, 3600, json.dumps(participants_dict))

    return participants