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