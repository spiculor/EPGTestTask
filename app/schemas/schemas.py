from pydantic import BaseModel

class ParticipantCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    gender: str
    latitude: float
    longitude: float
    password: str  

from datetime import datetime

class ParticipantResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    gender: str
    latitude: float
    longitude: float
    created_at: datetime 

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MatchResponse(BaseModel):
    message: str
    email: str